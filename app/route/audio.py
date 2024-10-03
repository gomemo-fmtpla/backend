from app.commons.environment_manager import load_env
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, APIRouter
from supabase import create_client, Client
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
import uuid
import os

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
)

# Initialize Supabase client to None
supabase: Client = None

# Function to initialize Supabase client if not already initialized
def get_supabase_client():
    global supabase
    if supabase is None:
        SUPABASE_URL = "http://49.12.195.35:8000/"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
        SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q"
        supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
    return supabase

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:c42f68c2db2a5335a5db@49.12.195.35:3656/gomemo"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

# Define the table
audio_files = Table(
    'audio_files', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('user_id', Integer, index=True),
    Column('file_url', String, index=True)
)

metadata.create_all(bind=engine)

@router.post("/upload/")
async def upload_audio_file(user_id: int = Form(...), file: UploadFile = File(...)):
    try:
        # Ensure Supabase client is initialized
        supabase_client = get_supabase_client()
        
        # Create a new bucket if it doesn't exist
        bucket_name = "audio-files"
        existing_buckets = supabase_client.storage.list_buckets()
        if not any(bucket.name == bucket_name for bucket in existing_buckets):
            supabase_client.storage.create_bucket(bucket_name)

        # Rename the file before upload
        file_extension = os.path.splitext(file.filename)[1]
        new_file_name = f"{uuid.uuid4()}{file_extension}"

        # Upload the file to the bucket
        file_content = await file.read()
        supabase_client.storage.from_(bucket_name).upload(new_file_name, file_content)

        # Get the public URL of the uploaded file
        public_url = supabase_client.storage.from_(bucket_name).get_public_url(new_file_name)

        # Save the public URL and user_id into the PostgreSQL database
        db = SessionLocal()
        new_audio_file = {
            "user_id": user_id,
            "file_url": public_url
        }
        db.execute(audio_files.insert().values(new_audio_file))
        db.commit()
        db.close()

        return {"status": "success", "file_url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/supabase-health")
async def supabase_health():    
    try:
        # Ensure Supabase client is initialized
        supabase_client = get_supabase_client()
        
        # Test a simple request to Supabase, for example, list all buckets
        buckets = supabase_client.storage.list_buckets()
        return {"status": "connected", "buckets": [bucket.name for bucket in buckets]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase connection failed: {str(e)}")
