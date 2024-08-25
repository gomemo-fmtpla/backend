from app.commons.environment_manager import load_env
from openai import OpenAI
import os

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def transcribe_audio(audioPath : str) -> dict:
    """Transcribe an audio using OpenAI."""
    try:
        audio_file = open(audioPath, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
        
        print(transcription)

        return {
            "success": True,
            "data": {
                "transcript": transcription
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "TranslationError",
                "message": str(e)
            }
        }
