# app/api/notes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.schemas.note import NoteCreate, NoteUpdate
from app.usecases.auth_guard import auth_guard
from app.usecases.note.note import (
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
from app.usecases.generation.summary_translation_generation import translate_note  # Assuming you have a function for translation
from app.usecases.generation.flashcard_generation import generate_flashcards  # Assuming a flashcard function
from app.usecases.generation.quiz_generation import generate_quizzes  # Assuming a quizzes function
from app.database.models import User, Note
from typing import List, Dict, Any, Optional

router = APIRouter(
    prefix="/note",
    tags=["note"]
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
    transcript_response = generate_transcript(youtube_url)
    if not transcript_response['success']:
        raise HTTPException(status_code=400, detail=transcript_response['error'])
    
    transcript = transcript_response['data']['transcript']
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])
    
    return summary_response

@router.post("/generate/audio/")
async def generate_audio_summary(
    transcript: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])
    
    return summary_response

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

@router.post("/translate/")
async def translate_note_endpoint(
    note_id: int,
    target_language: str,
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    translation = translate_note(note.transcript_text, target_language)
    if not translation['success']:
        raise HTTPException(status_code=500, detail=translation['error'])
    
    return {"translated_text": translation['data']['translated_text']}

@router.get("/flashcard/")
async def get_flashcards(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note.flashcards

@router.get("/quizzes/")
async def get_quizzes(note_id: int, current_user: User = Depends(auth_guard), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note.quizzes

@router.post("/flashcard/")
async def create_flashcards(
    note_id: int,
    flashcard_data: Dict[str, Any],
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.flashcards = flashcard_data
    db.commit()
    db.refresh(note)
    return note.flashcards

@router.post("/quizzes/")
async def create_quizzes(
    note_id: int,
    quiz_data: Dict[str, Any],
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.quizzes = quiz_data
    db.commit()
    db.refresh(note)
    return note.quizzes
