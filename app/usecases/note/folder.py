from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Folder, Note, NoteMetadata, User
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteMetadataUpdate, NoteUpdate
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

def get_all_folders_usecase(db: Session, user_id: int) -> List[Folder]:
    return db.query(Folder).filter(Folder.user_id == user_id).all()

def get_all_folders_with_note_count_usecase(db: Session, user_id: int) -> List[dict]:
    folders = db.query(Folder).filter(Folder.user_id == user_id).all()
    folder_list = []
    for folder in folders:
        note_count = db.query(Note).filter(Note.folder_id == folder.id).count()
        folder_list.append({
            "folder": folder,
            "note_count": note_count
        })
    return folder_list

def create_folder_usecase(db: Session, user_id: int, folder_name: str) -> Folder:
    new_folder = Folder(name=folder_name, user_id=user_id, created_at=datetime.now())
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

def update_folder_usecase(db: Session, folder_id: int, folder_name: str) -> Optional[Folder]:
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder:
        folder.name = folder_name
        folder.updated_at = datetime.now()
        db.commit()
        db.refresh(folder)
    return folder

def delete_folder_usecase(db: Session, folder_id: int) -> bool:
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder:
        db.delete(folder)
        db.commit()
        return True
    return False