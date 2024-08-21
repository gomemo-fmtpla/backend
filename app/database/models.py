from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class SubscriptionPlanType(enum.Enum):
    free = 'free'
    weekly = 'weekly'
    monthly = 'monthly'
    annual = 'annual'

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    subscription_plan = Column(Enum(SubscriptionPlanType), nullable=False, default=SubscriptionPlanType.free)
    subscription_end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    folders = relationship("Folder", back_populates="user")
    notes = relationship("Note", back_populates="user")

class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="folders")
    notes = relationship("Note", back_populates="folder")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    # adding youtube link
    youtube_link = Column(String(255), nullable=True)
    title = Column(String(255))
    summary = Column(Text)
    transcript_text = Column(Text)
    language = Column(String(10))
    flashcards = Column(JSONB, nullable=True, default=None)
    quizzes = Column(JSONB, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="notes")
    folder = relationship("Folder", back_populates="notes")

class NoteMetadata(Base):
    __tablename__ = "note_metadata"

    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    title = Column(String(255), nullable=False)
    content_category = Column(String(50), nullable=False)
    emoji_representation = Column(String(10), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    note = relationship("Note", back_populates="note_metadata")