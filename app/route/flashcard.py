from app.usecases.generation.transcipt_extraction import generate_transcript
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.usecases.generation.flashcard_generation import generate_flashcards

router = APIRouter(
    prefix="/flashcard",
    tags=["flashcard"],
)

class FlashcardRequest(BaseModel):
    transcript: str

@router.post("/")
async def generate_flashcard(request: FlashcardRequest):
    # check first if it already generated
    yt = request.transcript
    transcript_response = generate_transcript(yt)
    if not transcript_response['success']:
        raise HTTPException(status_code=400, detail=transcript_response['error'])

    transcript = transcript_response['data']['transcript']
    # print(transcript)
    
    # transcript = request.transcript
    response = generate_flashcards(transcript)
    if not response['success']:
        raise HTTPException(status_code=500, detail=response['error'])

    return response
