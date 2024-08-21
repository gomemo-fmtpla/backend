from app.database.models import User
from app.usecases.auth_guard import auth_guard
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.usecases.misc.summary_generation_vertex import generate_summary_vertex
from app.usecases.generation.summary_generation import generate_summary
from app.usecases.generation.transcipt_extraction import generate_transcript

router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)

class YouTubeSummaryRequest(BaseModel):
    youtube_url: str

class AudioSummaryRequest(BaseModel):
    transcript: str

async def youtube_summary(
    request: YouTubeSummaryRequest,
    current_user: User = Depends(auth_guard)
):
    user_id = current_user.id
    transcript_response = generate_transcript(request.youtube_url)
    if not transcript_response['success']:
        raise HTTPException(status_code=400, detail=transcript_response['error'])

    transcript = transcript_response['data']['transcript']
    print(transcript)
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])

    return summary_response

@router.post("/audio/")
async def audio_summary(request: AudioSummaryRequest):
    transcript = request.transcript
    summary_response = generate_summary(transcript)
    if not summary_response['success']:
        raise HTTPException(status_code=500, detail=summary_response['error'])

    return summary_response
