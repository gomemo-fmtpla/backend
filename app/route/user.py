import os

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.db import get_db
from app.database.models import Folder, Note, NoteMetadata, User
from app.usecases.auth_guard import auth_guard
from app.database.schemas.user import UserCreate, UserUpdate, UserOnboardingUpdate
from app.usecases.note.note import create_welcoming_note
from app.usecases.storage.audio_store import delete_object, extract_audio_filename
from app.usecases.user.user import (
    get_user_by_username,
    create_user, 
    update_user, 
    get_subscription_status
)

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

class AuthUserRequest(BaseModel):
    username: str
    email: str

class SubscriptionUpdateRequest(BaseModel):
    subscription_plan: str
    receipt: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_or_create_user(
    db: Session, 
    username: str, 
    email: str
):
    user = get_user_by_username(db, username)
    if user:
        return user
        # if verify_password(password, user.hashed_password):
        #     return user
        # else:
        #     raise HTTPException(status_code=401, detail="Incorrect password")
    else:
        # Hash the password before storing it
        # hashed_password = hash_password(password)
        user_create = UserCreate(username=username, email=email)
        new_user = create_user(db, user_create)
        create_welcoming_note(db=db, user_id=new_user.id)
        return new_user


# POST /auth_user
@router.post("/auth/")
async def auth_user(
    request: AuthUserRequest, 
    db: Session = Depends(get_db)
):
    user = await authenticate_or_create_user(db, request.username, request.email)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "subscription_plan": user.subscription_plan,
        "subscription_end_date": user.subscription_end_date,
    }

# GET /subscription
@router.get("/subscription/")
async def get_subscription(
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    subscription_status = get_subscription_status(db, current_user.id)
    return subscription_status

# POST /subscription
@router.post("/subscription/")
async def update_subscription(
    request: SubscriptionUpdateRequest, 
    current_user: User = Depends(auth_guard), 
    db: Session = Depends(get_db)
):
    user_update = UserUpdate(
        subscription_plan=request.subscription_plan,
        transaction_receipt=request.receipt
    )
    updated_user = update_user(db, current_user.id, user_update)
    return {
        "subscription_plan": updated_user.subscription_plan,
        "receipt": updated_user.transaction_receipt,
    }

from fastapi import HTTPException

@router.delete("/delete/")
async def delete_user(
    current_user: User = Depends(auth_guard),
    db: Session = Depends(get_db)
):
    user_to_delete = get_user_by_id(db, current_user.id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete all notes related to the current user
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    for note in notes:
        # Delete note metadata
        note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note.id).first()
        if note_metadata:
            db.delete(note_metadata)
        
        # Delete associated Minio files
        if note.content_url:
            file_name = extract_audio_filename(note.content_url)
            if file_name:  # Remove the translated check since we want to delete all files
                try:
                    delete_object(file_name=file_name)
                except Exception as e:
                    print(f"Error deleting file {file_name}: {str(e)}")
                    # Continue with deletion even if file deletion fails
                    pass
        
        db.delete(note)
    
    # Delete user folders (the cascade will handle related records)
    folders = db.query(Folder).filter(Folder.user_id == current_user.id).all()
    for folder in folders:
        db.delete(folder)
    
    delete_user_by_id(db, current_user.id)
    db.commit()
    
    return {
        "message": "User deleted successfully", 
        "user_id": current_user.id,
        "username": current_user.username,
    }

def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()

def delete_user_by_id(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()

# POST /update_onboarding_data
@router.post("/update_onboarding_data/")
async def update_onboarding_data(
    primary_goal: str,
    user_type: str,
    study_format: str,
    usage_frequency: str,
    focus_topic: str,
    learning_style: str,
    current_user: User = Depends(auth_guard), 
    db: Session = Depends(get_db),
    
):
    user_update = UserOnboardingUpdate(
        primary_goal=primary_goal,
        user_type=user_type,
        study_format=study_format,
        usage_frequency=usage_frequency,
        focus_topic=focus_topic,
        learning_style=learning_style,
    )
    updated_user = update_user(db, current_user.id, user_update)
    return {
        "primary_goal": updated_user.primary_goal,
        "user_type": updated_user.user_type,
        "study_format": updated_user.study_format,
        "usage_frequency": updated_user.usage_frequency,
        "focus_topic": updated_user.focus_topic,
        "learning_style": updated_user.learning_style,
    }