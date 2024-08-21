# app/database/schemas/note.py

from pydantic import BaseModel
from typing import Optional, Dict, Any

class NoteBase(BaseModel):
    title: str
    summary: str
    transcript_text: str
    language: str
    youtube_link: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    transcript_text: Optional[str] = None
    language: Optional[str] = None
    youtube_link: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

class NoteInFolderResponse(BaseModel):
    id: int
    title: str
    summary: str
    transcript_text: str
    language: str
    youtube_link: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
