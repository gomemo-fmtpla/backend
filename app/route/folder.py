from datetime import datetime
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.usecases.auth_guard import auth_guard
from app.usecases.note.folder import (
    get_all_folders_usecase, 
    get_all_folders_with_note_count_usecase, 
    create_folder_usecase, 
    update_folder_usecase, 
    delete_folder_usecase
)
from app.database.models import Folder, User
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteMetadataUpdate, NoteUpdate
from typing import List, Optional

router = APIRouter(
    prefix="/folders",
    tags=["folders"]
)

@router.get("/")
async def get_folders(current_user: User = Depends(auth_guard), 
                    db: Session = Depends(get_db)):
    return get_all_folders_with_note_count_usecase(db=db, user_id=current_user.id)

@router.get("/{folder_id}")
async def get_folder(folder_id: int, current_user: User = Depends(auth_guard), 
                     db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.post("/")
async def create_folder(folder_name: str, current_user: User = Depends(auth_guard), 
                        db: Session = Depends(get_db)):
    try:
        folder = create_folder_usecase(db=db, user_id=current_user.id, folder_name=folder_name)
        return folder
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{folder_id}")
async def update_folder(folder_id: int, folder_name: str, current_user: User = Depends(auth_guard), 
                        db: Session = Depends(get_db)):
    updated_folder = update_folder_usecase(db=db, folder_id=folder_id, folder_name=folder_name)
    if not updated_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return updated_folder

@router.delete("/{folder_id}")
async def remove_folder(folder_id: int, current_user: User = Depends(auth_guard), 
                        db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    success = delete_folder_usecase(db=db, folder_id=folder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"detail": "Folder deleted successfully", "folder_id": folder_id, "folder_name": folder.name}