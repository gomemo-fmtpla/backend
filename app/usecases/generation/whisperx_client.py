import json
from urllib.parse import urljoin

import requests

from app.config import settings


def get_whisperx_transcribe_url() -> str:
    base = settings.WHISPERX_BASE_URL.rstrip("/") + "/"
    return urljoin(base, "transcribe/")


def get_whisperx_transcribe_audio_url() -> str:
    base = settings.WHISPERX_BASE_URL.rstrip("/") + "/"
    return urljoin(base, "transcribe-audio/")


def post_whisperx_transcription(
    endpoint_url: str,
    payload: dict,
    timeout: int = 3600,
) -> dict:
    try:
        response = requests.post(
            endpoint_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": str(exc),
            },
        }

    if response.status_code != 200:
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": f"WhisperX service returned HTTP {response.status_code}",
            },
        }

    try:
        transcription_data = response.json()
    except ValueError:
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": "WhisperX service returned invalid JSON",
            },
        }

    transcription = transcription_data.get("transcription", "")
    if not transcription or str(transcription).startswith("Error"):
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": str(transcription) or "Empty transcription",
            },
        }

    return {
        "success": True,
        "data": {"transcription": transcription},
        "error": None,
    }
