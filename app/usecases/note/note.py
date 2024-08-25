# app/usecases/note.py

from sqlalchemy.orm import Session
from app.database.models import Folder, Note, NoteMetadata, User
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteMetadataUpdate, NoteUpdate
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

def add_note(
    db: Session, 
    user_id: int, 
    folder_id: Optional[int], 
    note_create: NoteCreate
) -> Note:
    try:
        new_note = Note(
            user_id=user_id,
            folder_id=folder_id,
            **note_create.dict()  # Unpack the Pydantic model to pass parameters
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_note(
    db: Session, 
    note_id: int, 
    note_update: NoteUpdate
) -> Optional[Note]:
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None
        for field, value in note_update.dict(exclude_unset=True).items():
            setattr(note, field, value)
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def add_metadata(
    db: Session, 
    user_id: int,
    note_id: int, 
    metadata_create: NoteMetadataCreate
) -> NoteMetadata:
    try:
        new_metadata = NoteMetadata(
            user_id=user_id,
            note_id=note_id,
            **metadata_create.dict()
        )
        db.add(new_metadata)
        db.commit()
        db.refresh(new_metadata)
        return new_metadata
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def update_metadata(
    db: Session, 
    note_id: int, 
    metadata_update: NoteMetadataUpdate
) -> Optional[NoteMetadata]:
    try:
        metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note_id).first()
        if not metadata:
            return None
        for field, value in metadata_update.dict(exclude_unset=True).items():
            setattr(metadata, field, value)
        db.commit()
        db.refresh(metadata)
        return metadata
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def move_folder(
    db: Session, 
    folder_id: int, 
    new_folder_id: Optional[int]
) -> List[Note]:
    try:
        notes = db.query(Note).filter(Note.folder_id == folder_id).all()
        for note in notes:
            note.folder_id = new_folder_id
        db.commit()
        return notes
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def remove_folder(db: Session, folder_id: int) -> List[Note]:
    try:
        notes = db.query(Note).filter(Note.folder_id == folder_id).all()
        for note in notes:
            note.folder_id = None  # Unlink notes from the folder
        db.query(Folder).filter(Folder.id == folder_id).delete()
        db.commit()
        return notes
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_all_notes(db: Session, user_id: int) -> List[NoteMetadata]:
    return db.query(NoteMetadata).filter(NoteMetadata.user_id == user_id).all()

def get_unfoldered_notes(db: Session, user_id: int) -> List[Note]:
    return db.query(Note).filter(Note.user_id == user_id, Note.folder_id == None).all()

def get_notes_by_folder(db: Session, folder_id: int) -> List[Note]:
    return db.query(Note).filter(Note.folder_id == folder_id).all()

def get_note_by_id(db: Session, note_id: int, user_id: int) -> Note:
    return db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()


