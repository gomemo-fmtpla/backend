import json
import time
import traceback
import os
import uuid
from datetime import datetime

from app.worker import celery_app
from app.database.db import DatabaseSingleton
from app.database.schemas.note import NoteCreate, NoteMetadataCreate
from app.usecases.note.note import add_note, add_metadata
from app.commons.pydantic_to_json import metadata_to_dict
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio, transcribe_audio_whisper_openai, transcribe_audio_salad, transcribe_audio_deepinfra
from app.usecases.generation.summary_generation import generate_summary

from redis import Redis
from app.config import settings

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL)


@celery_app.task(name="process_audio", bind=True)
def process_audio(self, audio_url, lang, context, user_id):
    # Log task start
    task_id = self.request.id
    print(f"!!!Starting process_audio task {task_id} for URL: {audio_url}")
    
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    redis_task_id = str(uuid.uuid4())
    redis_client.set(f"task:{task_id}:status", "PROCESSING")
    result = {"status": "error", "message": "Failed to process the task", "task_id": redis_task_id}
    
    try:
        # Transcribe audio
        print(f"Task {task_id}: Starting transcription")
        redis_client.set(f"task:{task_id}:status", "TRANSCRIBING")
        start_time = time.time()
        transcription_response = transcribe_audio_deepinfra(audio_url=audio_url)
        transcription_time = time.time() - start_time
        print(f"Task {task_id}: Transcription took {transcription_time:.2f} seconds")
        
        if not transcription_response['success']:
            error_details = transcription_response.get('error', {})
            print(f"Task {task_id}: Transcription failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to transcribe audio: {error_details}", "task_id": redis_task_id}
            
        transcript = transcription_response["data"]["transcript"]
        print(f"Task {task_id}: Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print(f"Task {task_id}: Starting summary generation")
        redis_client.set(f"task:{task_id}:status", "SUMMARIZING")
        start_time = time.time()
        summary_response = generate_summary(transcript, lang, context=context)
        summary_time = time.time() - start_time
        print(f"Task {task_id}: Summary generation took {summary_time:.2f} seconds")
        
        if not summary_response['success']:
            error_details = summary_response.get('error', {})
            print(f"Task {task_id}: Summary generation failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to generate summary: {error_details}", "task_id": redis_task_id}
            
        summary_data = summary_response['data']
        print(f"Task {task_id}: Summary generation successful")
        
        # Create note
        print(f"Task {task_id}: Creating note")
        redis_client.set(f"task:{task_id}:status", "CREATING_NOTE")
        
        # Create note
        note_create = NoteCreate(
            title=summary_data['title'],
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            content_url=audio_url,
        )
        
        new_note = add_note(
            db=db_session,
            user_id=user_id,
            folder_id=None,
            note_create=note_create
        )
        print(f"Task {task_id}: Note created with ID: {new_note.id}")
        
        # Add metadata
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
        result = {"status": "complete", "message": note_metadata_json, "task_id": redis_task_id}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Task {task_id}: Failed with error: {str(e)}")
        print(f"Task {task_id}: Traceback: {error_traceback}")
        redis_client.set(f"task:{task_id}:status", "FAILED")
        result = {"status": "error", "message": f"Process failed: {str(e)}", "traceback": error_traceback, "task_id": redis_task_id}
    
    finally:
        # Set expiry untuk task status
        redis_client.expire(f"task:{task_id}:status", 3600)  # 1 jam
        db_session.close()
        print(f"Task {task_id}: Finished with status: {result['status']}")
    
    return result


@celery_app.task(name="process_audio_whisper_openai", bind=True)
def process_audio_whisper_openai(self, audio_url, lang, context, user_id):
    # Log task start
    task_id = self.request.id
    print(f"Starting Audio Whisper task {task_id} for URL: {audio_url}")
    
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    redis_client.set(f"task:{task_id}:status", "PROCESSING")
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        # Transcribe audio
        print(f"Task {task_id}: Starting transcription with Whisper OpenAI")
        redis_client.set(f"task:{task_id}:status", "TRANSCRIBING")
        start_time = time.time()
        transcription_response = transcribe_audio_whisper_openai(audio_url=audio_url)
        transcription_time = time.time() - start_time
        print(f"Task {task_id}: Transcription took {transcription_time:.2f} seconds")
        
        if not transcription_response['success']:
            error_details = transcription_response.get('error', {})
            print(f"Task {task_id}: Transcription failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to transcribe audio: {error_details}"}
            
        transcript = transcription_response["data"]["transcript"]
        print(f"Task {task_id}: Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print(f"Task {task_id}: Starting summary generation")
        redis_client.set(f"task:{task_id}:status", "SUMMARIZING")
        start_time = time.time()
        summary_response = generate_summary(transcript, lang, context=context)
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
        
        # Create note
        note_create = NoteCreate(
            title=summary_data['title'],
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            content_url=audio_url,
        )
        
        new_note = add_note(
            db=db_session,
            user_id=user_id,
            folder_id=None,
            note_create=note_create
        )
        print(f"Task {task_id}: Note created with ID: {new_note.id}")
        
        # Add metadata
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
        result = {"status": "error", "message": f"Process failed on generate_audio_summary_2: {str(e)}", "traceback": error_traceback}
    
    finally:
        # Cleanup
        redis_client.expire(f"task:{task_id}:status", 3600)  # 1 jam
        db_session.close()
        print(f"Task {task_id}: Finished with status: {result['status']}")
    
    return result


@celery_app.task(name="process_audio_salad", bind=True)
def process_audio_salad(self, audio_url, lang, context, user_id):
    # Log task start
    task_id = self.request.id
    print(f"Starting Audio Salad task {task_id} for URL: {audio_url}")
    
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    redis_client.set(f"task:{task_id}:status", "PROCESSING")
    result = {"status": "error", "message": "Failed to process the task"}
    temp_audio_file = None
    
    try:
        # Transcribe audio
        print(f"Task {task_id}: Starting transcription with Audio Salad")
        redis_client.set(f"task:{task_id}:status", "TRANSCRIBING")
        start_time = time.time()
        transcription_response = transcribe_audio_salad(audio_url=audio_url)
        transcription_time = time.time() - start_time
        print(f"Task {task_id}: Transcription took {transcription_time:.2f} seconds")
        
        if not transcription_response['success']:
            error_details = transcription_response.get('error', {})
            print(f"Task {task_id}: Transcription failed: {error_details}")
            redis_client.set(f"task:{task_id}:status", "FAILED")
            return {"status": "error", "message": f"Failed to transcribe audio: {error_details}"}
            
        transcript = transcription_response["data"]["transcript"]
        print(f"Task {task_id}: Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print(f"Task {task_id}: Starting summary generation")
        redis_client.set(f"task:{task_id}:status", "SUMMARIZING")
        start_time = time.time()
        summary_response = generate_summary(transcript, lang, context=context)
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
        
        # Create note
        note_create = NoteCreate(
            title=summary_data['title'],
            summary=summary_data['markdown'],
            transcript_text=transcript,
            language=summary_data['lang'],
            content_url=audio_url,
        )
        
        new_note = add_note(
            db=db_session,
            user_id=user_id,
            folder_id=None,
            note_create=note_create
        )
        print(f"Task {task_id}: Note created with ID: {new_note.id}")
        
        # Add metadata
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
        result = {"status": "error", "message": f"Process failed on generate_audio_summary_3: {str(e)}", "traceback": error_traceback}
    
    finally:
        # Hapus file audio temporary jika ada
        if temp_audio_file and os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        
        # Cleanup
        redis_client.expire(f"task:{task_id}:status", 3600)  # 1 jam
        db_session.close()
        print(f"Task {task_id}: Finished with status: {result['status']}")
    
    return result 