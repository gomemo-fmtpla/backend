# app/route/notes.py
import json
import os
import time
import traceback
import uuid

from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.commons.pydantic_to_json import metadata_to_dict
from app.database.db import get_db
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteUpdate
from app.usecases.auth_guard import auth_guard
from app.usecases.generation.chat_generation import generate_chat
from app.usecases.note.note import (
    add_metadata,
    add_note,
    get_folder_by_note_id_usecase, 
    update_note,
    get_note_by_id,  
    get_all_notes,
    move_note_to_folder_usecase,
    remove_note_folder_usecase,
)
from app.usecases.generation.youtube_transcript_extraction import generate_transcript, generate_youtube_transcript
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio, transcribe_audio_salad, transcribe_audio_whisper_openai
from app.usecases.generation.summary_generation import generate_summary
from app.usecases.generation.summary_translation_generation import translate_summary
from app.usecases.generation.flashcard_generation import generate_flashcards
from app.usecases.generation.quiz_generation import generate_quizzes
from app.database.models import NoteMetadata, User, Note

from app.usecases.storage.audio_store import delete_object, extract_audio_filename, put_object

from redis import Redis
from app.config import settings


# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL)

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

@router.get("/")
async def get_notes(current_user: User = Depends(auth_guard), 
                    db: Session = Depends(get_db)):
    return get_all_notes(db, user_id=current_user.id)

@router.get("/{note_id}")
async def get_note(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    note = get_note_by_id(db, note_id=note_id, user_id=current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.get("/generate/youtube/")
async def generate_youtube_summary(
    youtube_url: str,
    lang: str = "",
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        try:
            print(f"Starting transcription for URL: {youtube_url}")
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating transcript...'})}\n\n"

            # Add timing information
            start_time = time.time()
            transcript_response = generate_transcript(youtube_url)
            transcription_time = time.time() - start_time
            print(f"Transcription took {transcription_time:.2f} seconds")
            print(f"Transcript response: {transcript_response}")
            
            if not transcript_response['success']:
                error_details = transcript_response.get('error', {})
                print(f"Transcription failed with error: {error_details}")
                yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to transcribe the YouTube video: {error_details}'})}\n\n"
                return
            
            transcript = transcript_response['data']['transcript']
            print(f"Transcript length: {len(transcript)} characters")

            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"

            start_time = time.time()
            summary_response = generate_summary(transcript, lang)
            summary_time = time.time() - start_time
            print(f"Summary generation took {summary_time:.2f} seconds")
            
            if not summary_response['success']:
                error_details = summary_response.get('error', {})
                print(f"Summary generation failed with error: {error_details}")
                yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to generate summary: {error_details}'})}\n\n"
                return

            summary_data = summary_response['data']
            print("Summary generated successfully")

            yield f"data: {json.dumps({'status': 'progress', 'message': 'Creating note...'})}\n\n"

            try:
                note_create = NoteCreate(
                    title=summary_data['title'],
                    summary=summary_data['markdown'],
                    transcript_text=transcript,
                    language=summary_data['lang'],
                    content_url=youtube_url,
                )
                
                new_note = add_note(
                    db=db,
                    user_id=current_user.id,
                    folder_id=None,
                    note_create=note_create
                )
                print(f"Note created successfully with ID: {new_note.id}")

                metadata_create = NoteMetadataCreate(
                    title=summary_data['title'],
                    content_category=summary_data['content_category'],
                    emoji_representation=summary_data['emoji_representation'],
                    date_created=datetime.now()
                )

                note_metadata = add_metadata(
                    db=db,
                    user_id=current_user.id,
                    note_id=new_note.id,
                    metadata_create=metadata_create
                )
                print("Metadata added successfully")

                note_metadata_json = json.dumps(metadata_to_dict(note_metadata))
                yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

            except Exception as db_error:
                print(f"Database operation failed: {str(db_error)}")
                raise

        except Exception as e:
            print(f"Process failed with error: {str(e)}")
            print(f"Full error traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed on generate_youtube_summary: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/generate/youtube/2/")
async def generate_youtube_summary_2(
    youtube_url: str,
    transcript: str,
    lang: str = "",
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        try:
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Transcribing audio...'})}\n\n"
            
            transcription_response = generate_youtube_transcript(youtube_url=youtube_url)
            if not transcription_response['success']:
                print(transcription_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"
            
            transcript = transcription_response["data"]["transcript"]
        
            summary_response = generate_summary(transcript, lang)
            if not summary_response['success']:
                print(summary_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to generate summary'})}\n\n"
                return

            summary_data = summary_response['data']

            yield f"data: {json.dumps({'status': 'progress', 'message': 'Creating note...'})}\n\n"

            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=transcript,
                language=summary_data['lang'],
                content_url=youtube_url,
            )
            new_note = add_note(
                db=db,
                user_id=current_user.id,
                folder_id=None,  # Or specify a folder_id if needed
                note_create=note_create
            )

            metadata_create = NoteMetadataCreate(
                title=summary_data['title'],
                content_category=summary_data['content_category'],
                emoji_representation=summary_data['emoji_representation'],
                date_created=datetime.now()
            )

            note_metadata = add_metadata(
                db=db,
                user_id=current_user.id,
                note_id=new_note.id,
                metadata_create=metadata_create
            )

            note_metadata_json = json.dumps(metadata_to_dict(note_metadata))

            yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed on generate_youtube_summary_2: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/audio/store")
async def store_audio(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(auth_guard),
):
    audio_path = f"/tmp/{audio_file.filename}"
    try:
        # Save the uploaded file to a temporary location
        with open(audio_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        object_url = put_object(audio_file, audio_path)
        
        # Return the URL or any other necessary responseZ
        print("object_url: ", object_url)
        return {"success": True, "url": object_url}
    
    except Exception as e:
        if 'object_url' in locals():
            delete_object(object_url)
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
@router.get("/generate/audio")
async def generate_audio_summary(
    audio_url: str,
    lang: str = "",
    context: str = "",  
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        task_id = None
        try:
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            redis_client.set(f"task_status:{task_id}", "QUEUED")
            
            yield f"data: {json.dumps({'status': 'queued', 'task_id': task_id})}\n\n"
            
            # Process transcription
            transcription_response = transcribe_audio(audio_url=audio_url)
            if not transcription_response['success']:
                raise Exception(transcription_response['error'])
            
            redis_client.set(f"task_status:{task_id}", "TRANSCRIBING")
            yield f"data: {json.dumps({'status': 'transcribing'})}\n\n"
            
            transcript = transcription_response["data"]["transcript"]
            
            # Generate summary
            redis_client.set(f"task_status:{task_id}", "SUMMARIZING")
            yield f"data: {json.dumps({'status': 'summarizing'})}\n\n"
            
            summary_response = generate_summary(transcript, lang, context=context)
            if not summary_response['success']:
                raise Exception(summary_response['error'])
            
            summary_data = summary_response['data']
            
            # Create note
            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=transcript,
                language=summary_data['lang'],
                content_url=audio_url,
            )
            
            new_note = add_note(db=db, user_id=current_user.id, 
                              folder_id=None, note_create=note_create)
            
            redis_client.set(f"task_status:{task_id}", "COMPLETE")
            yield f"data: {json.dumps({'status': 'complete', 'note_id': new_note.id})}\n\n"

        except Exception as e:
            if task_id:
                redis_client.set(f"task_status:{task_id}", "FAILED")
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
        finally:
            if task_id:
                # Cleanup task status after 1 hour
                redis_client.expire(f"task_status:{task_id}", 3600)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/generate/audio/2/")
async def generate_audio_summary_2(
    audio_url: str,
    lang: str = "",
    context: str = "",  
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        try:
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Transcribing audio...'})}\n\n"
            
            transcription_response = transcribe_audio_whisper_openai(audio_url=audio_url)
            if not transcription_response['success']:
                print(transcription_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n"
                return
            
            print("transcription_response: ", transcription_response)
            
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"
            
            transcript = transcription_response["data"]["transcript"]
            
            summary_response = generate_summary(transcript, lang, context=context)
            if not summary_response['success']:
                print(summary_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to generate summary'})}\n\n"
                return
            
            summary_data = summary_response['data']

            # Step 3: Create a new note
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Creating note...'})}\n\n"
            
            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=transcript,
                language=summary_data['lang'],
                content_url=audio_url,
            )
            new_note = add_note(
                db=db,
                user_id=current_user.id,
                folder_id=None,
                note_create=note_create
            )

            metadata_create = NoteMetadataCreate(
                title=summary_data['title'],
                content_category=summary_data['content_category'],
                emoji_representation=summary_data['emoji_representation'],
                date_created=datetime.now()
            )
            note_metadata = add_metadata(
                db=db,
                user_id=current_user.id,
                note_id=new_note.id,
                metadata_create=metadata_create
            )

            # Convert metadata to JSON
            note_metadata_json = json.dumps(metadata_to_dict(note_metadata))

            # Final status with the note metadata JSON
            yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed on generate_audio_summary_2: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/generate/audio/3/")
async def generate_audio_summary_3(
    audio_url: str,
    lang: str = "",
    context: str = "",  
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        temp_audio_file = None  # Initialize temp_audio_file to None
        try:
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Transcribing audio...'})}\n\n"
            
            transcription_response = transcribe_audio_salad(audio_url=audio_url)
            if not transcription_response['success']:
                print(transcription_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n"
                return
            
            # print("transcription_response: ", transcription_response)
            
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"
            
            transcript = transcription_response["data"]["transcript"]
            
            summary_response = generate_summary(transcript, lang, context=context)
            if not summary_response['success']:
                print(summary_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to generate summary'})}\n\n"
                return
            
            summary_data = summary_response['data']

            # Step 3: Create a new note
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Creating note...'})}\n\n"
            
            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=transcript,
                language=summary_data['lang'],
                content_url=audio_url,
            )
            new_note = add_note(
                db=db,
                user_id=current_user.id,
                folder_id=None,
                note_create=note_create
            )

            metadata_create = NoteMetadataCreate(
                title=summary_data['title'],
                content_category=summary_data['content_category'],
                emoji_representation=summary_data['emoji_representation'],
                date_created=datetime.now()
            )
            note_metadata = add_metadata(
                db=db,
                user_id=current_user.id,
                note_id=new_note.id,
                metadata_create=metadata_create
            )

            # Convert metadata to JSON
            note_metadata_json = json.dumps(metadata_to_dict(note_metadata))

            # Final status with the note metadata JSON
            yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed on generate_audio_summary_3: {str(e)}'})}\n\n"
            if temp_audio_file and os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/generate/context/")
async def generate_context_note(
    context: str,
    lang: str = "",
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        try:
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Générer un résumé...'})}\n\n"
            
            summary_response = generate_summary(context, lang, context=context)
            if not summary_response['success']:
                print(summary_response["error"])
                yield f"data: {json.dumps({'status': 'error', 'message': f'Échec de la génération du résumé'})}\n\n"
                return
            
            summary_data = summary_response['data']

            yield f"data: {json.dumps({'status': 'progress', 'message': 'Créer une note...'})}\n\n"
            
            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=context,
                language=summary_data['lang'],
                content_url="",
            )
            new_note = add_note(
                db=db,
                user_id=current_user.id,
                folder_id=None,
                note_create=note_create
            )
            metadata_create = NoteMetadataCreate(
                title=summary_data['title'],
                content_category=summary_data['content_category'],
                emoji_representation=summary_data['emoji_representation'],
                date_created=datetime.now()
            )
            note_metadata = add_metadata(
                db=db,
                user_id=current_user.id,
                note_id=new_note.id,
                metadata_create=metadata_create
            )
            
            note_metadata_json = json.dumps(metadata_to_dict(note_metadata))

            yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': 'Échec du processus'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.put("/{note_id}")
async def update_existing_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    updated_note = update_note(db, note_id=note_id, note_update=note_update, user_id=current_user.id)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, current_user.id == Note.user_id).first()
    note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note_id, NoteMetadata.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.content_url:
        file_name = extract_audio_filename(note.content_url)
        print("File name extracted: ", file_name)
        if file_name:
            delete_object(file_name=file_name)

    db.delete(note_metadata)
    db.delete(note)
    db.commit()

    return {"detail": f'Note with id {note_id} deleted'}

@router.get("/translate/{note_id}")
async def translate_note_endpoint(
    note_id: int,
    target_language: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    async def event_generator():
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if not note:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to get note'})}\n\n"
                return
            
            note.translated = True

            # Step 2: Translate the note's transcript
            translation = translate_summary(note.transcript_text, target_language)
            if not translation['success']:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to translate summary'})}\n\n"
                return
            
            translated_text = translation['data']['translated_text']

            # Step 3: Generate summary
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating translated summary...'})}\n\n"
            
            # new_public_url = copy_file_from_url(public_url=note.content_url)
            summary_response = generate_summary(translated_text, target_language)
            if not summary_response['success']:
                yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to generate summary'})}\n\n"
                return
            
            summary_data = summary_response['data']

            # Step 4: Create a new note
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Creating note...'})}\n\n"
            
            note_create = NoteCreate(
                title=summary_data['title'],
                summary=summary_data['markdown'],
                transcript_text=translated_text,
                language=summary_data['lang'],
                content_url=note.content_url,
                translated=True,
            )
            new_note = add_note(
                db=db,
                user_id=current_user.id,
                folder_id=None,
                note_create=note_create
            )

            metadata_create = NoteMetadataCreate(
                title=summary_data['title'],
                content_category=summary_data['content_category'],
                emoji_representation=summary_data['emoji_representation'],
                date_created=datetime.now()
            )
            note_metadata = add_metadata(
                db=db,
                user_id=current_user.id,
                note_id=new_note.id,
                metadata_create=metadata_create
            )

            # Convert metadata to JSON
            note_metadata_json = json.dumps(metadata_to_dict(note_metadata))

            # Final yield: status "complete" with note_metadata_json as the message
            yield f"data: {json.dumps({'status': 'complete', 'message': note_metadata_json})}\n\n"

            db.commit()
            db.refresh(note)

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed on translate_note_endpoint: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/flashcard/{note_id}")
async def create_flashcards(
    note_id: int,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.flashcards :
        note.flashcards.clear()

    flashcard_data = generate_flashcards(note.summary, note.language)
    if not flashcard_data['success'] :
       print(flashcard_data['error'])
       raise HTTPException(status_code=500, detail="Server fail")
     
    note.flashcards = flashcard_data['data']['flashcards']
    db.commit()
    db.refresh(note)
    return note.flashcards

@router.get("/quizzes/{note_id}")
async def create_quizzes(
    note_id: int,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.quizzes :
        note.quizzes.clear()
    
    quiz_data = generate_quizzes(note.summary, note.language)
    if not quiz_data['success'] :
       print(quiz_data['error'])
       raise HTTPException(status_code=500, detail="Server fail")
     
    note.quizzes = quiz_data['data']['quizzes']
    db.commit()
    db.refresh(note)
    return note.quizzes

@router.put("/{note_id}/move-folder")
async def move_note_to_folder(note_id: int, new_folder_id: int, current_user: User = Depends(auth_guard), 
                              db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note = move_note_to_folder_usecase(db=db, note_id=note_id, new_folder_id=new_folder_id)
    return updated_note

@router.put("/{note_id}/remove-folder")
async def remove_note_folder(note_id: int, current_user: User = Depends(auth_guard), 
                             db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note = remove_note_folder_usecase(db=db, note_id=note_id)
    return updated_note

@router.get("/{note_id}/folder/")
async def get_folder_by_note_id(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    folder = get_folder_by_note_id_usecase(db, note_id=note_id, user_id=current_user.id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.post("/export-note/")
async def export_note(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    note = get_note_by_id(db, note_id=note_id, user_id=current_user.id)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    shared_url = f"https://gomemo.ai/{current_user.username}/{note_id}"

    return {"message": "Note exported successfully", "shared_url": shared_url, "note": note}

@router.post("/import-note/")
async def export_note(old_note_id: int, old_user_username: str, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    old_user = db.query(User).filter(User.username == old_user_username).first()
    old_note = get_note_by_id(db, note_id=old_note_id, user_id=old_user.id)
    old_note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == old_note.id, NoteMetadata.user_id == old_user.id).first()
    
    if not old_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_create = NoteCreate(
        title=old_note.title,
        summary=old_note.summary,
        transcript_text=old_note.transcript_text,
        language=old_note.language,
        content_url=old_note.content_url,
    )
    new_note = add_note(
        db=db,
        user_id=current_user.id,
        folder_id=None,
        note_create=note_create
    )

    metadata_create = NoteMetadataCreate(
        title=old_note_metadata.title,
        content_category=old_note_metadata.content_category,
        emoji_representation=old_note_metadata.emoji_representation,
        date_created=datetime.now()
    )
    new_note_metadata = add_metadata(
        db=db,
        user_id=current_user.id,
        note_id=new_note.id,
        metadata_create=metadata_create
    )
    
    old_shared_url = f"https://gomemo.ai/{old_user.username}/{old_note.id}"
    new_shared_url = f"https://gomemo.ai/{current_user.username}/{new_note.id}"
    
    return { "message": "Note imported successfully", 
            "old_shared_url": old_shared_url, 
            "old_note_id": old_note.id,
            "new_shared_url": new_shared_url, 
            "new_note_id": new_note.id}
    
@router.get("/chat/")
async def generate_chat_response(
    note_id: int,
    chat_input: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = get_note_by_id(db, note_id=note_id, user_id=current_user.id)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    summary = note.summary
    lang = note.language
    chat_response = generate_chat(chat_input, summary, lang)

    if not chat_response['success']:
        return {"status": "error", "chatInput": chat_input, "answer": "Failed to generate chat response"}

    return chat_response

# @router.get("/chat/")
# async def generate_chat_response(
#     chat_input: str,
#     note_id: int,
#     current_user: User = Depends(auth_guard),
#     db: Session = Depends(get_db)
# ):
#     async def event_generator():
#         try:
#             yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating chat response...'})}\n\n"
            
#             note = get_note_by_id(db, note_id=note_id, user_id=current_user.id)
            
#             if not note:
#                 raise HTTPException(status_code=404, detail="Note not found")
            
#             summary = note.summary
#             lang = note.language
#             chat_response = generate_chat(chat_input, summary, lang)

#             if not chat_response['success']:
#                 print(chat_response["error"])
#                 yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to generate chat response'})}\n\n"
#                 return

#             chat_response_data = chat_response['data']

#             yield f"data: {json.dumps({'status': 'complete', 'message': chat_response_data})}\n\n"

#         except Exception as e:
#             yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed: {str(e)}'})}\n\n"

#     return StreamingResponse(event_generator(), media_type="text/event-stream")
