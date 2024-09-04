import os
import uuid
from fastapi import HTTPException
from minio import Minio, S3Error
import urllib.parse

from app.commons.environment_manager import load_env;

# Create client with access key and secret key with specific region.
load_env()
minio_client = Minio(
    "gomemo-minio.skaq74.easypanel.host",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
)

BUCKET_NAME = "gomemo"

def put_object(audio_file, audio_path) -> str:
    try:
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(audio_file.filename)[1]
        minio_file_name = f"{file_id}{file_extension}"
        
        # Upload the file to MinIO
        minio_client.fput_object(
            BUCKET_NAME,
            minio_file_name,
            audio_path
        )
        
        # Generate public URL for the file
        public_url = minio_client.presigned_get_object(BUCKET_NAME, minio_file_name)
        return public_url

    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to MinIO: {str(err)}")

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


def delete_object(file_name: str):
    """
    Deletes an object from the MinIO bucket.
    
    :param file_name: The name of the file in MinIO to delete.
    :raises HTTPException: If the deletion from MinIO fails.
    """
    try:
        # Delete the file from MinIO
        minio_client.remove_object(BUCKET_NAME, file_name)
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Failed to delete file from MinIO: {str(err)}")