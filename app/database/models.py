from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), index=True)
    hashed_password = Column(String(100))
    subscription_plan = Column(String, nullable=False, default="trial")
    subscription_end_date = Column(Date)
    transaction_receipt = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    folders = relationship("Folder", back_populates="user")
    notes = relationship("Note", back_populates="user")
    note_metadata = relationship("NoteMetadata", back_populates="user")

class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="folders")
    notes = relationship("Note", back_populates="folder")
    note_metadata = relationship("NoteMetadata", back_populates="folder")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    content_url = Column(String(1024), nullable=True)
    title = Column(String(255))
    summary = Column(Text)
    transcript_text = Column(Text)
    language = Column(String(10))
    translated = Column(Boolean, nullable=True, default=False)
    flashcards = Column(JSONB, nullable=True, default=None)
    quizzes = Column(JSONB, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="notes")
    folder = relationship("Folder", back_populates="notes")
    note_metadata = relationship("NoteMetadata", back_populates="note", uselist=False)

class NoteMetadata(Base):
    __tablename__ = "note_metadata"

    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    title = Column(String(255), nullable=False)
    content_category = Column(String(50), nullable=False)
    emoji_representation = Column(String(10), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    note = relationship("Note", back_populates="note_metadata")
    user = relationship("User", back_populates="note_metadata")
    folder = relationship("Folder", back_populates="note_metadata")

class NoteLink(Base):
    __tablename__ = 'note_links'
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    public_url = Column(String, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="note_links")
    note = relationship("Note", back_populates="note_links")