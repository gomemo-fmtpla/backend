from app.usecases.user.user import get_user_by_username
from app.database.models import User
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
import os

async def verify_api_key(
    api_key: str = Header(None),
    user: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Verify the API key and check if the user exists in the database."""
    
    # Check if API key is present
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key is missing")

    # Check if user_id is present
    if user is None:
        raise HTTPException(status_code=401, detail="User ID is missing")

    # Load the expected API key from the environment or configuration
    expected_api_key = os.getenv("API_KEY")

    # Verify the API key
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Fetch the user from the database
    user = get_user_by_username(db, user)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def auth_guard(current_user: User = Depends(verify_api_key)) -> User:
    """Guard function that ensures the user is authenticated and exists."""
    return current_user