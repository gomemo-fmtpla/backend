import os
import time
import uuid
from fastapi import HTTPException
import requests
from minio import Minio, S3Error
import urllib.parse

from app.commons.environment_manager import load_env
from app.commons.logger import logger

# Create client with access key and secret key with specific region.
load_env()
MINIO_ENDPOINTS = os.getenv("MINIO_ENDPOINTS")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

if not all([MINIO_ENDPOINTS, MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
    error_msg = "Missing required MinIO environment variables:"
    if not MINIO_ENDPOINTS:
        error_msg += " MINIO_ENDPOINTS"
    if not MINIO_ACCESS_KEY:
        error_msg += " MINIO_ACCESS_KEY"
    if not MINIO_SECRET_KEY:
        error_msg += " MINIO_SECRET_KEY"
    logger.error(error_msg)
    raise ValueError(error_msg)

minio_client = Minio(
    endpoint=MINIO_ENDPOINTS,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=True
)

BUCKET_NAME = "gomemo"

def put_object(audio_file, audio_path) -> str:
    try:
        timestamp = int(time.time())
        file_extension = os.path.splitext(audio_file.filename)[1]
        file_name = os.path.splitext(audio_file.filename)[0]
        minio_file_name = f"{file_name}_{timestamp}{file_extension}"
        
        # Upload the file to MinIO
        print(f"Putting object [{audio_file}] [{minio_file_name}] to MinIO...")
        minio_client.fput_object(
            BUCKET_NAME,
            minio_file_name,
            audio_path
        )
        
        # Generate public URL for the file (without expiration)
        public_url = f"{MINIO_ENDPOINTS}/{BUCKET_NAME}/{minio_file_name}"
        print(f"MinIO public url: [{public_url}]")
        return public_url

    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to MinIO: {str(err)}")

def copy_file_from_url(public_url: str) -> str:
    try:
        # Download the file from the public URL
        # Check if the URL is a YouTube URL
        if "youtube.com" in public_url or "youtu.be" in public_url:
            return public_url
        
        response = requests.get(public_url)
        response.raise_for_status()

        # Extract file name from URL
        parsed_url = urllib.parse.urlparse(public_url)
        file_name = os.path.basename(parsed_url.path)
        file_extension = os.path.splitext(file_name)[1]

        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        minio_file_name = f"{file_id}{file_extension}"

        # Save the file locally
        local_file_path = f"/tmp/{minio_file_name}"
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        # Upload the file to MinIO
        minio_client.fput_object(
            BUCKET_NAME,
            minio_file_name,
            local_file_path
        )

        # Generate public URL for the file
        public_url = f"{MINIO_ENDPOINTS}/{BUCKET_NAME}/{minio_file_name}"
        print("New public url : ", public_url)
        return public_url

    except requests.RequestException as req_err:
        raise HTTPException(status_code=400, detail=f"Failed to download file from URL: {str(req_err)}")
    except S3Error as s3_err:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to MinIO: {str(s3_err)}")
    finally:
        # Clean up the local file
        if 'local_file_path' in locals() and os.path.exists(local_file_path):
            os.remove(local_file_path)

def extract_audio_filename(url: str) -> str:
    if not url:
        raise ValueError("Empty URL provided")
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # For YouTube URLs, extract the video ID and create a simple filename
        if "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
            query_params = urllib.parse.parse_qs(parsed_url.query)
            video_id = query_params.get('v', [''])[0]
            if video_id:
                return f"youtube_{video_id}"
            elif parsed_url.path.startswith('/watch_v='):
                # Handle already processed YouTube URLs
                video_id = parsed_url.path.split('=')[1]
                return f"youtube_{video_id}"
        
        # For regular URLs, get the last component of the path
        filename = parsed_url.path.split('/')[-1]
        if not filename:
            raise ValueError("Could not extract filename from URL")
        return filename
    except Exception as e:
        raise ValueError(f"Failed to extract filename from URL: {str(e)}")

def delete_object(file_name: str):
    try:
        # For YouTube files, they're stored with a simple prefix format
        if file_name.startswith('youtube_'):
            encoded_file_name = file_name 
        else:
            # For other files, URL encode the filename to handle special characters
            encoded_file_name = urllib.parse.quote(file_name)
        
        try:
            # Try to delete the object without checking existence first
            minio_client.remove_object(BUCKET_NAME, encoded_file_name)
        except S3Error as s3_err:
            if s3_err.code == 'NoSuchKey':
                # Object doesn't exist, which is fine for deletion
                pass
            else:
                # Other S3 errors should be raised
                raise
    except Exception as e:
        raise ValueError(f"Failed to delete file from MinIO: {str(e)}")