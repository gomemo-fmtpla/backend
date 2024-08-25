# app/api/notes.py

from datetime import datetime
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.commons.pydantic_to_json import note_to_dict
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
from app.database.models import User, Note
from typing import List, Dict, Any, Optional

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

@router.post("/generate/youtube/")
async def generate_youtube_summary(
    youtube_url: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    # Generate transcript
    transcript_response = generate_transcript(youtube_url)
    if not transcript_response['success']:
        raise HTTPException(status_code=400, detail=transcript_response['error'])
    
    transcript = transcript_response['data']['transcript']
    
    # Generate summary
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])
    
    summary_data = summary_response['data']
    print(summary_data)

    # Create a new note
    note_create = NoteCreate(
        title=summary_data['title'],  # Use the title from the summary
        summary=summary_data['markdown'],
        transcript_text=transcript,
        language=summary_data['lang'],
        youtube_link=youtube_url,
    )

    new_note = add_note(
        db=db,
        user_id=current_user.id,
        folder_id=None,  # Or specify a folder_id if needed
        note_create=note_create
    )
    
    note_dict = note_to_dict(new_note)
    print(note_dict)

    # Create metadata for the new note
    metadata_create = NoteMetadataCreate(
        title=summary_data['title'],
        content_category=summary_data['content_category'],
        emoji_representation=summary_data['emoji_representation'],
        date_created=datetime.now()   
    )

    add_metadata(
        db=db,
        note_id=new_note.id,
        metadata_create=metadata_create
    )
    
    return {
        "success": True,
        "data": {
            "note": note_dict
        }
    }

@router.post("/generate/audio/")
async def generate_audio_summary(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
) :
    # Save the uploaded file to a temporary location
    try:
        audio_path = f"/tmp/{audio_file.filename}"
        with open(audio_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        # Transcribe the audio
        transcription_response = transcribe_audio(audio_path)
        if not transcription_response['success']:
            raise HTTPException(status_code=500, detail=transcription_response['error'])
        
        transcript = transcription_response['data']['transcript']
        
        # Generate summary
        summary_response = generate_summary(transcript)
        if not summary_response['success']:
            raise HTTPException(status_code=500, detail=summary_response['error'])
        
        summary_data = summary_response['data']
        
        # Create a new note
        note_create = NoteCreate(
            title=summary_data['title'],  # Use the title from the summary
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            youtube_link="",
        )

        new_note = add_note(
            db=db,
            user_id=current_user.id,
            folder_id=None,  # Or specify a folder_id if needed
            note_create=note_create
        )

        note_dict = note_to_dict(new_note)
        print(note_dict)
    
        # Create metadata for the new note
        metadata_create = NoteMetadataCreate(
            title=summary_data['title'],
            content_category=summary_data['content_category'],
            emoji_representation=summary_data['emoji_representation'],
            date_created=datetime.now()   
        )

        add_metadata(
            db=db,
            user_id=current_user.id,
            note_id=new_note.id,
            metadata_create=metadata_create
        )
        
        return {
            "success": True,
            "data": {
                "note": note_dict
            }
        }
    
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)

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
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"detail": "Note deleted"}

@router.post("/translate/{note_id}")
async def translate_note_endpoint(
    note_id: int,
    target_language: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    translation = translate_summary(note.transcript_text, target_language)
    if not translation['success']:
        raise HTTPException(status_code=500, detail=translation['error'])
    
    return {"translated_text": translation['data']['translated_text']}

# @router.get("/flashcard/{note_id}")
# async def get_flashcards(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
#     note = db.query(Note).filter(Note.id == note_id and Note.user_id == current_user.id).first()
#     if not note:
#         raise HTTPException(status_code=404, detail="Note not found")
    
#     return note.flashcards

# @router.get("/quizzes/{note_id}")
# async def get_quizzes(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
#     note = db.query(Note).filter(Note.id == note_id and Note.user_id == current_user.id).first()
#     if not note:
#         raise HTTPException(status_code=404, detail="Note not found")
    
#     return note.quizzes

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

    flashcard_data = generate_flashcards(note.transcript_text)
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
    
    quiz_data = generate_quizzes(note.transcript_text)
    note.quizzes = quiz_data['data']['quizzes']
    db.commit()
    db.refresh(note)
    return note.quizzes
