import os

import psutil
from app.database.models import User
from app.usecases.auth_guard import auth_guard
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.usecases.generation.summary_generation import generate_summary
from app.usecases.generation.transcript_extraction import generate_transcript, transcript_with_whisper_local

router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)

class YouTubeSummaryRequest(BaseModel):
    youtube_url: str
    video_lang: str

class AudioSummaryRequest(BaseModel):
    transcript: str

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"RSS: {mem_info.rss / 1024 ** 2:.2f} MB, VMS: {mem_info.vms / 1024 ** 2:.2f} MB")

# Define a request body model
class YouTubeURLRequest(BaseModel):
    youtube_url: str

@router.post("/whisper/")
async def testing_audio(request: YouTubeURLRequest):
    log_memory_usage()  
    
    youtube_url = request.youtube_url
    
    # Call the transcript_with_whisper function
    try:
        result = transcript_with_whisper_local(youtube_url)
        
        # Check if transcription was successful
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error']['message'])

        return {
            "success": True,
            "transcript": result['data']['transcript']
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to process the audio: {str(e)}")
 

@router.post("/youtube/")
async def youtube_summary(
    request: YouTubeSummaryRequest
):
    transcript_response = generate_transcript(request.youtube_url, video_lang=request.video_lang)
    if not transcript_response['success']:
        raise HTTPException(status_code=400, detail=transcript_response['error'])

    transcript = transcript_response['data']['transcript']
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])

    return summary_response

@router.post("/audio/")
async def audio_summary(
    request: AudioSummaryRequest,
    current_user: User = Depends(auth_guard)  # Authentication applied
):
    transcript = request.transcript
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])

    return summary_response