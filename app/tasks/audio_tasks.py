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
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio, transcribe_audio_whisper_openai, transcribe_audio_salad
from app.usecases.generation.summary_generation import generate_summary

from redis import Redis
from app.config import settings

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL)


@celery_app.task(name="process_audio")
def process_audio(audio_url, lang, context, user_id):
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    task_id = str(uuid.uuid4())
    redis_client.set(f"task_status:{task_id}", "PROCESSING")
    result = {"status": "error", "message": "Failed to process the task", "task_id": task_id}
    
    try:
        # Transcribe audio
        redis_client.set(f"task_status:{task_id}", "TRANSCRIBING")
        transcription_response = transcribe_audio(audio_url=audio_url)
        
        if not transcription_response['success']:
            redis_client.set(f"task_status:{task_id}", "FAILED")
            return {"status": "error", "message": "Failed to transcribe audio", "task_id": task_id}
            
        transcript = transcription_response["data"]["transcript"]
        
        # Generate summary
        redis_client.set(f"task_status:{task_id}", "SUMMARIZING")
        summary_response = generate_summary(transcript, lang, context=context)
        
        if not summary_response['success']:
            redis_client.set(f"task_status:{task_id}", "FAILED")
            return {"status": "error", "message": "Failed to generate summary", "task_id": task_id}
            
        summary_data = summary_response['data']
        
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
        redis_client.set(f"task_status:{task_id}", "COMPLETE")
        result = {"status": "complete", "message": note_metadata_json, "task_id": task_id}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        redis_client.set(f"task_status:{task_id}", "FAILED")
        result = {"status": "error", "message": f"Process failed: {str(e)}", "traceback": error_traceback, "task_id": task_id}
    
    finally:
        # Set expiry untuk task status
        redis_client.expire(f"task_status:{task_id}", 3600)  # 1 jam
        db_session.close()
    
    return result


@celery_app.task(name="process_audio_whisper_openai")
def process_audio_whisper_openai(audio_url, lang, context, user_id):
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        # Transcribe audio
        transcription_response = transcribe_audio_whisper_openai(audio_url=audio_url)
        
        if not transcription_response['success']:
            return {"status": "error", "message": "Failed to transcribe audio"}
            
        transcript = transcription_response["data"]["transcript"]
        
        # Generate summary
        summary_response = generate_summary(transcript, lang, context=context)
        
        if not summary_response['success']:
            return {"status": "error", "message": "Failed to generate summary"}
            
        summary_data = summary_response['data']
        
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
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {"status": "error", "message": f"Process failed on generate_audio_summary_2: {str(e)}", "traceback": error_traceback}
    
    finally:
        db_session.close()
    
    return result


@celery_app.task(name="process_audio_salad")
def process_audio_salad(audio_url, lang, context, user_id):
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    result = {"status": "error", "message": "Failed to process the task"}
    temp_audio_file = None
    
    try:
        # Transcribe audio
        transcription_response = transcribe_audio_salad(audio_url=audio_url)
        
        if not transcription_response['success']:
            return {"status": "error", "message": "Failed to transcribe audio"}
            
        transcript = transcription_response["data"]["transcript"]
        
        # Generate summary
        summary_response = generate_summary(transcript, lang, context=context)
        
        if not summary_response['success']:
            return {"status": "error", "message": "Failed to generate summary"}
            
        summary_data = summary_response['data']
        
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
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {"status": "error", "message": f"Process failed on generate_audio_summary_3: {str(e)}", "traceback": error_traceback}
    
    finally:
        # Hapus file audio temporary jika ada
        if temp_audio_file and os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        db_session.close()
    
    return result 