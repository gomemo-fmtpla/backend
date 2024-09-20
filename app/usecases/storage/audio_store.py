import os
import uuid
from fastapi import HTTPException
import requests
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
        public_url = minio_client.presigned_get_object(BUCKET_NAME, minio_file_name)
        print("New public url : ", public_url)
        return public_url

    except requests.RequestException as req_err:
        raise HTTPException(status_code=400, detail=f"Failed to download file from URL: {str(req_err)}")
    except S3Error as s3_err:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to MinIO: {str(s3_err)}")
    finally:
        # Clean up the local file
        if os.path.exists(local_file_path):
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