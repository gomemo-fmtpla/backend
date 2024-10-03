import os
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from supabase import create_client, Client
import asyncpg
import uuid

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
)

# Initialize Supabase client
SUPABASE_URL = "http://49.12.195.35:8000/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q"
supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:c42f68c2db2a5335a5db@49.12.195.35:3656/gomemo"

# Initialize the PostgreSQL connection pool
async def get_pg_conn():
    return await asyncpg.connect(DATABASE_URL)

# Anonymous login function for guest users
def guest_login():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=anonymous"
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)
    print(f"Guest login response status: {response.status_code}")
    print(f"Guest login response headers: {response.headers}")
    print(f"Guest login response body: {response.text}")

    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        try:
            error_message = response.json().get('error', 'Unknown error')
        except ValueError:
            error_message = response.text
        raise HTTPException(status_code=500, detail=f"Guest login failed: {error_message}")

class AudioResponse(BaseModel):
    message: str
    public_url: str

async def save_to_db(user_id: int, public_url: str, conn):
    query = """
    INSERT INTO audio_files (user_id, public_url) 
    VALUES ($1, $2)
    RETURNING id;
    """
    try:
        record_id = await conn.fetchval(query, user_id, public_url)
        return record_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@router.post("/", response_model=AudioResponse)
async def uploadAudioFile(file: UploadFile = File(...), user_id: int = 1, conn=Depends(get_pg_conn)):
    try:
        # Anonymous guest login
        access_token = guest_login()
        supabase.auth.set_auth(access_token)

        # Rename the file
        unique_filename = f"{uuid.uuid4()}.mp3"
        file_content = await file.read()

        # Upload the file to the Supabase bucket
        try:
            supabase.storage.from_('audio_files_bucket').upload(f"audios/{unique_filename}", file_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

        # Get the public URL of the uploaded file
        public_url = supabase.storage.from_('audio_files_bucket').get_public_url(f"audios/{unique_filename}")

        # Save the public URL in the PostgreSQL database
        await save_to_db(user_id, public_url, conn)

        return AudioResponse(message="File uploaded successfully", public_url=public_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/supabase-health")
async def supabase_health():
    try:
        # Test a simple request to Supabase, for example, list all buckets
        buckets = supabase.storage.list_buckets()
        return {"status": "connected", "buckets": buckets}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase connection failed: {str(e)}")
