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

def put_note_object(file_path: str, file_name: str) -> str:
    try:
        # Verify the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="File does not exist")

        # Upload the file to MinIO
        minio_client.fput_object(
            BUCKET_NAME,
            file_name,
            file_path
        )

        # Generate public URL for the file
        public_url = f"{MINIO_ENDPOINTS}/{BUCKET_NAME}/{file_name}"
        print("New public url : ", public_url)
        return public_url

    except S3Error as s3_err:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to MinIO: {str(s3_err)}")
    
def delete_note_object(file_name: str):
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