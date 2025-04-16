import json
import time
import traceback
from datetime import datetime

from app.worker import celery_app
from app.database.db import DatabaseSingleton
from app.database.schemas.note import NoteCreate, NoteMetadataCreate
from app.usecases.note.note import add_note, add_metadata
from app.commons.pydantic_to_json import metadata_to_dict
from app.usecases.generation.youtube_transcript_extraction import generate_transcript, generate_youtube_transcript
from app.usecases.generation.summary_generation import generate_summary


@celery_app.task(name="process_youtube_video")
def process_youtube_video(youtube_url, lang, user_id):
    # Buat session baru untuk tugas ini
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    task_updates = []
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        task_updates.append({"status": "progress", "message": "Generating transcript..."})
        
        # Transcribe Youtube Video
        start_time = time.time()
        transcript_response = generate_transcript(youtube_url)
        transcription_time = time.time() - start_time
        
        if not transcript_response['success']:
            error_details = transcript_response.get('error', {})
            return {"status": "error", "message": f"Failed to transcribe the YouTube video: {error_details}"}
            
        transcript = transcript_response['data']['transcript']
        task_updates.append({"status": "progress", "message": "Generating summary..."})
        
        # Generate summary
        start_time = time.time()
        summary_response = generate_summary(transcript, lang)
        
        if not summary_response['success']:
            error_details = summary_response.get('error', {})
            return {"status": "error", "message": f"Failed to generate summary: {error_details}"}
            
        summary_data = summary_response['data']
        task_updates.append({"status": "progress", "message": "Creating note..."})
        
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
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {"status": "error", "message": f"Process failed: {str(e)}", "traceback": error_traceback}
    
    finally:
        db_session.close()
    
    return result


@celery_app.task(name="process_youtube_video_2")
def process_youtube_video_2(youtube_url, transcript, lang, user_id):
    db_session = DatabaseSingleton.getInstance().SessionLocal()
    task_updates = []
    result = {"status": "error", "message": "Failed to process the task"}
    
    try:
        task_updates.append({"status": "progress", "message": "Transcribing audio..."})
        
        # Transcribe Youtube Video
        transcription_response = generate_youtube_transcript(youtube_url=youtube_url)
        if not transcription_response['success']:
            return {"status": "error", "message": "Failed to transcribe audio"}
            
        transcript = transcription_response["data"]["transcript"]
        task_updates.append({"status": "progress", "message": "Generating summary..."})
        
        # Generate summary
        summary_response = generate_summary(transcript, lang)
        if not summary_response['success']:
            return {"status": "error", "message": f"Failed to generate summary"}
            
        summary_data = summary_response['data']
        task_updates.append({"status": "progress", "message": "Creating note..."})
        
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
        result = {"status": "complete", "message": note_metadata_json}
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {"status": "error", "message": f"Process failed on generate_youtube_summary_2: {str(e)}", "traceback": error_traceback}
    
    finally:
        db_session.close()
    
    return result 