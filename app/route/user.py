import os

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.db import get_db
from app.database.models import Note, NoteMetadata, User
from app.usecases.auth_guard import auth_guard
from app.database.schemas.user import UserCreate, UserUpdate
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
        note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note.id).first()
        if note_metadata:
            db.delete(note_metadata)
        
        file_name = extract_audio_filename(note.content_url)
        if file_name and not note.translated:
            delete_object(file_name=file_name)
        
        db.delete(note)
    
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