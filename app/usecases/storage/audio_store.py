import os
import time
import uuid
from fastapi import HTTPException
import requests
from minio import Minio, S3Error
import urllib.parse

from app.commons.environment_manager import load_env

# Create client with access key and secret key with specific region.
load_env()
MINIO_ENDPOINTS = os.getenv("MINIO_ENDPOINTS")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

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


def extract_audio_filename(audio_url: str):
    # Decode the URL
    decoded_url = urllib.parse.unquote(audio_url)
    
    # Check if the URL is a YouTube link
    if "youtube.com" in decoded_url or "youtu.be" in decoded_url:
        return None  # Or handle YouTube links differently if needed
    
    # Extract the filename from the URL
    path = urllib.parse.urlparse(decoded_url).path
    filename = path.split('/')[-1]
    return filename

def extract_audio_filename(url: str) -> str:
    if not url:
        raise ValueError("Empty URL provided")
    try:
        # Extract filename from URL
        filename = url.split('/')[-1]
        if not filename:
            raise ValueError("Could not extract filename from URL")
        return filename
    except Exception as e:
        raise ValueError(f"Failed to extract filename from URL: {str(e)}")

def delete_object(file_name: str):
    try:
        # Check if object exists before trying to delete
        if not minio_client.stat_object(BUCKET_NAME, file_name):
            raise ValueError(f"File {file_name} does not exist in MinIO bucket")
        # Delete the file from MinIO
        minio_client.remove_object(BUCKET_NAME, file_name)
    except Exception as e:
        raise ValueError(f"Failed to delete file from MinIO: {str(e)}")