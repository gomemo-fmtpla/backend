from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import JSON 
from sqlalchemy.dialects.postgresql import JSON as PostgresJSON
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
    
    primary_goal = Column(String(100), nullable=True)
    user_type = Column(String(50), nullable=True)
    study_format = Column(String(50), nullable=True)
    usage_frequency = Column(String(50), nullable=True)
    focus_topic = Column(String(100), nullable=True)
    learning_style = Column(String(50), nullable=True)
    
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
    flashcards = Column(JSON().with_variant(PostgresJSON, 'postgresql'), nullable=True, default=None)
    quizzes = Column(JSON().with_variant(PostgresJSON, 'postgresql'), nullable=True, default=None)
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