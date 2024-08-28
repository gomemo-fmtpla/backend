# app/api/notes.py

from datetime import datetime
import json
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.commons.pydantic_to_json import metadata_to_dict, note_to_dict
from app.database.db import get_db
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteUpdate
from app.usecases.auth_guard import auth_guard
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio
from app.usecases.note.note import (
    add_metadata,
    add_note, 
    update_note,
    get_note_by_id, 
    move_folder, 
    remove_folder, 
    get_all_notes,
    get_unfoldered_notes, 
    get_notes_by_folder,
)
from app.usecases.generation.summary_generation import generate_summary
from app.usecases.generation.transcript_extraction import generate_transcript
from app.usecases.generation.summary_translation_generation import translate_summary  # Assuming you have a function for translation
from app.usecases.generation.flashcard_generation import generate_flashcards  # Assuming a flashcard function
from app.usecases.generation.quiz_generation import generate_quizzes  # Assuming a quizzes function
from app.database.models import NoteMetadata, User, Note
from typing import List, Dict, Any, Optional

from app.usecases.storage.audio_store import delete_object, extract_audio_filename, put_object

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
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating transcript...'})}\n\n"

            transcript_response = generate_transcript(youtube_url)
            if not transcript_response['success']:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe the YouTube video'})}\n\n"
                return
            transcript = transcript_response['data']['transcript']

            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"

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
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed: {str(e)}'})}\n\n"

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
        return {"success": True, "url": object_url}
    
    except Exception as e:
        if 'object_url' in locals():
            delete_object(object_url)
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
        try:
            # Step 1: Transcribe the audio
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Transcribing audio...'})}\n\n"
            print(audio_url)
            transcription_response = transcribe_audio(audio_url=audio_url)
            if not transcription_response['success']:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n"
                return
            
            transcript = transcription_response['data']['transcript']

            # Step 2: Generate summary
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating summary...'})}\n\n"
            
            summary_response = generate_summary(transcript, lang, context=context)
            if not summary_response['success']:
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
            yield f"data: {json.dumps({'status': 'error', 'message': 'Process failed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.put("/{note_id}")
async def update_existing_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    updated_note = update_note(db, note_id=note_id, note_update=note_update)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id and current_user.id == Note.id).first()
    note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note_id and NoteMetadata.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    file_name = extract_audio_filename(note.content_url)
    if file_name :
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
            # Step 1: Retrieve the note
            note = db.query(Note).filter(Note.id == note_id).first()
            if not note:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to get note'})}\n\n"
                return

            # Step 2: Translate the note's transcript
            translation = translate_summary(note.transcript_text, target_language)
            if not translation['success']:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Failed to translate summary'})}\n\n"
                return
            
            translated_text = translation['data']['translated_text']

            # Step 3: Generate summary
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Generating translated summary...'})}\n\n"
            
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

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'Process failed: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/flashcard/{note_id}")
async def create_flashcards(
    note_id: int,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id and Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.flashcards :
        return note.flashcards

    flashcard_data = generate_flashcards(note.transcript_text, note.language)
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
    note = db.query(Note).filter(Note.id == note_id and Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.quizzes :
        return note.quizzes
    
    quiz_data = generate_quizzes(note.transcript_text, note.language)
    note.quizzes = quiz_data['data']['quizzes']
    db.commit()
    db.refresh(note)
    return note.quizzes
