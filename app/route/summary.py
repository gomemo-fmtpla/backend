from app.database.models import User
from app.usecases.auth_guard import auth_guard
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.usecases.generation.summary_generation import generate_summary
from app.usecases.generation.transcript_extraction import generate_transcript

router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)

class YouTubeSummaryRequest(BaseModel):
    youtube_url: str
    video_lang: str

class AudioSummaryRequest(BaseModel):
    transcript: str

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