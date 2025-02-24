from app.tasks.audio_queue import celery_app
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio
from app.usecases.generation.summary_generation import generate_summary

@celery_app.task(name="process_audio_transcription")
def process_audio_transcription(audio_url: str):
    return transcribe_audio(audio_url=audio_url)

@celery_app.task(name="process_audio_summary") 
def process_audio_summary(transcript: str, lang: str, context: str):
    return generate_summary(transcript, lang, context=context)
