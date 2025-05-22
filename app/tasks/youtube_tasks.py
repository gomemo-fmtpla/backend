import json
import time
import traceback
from datetime import datetime

from app.worker import celery_app
from app.database.db import DatabaseSingleton
from app.database.schemas.note import NoteCreate, NoteMetadataCreate
from app.usecases.note.note import add_note, add_metadata
from app.commons.pydantic_to_json import metadata_to_dict
from app.usecases.generation.youtube_transcript_extraction import generate_transcript, generate_transcript_with_deepinfra, generate_youtube_transcript
from app.usecases.generation.summary_generation import generate_summary

from redis import Redis
from app.config import settings

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL)


@celery_app.task(name="process_youtube_video", bind=True)
def process_youtube_video(self, youtube_url, lang, user_id):
    # Log task start
    task_id = self.request.id
    print(f"Starting YouTube task {task_id} for URL: {youtube_url}")
    
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        # Update Redis status
        redis_client.set(f"task:{task_id}:status", "STARTED")
        
        # Transcribe Youtube Video
        print(f"Task {task_id}: Starting transcription")
        redis_client.set(f"task:{task_id}:status", "TRANSCRIBING")
        start_time = time.time()
        transcript_response = generate_transcript_with_deepinfra(youtube_url)
        transcription_time = time.time() - start_time
        print(f"Task {task_id}: Transcription took {transcription_time:.2f} seconds")
        
        if not transcript_response['success']:
            error_details = transcript_response.get('error', {})
            print(f"Task {task_id}: Transcription failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to transcribe the YouTube video: {error_details}"}
            
        transcript = transcript_response['data']['transcript']
        print(f"Task {task_id}: Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print(f"Task {task_id}: Starting summary generation")
        redis_client.set(f"task:{task_id}:status", "SUMMARIZING")
        start_time = time.time()
        summary_response = generate_summary(transcript, lang)
        summary_time = time.time() - start_time
        print(f"Task {task_id}: Summary generation took {summary_time:.2f} seconds")
        
        if not summary_response['success']:
            error_details = summary_response.get('error', {})
            print(f"Task {task_id}: Summary generation failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to generate summary: {error_details}"}
            
        summary_data = summary_response['data']
        print(f"Task {task_id}: Summary generation successful")
        
        # Create note
        print(f"Task {task_id}: Creating note")
        redis_client.set(f"task:{task_id}:status", "CREATING_NOTE")
        
        # Buat note
        note_create = NoteCreate(
            title=summary_data['title'],
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            content_url=youtube_url,
        )
        
        new_note = add_note(
            db=db_session,
            user_id=user_id,
            folder_id=None,
            note_create=note_create
        )
        print(f"Task {task_id}: Note created with ID: {new_note.id}")
        
        # Tambahkan metadata
        metadata_create = NoteMetadataCreate(
            title=summary_data['title'],
            content_category=summary_data['content_category'],
            emoji_representation=summary_data['emoji_representation'],
            date_created=datetime.now()
        )
        
        note_metadata = add_metadata(
            db=db_session,
            user_id=user_id,
            note_id=new_note.id,
            metadata_create=metadata_create
        )
        
        note_metadata_json = metadata_to_dict(note_metadata)
        print(f"Task {task_id}: Completed successfully")
        redis_client.set(f"task:{task_id}:status", "COMPLETE")
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Task {task_id}: Failed with error: {str(e)}")
        print(f"Task {task_id}: Traceback: {error_traceback}")
        redis_client.set(f"task:{task_id}:status", "FAILED")
        result = {"status": "error", "message": f"Process failed: {str(e)}", "traceback": error_traceback}
    
    finally:
        # Cleanup
        redis_client.expire(f"task:{task_id}:status", 3600)  # 1 jam expiry
        db_session.close()
        print(f"Task {task_id}: Finished with status: {result['status']}")
    
    return result


@celery_app.task(name="process_youtube_video_2", bind=True)
def process_youtube_video_2(self, youtube_url, transcript, lang, user_id):
    # Log task start
    task_id = self.request.id
    print(f"Starting YouTube task 2 {task_id} for URL: {youtube_url}")
    
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        # Update Redis status
        redis_client.set(f"task:{task_id}:status", "STARTED")
        print(f"Task {task_id}: Starting transcription")
        
        # Transcribe Youtube Video
        transcription_response = generate_youtube_transcript(youtube_url=youtube_url)
        if not transcription_response['success']:
            print(f"Task {task_id}: Transcription failed: {transcription_response.get('error')}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": "Failed to transcribe audio"}
            
        transcript = transcription_response["data"]["transcript"]
        print(f"Task {task_id}: Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print(f"Task {task_id}: Starting summary generation")
        redis_client.set(f"task:{task_id}:status", "SUMMARIZING")
        summary_response = generate_summary(transcript, lang)
        if not summary_response['success']:
            print(f"Task {task_id}: Summary generation failed: {summary_response.get('error')}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to generate summary"}
            
        summary_data = summary_response['data']
        print(f"Task {task_id}: Summary generation successful")
        
        # Create note
        print(f"Task {task_id}: Creating note")
        redis_client.set(f"task:{task_id}:status", "CREATING_NOTE")
        
        # Buat note
        note_create = NoteCreate(
            title=summary_data['title'],
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            content_url=youtube_url,
        )
        
        new_note = add_note(
            db=db_session,
            user_id=user_id,
            folder_id=None,
            note_create=note_create
        )
        print(f"Task {task_id}: Note created with ID: {new_note.id}")
        
        # Tambahkan metadata
        metadata_create = NoteMetadataCreate(
            title=summary_data['title'],
            content_category=summary_data['content_category'],
            emoji_representation=summary_data['emoji_representation'],
            date_created=datetime.now()
        )
        
        note_metadata = add_metadata(
            db=db_session,
            user_id=user_id,
            note_id=new_note.id,
            metadata_create=metadata_create
        )
        
        note_metadata_json = metadata_to_dict(note_metadata)
        print(f"Task {task_id}: Completed successfully")
        redis_client.set(f"task:{task_id}:status", "COMPLETE")
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Task {task_id}: Failed with error: {str(e)}")
        print(f"Task {task_id}: Traceback: {error_traceback}")
        redis_client.set(f"task:{task_id}:status", "FAILED")
        result = {"status": "error", "message": f"Process failed on generate_youtube_summary_2: {str(e)}", "traceback": error_traceback}
    
    finally:
        # Cleanup
        redis_client.expire(f"task:{task_id}:status", 3600)  # 1 jam expiry
        db_session.close()
        print(f"Task {task_id}: Finished with status: {result['status']}")
    
    return result 