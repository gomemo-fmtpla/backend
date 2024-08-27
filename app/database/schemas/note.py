# app/database/schemas/note.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any

class NoteBase(BaseModel):
    title: str
    summary: str
    transcript_text: str
    language: str
    content_url: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    transcript_text: Optional[str] = None
    language: Optional[str] = None
    content_url: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

class NoteInFolderResponse(BaseModel):
    id: int
    title: str
    summary: str
    transcript_text: str
    language: str
    content_url: Optional[str] = None
    flashcards: Optional[Dict[str, Any]] = None
    quizzes: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class NoteMetadataCreate(BaseModel):
    title: str
    content_category: str
    emoji_representation: str
    date_created: datetime

class NoteMetadataUpdate(BaseModel):
    title: Optional[str] = None
    date_created: Optional[datetime] = None
