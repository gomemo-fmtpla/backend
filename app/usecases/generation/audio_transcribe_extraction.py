import ssl
from click import File
from app.commons.environment_manager import load_env
from openai import OpenAI
import os
import requests
import json

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def transcribe_audio(audio_url: str) -> dict:
    """Transcribe an audio file using OpenAI, downloading it first to a static temporary file."""
    try:
        print(audio_url)
        
        # Send a GET request to the URL
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()  # Check for request errors
        
        # Extract the filename from the URL
        temp_audio_file = audio_url.split("/")[-1].split("?")[0]
        # print_audio_info(temp_audio_file)

        # Save the file locally
        with open(temp_audio_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        # Open the temporary file for transcription
        with open(temp_audio_file, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        # Clean up the temporary file
        os.remove(temp_audio_file)

        return {
            "success": True,
            "data": {
                "transcript": transcription
            },
            "error": None
        }

    except Exception as e:
        # Clean up in case of an error
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

        print("Error when transcribing content", e)
        return {
            "success": False,
            "error": {
                "type": "TranslationError",
                "message": str(e)
            }
        }
        
def transcribe_audio_local(audio_url: str) -> dict:
    # """Transcribe an audio file using the local Whisper model, downloading it first to a static temporary file."""
    url = "https://mustard-cayenne-0hlavnqk8jx0kp7z.salad.cloud/transcribe-audio/"

    payload = json.dumps({
        "url": audio_url
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            transcription_data = response.json()
            return {
                "success": True,
                "data": {
                    "transcript": transcription_data["transcription"]
                },
                "error": None
            }
        else:
            return {
                "success": False,
                "error": {
                    "type": "TranscriptionError",
                    "message": "Failed to get transcription from the server."
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": str(e)
            }
        }

# def transcribe_audio_local(audio_url: str) -> dict:
#     """Transcribe an audio file using the local Whisper model, downloading it first to a static temporary file."""
#     temp_audio_file = None
#     try:
#         print(f"Downloading audio from URL: {audio_url}")

#         # Send a GET request to the URL
#         response = requests.get(audio_url, stream=True)
#         response.raise_for_status()  # Check for request errors

#         # Extract the filename from the URL
#         temp_audio_file = audio_url.split("/")[-1].split("?")[0]
        
#         # Save the file locally
#         with open(temp_audio_file, "wb") as file:
#             for chunk in response.iter_content(chunk_size=8192):
#                 if chunk:
#                     file.write(chunk)

#         # Print audio information (optional, for debugging)
#         print_audio_info(temp_audio_file)
        
#         result = model.transcribe(audio=f"{temp_audio_file}")

#         # # Load and process the audio using Whisper
#         # audio = whisper.load_audio(temp_audio_file)
#         # audio = whisper.pad_or_trim(audio)

#         # # Make log-Mel spectrogram and move it to the device where the model is loaded
#         # mel = whisper.log_mel_spectrogram(audio).to(model.device)

#         # # Decode the audio using Whisper's built-in options
#         # options = whisper.DecodingOptions()
#         # result = whisper.decode(model, mel, options)

#         # Clean up the temporary file after transcription
#         os.remove(temp_audio_file)

#         return {
#             "success": True,
#             "data": {
#                 "transcript": result['text']
#             },
#             "error": None
#         }

#     except Exception as e:
#         # Clean up in case of an error
#         if temp_audio_file and os.path.exists(temp_audio_file):
#             os.remove(temp_audio_file)

#         print(f"Error when transcribing content: {e}")
#         return {
#             "success": False,
#             "error": {
#                 "type": "TranscriptionError",
#                 "message": str(e)
#             }
#         }

def print_audio_info(file_path: str):
    """Print information about the audio file."""
    try:
        # Load the audio file
        audio = File(file_path)
        
        if audio is None:
            print(f"Unable to read audio file: {file_path}")
            return
        
        # Print basic file information
        print(f"File: {file_path}")
        print(f"Format: {audio.mime}")
        
        # Print audio-specific information if available
        if hasattr(audio, 'info'):
            info = audio.info
            print(f"Duration: {info.length} seconds")
            print(f"Sample Rate: {info.sample_rate} Hz")
            print(f"Channels: {info.channels}")
        else:
            print("No detailed audio info available.")
    
    except Exception as e:
        print(f"Error reading audio file info: {str(e)}")