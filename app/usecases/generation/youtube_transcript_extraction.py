import json
import os
import ssl
import sys
import traceback
import requests
import tempfile
from openai import OpenAI
from pytubefix import YouTube
from pytubefix.captions import Caption
from pytubefix.cli import on_progress
from urllib.parse import urlparse, parse_qs
from app.commons.environment_manager import load_env

ssl._create_default_https_context = ssl._create_stdlib_context
load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    return None

def generate_transcript(youtube_url):
    video_id = get_video_id(youtube_url)
    if not video_id:
        return {
            "success": False,
            "error": {
                "type": "InvalidURL",
                "message": "The provided YouTube URL is invalid."
            }
        }
    
    try:
        url = "https://whisperx-green-smoke-3819.fly.dev/transcribe/"
        
        payload = json.dumps({
            "url": youtube_url
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload, timeout=3600)
        
        if response.status_code == 200:
            transcription_data = response.json()
            print(f"transcription_data: {transcription_data}")
            return {
                "success": True,
                "data": {
                    "video_id": video_id,
                    "transcript": transcription_data["transcription"]
                },
                "error": None
            }
    except Exception as e:
        print(f"Error on generate_transcript: {str(e)}.")
        return {
                "success": False,
                "error": {
                    "type": "TranscriptionError",
                    "message": str(e)
                }
            }

def generate_transcript_with_deepinfra(youtube_url):
    video_id = get_video_id(youtube_url)
    if not video_id:
        return {
            "success": False,
            "error": {
                "type": "InvalidURL",
                "message": "The provided YouTube URL is invalid."
            }
        }
    
    out_file = None
    try:
        print(f"!!!start generate_transcript_with_deepinfra")
        sys.stdout.flush()
        
        # Download the audio from YouTube
        yt = YouTube(youtube_url, on_progress_callback=on_progress, use_oauth=True, allow_oauth_cache=True)
        print(f"Video Title: {yt.title}")
        sys.stdout.flush()
        
        ys = yt.streams.get_audio_only()
        
        # Create a temporary file with a more reliable approach
        temp_dir = tempfile.mkdtemp()
        out_file = os.path.join(temp_dir, f"{video_id}.mp3")
        
        print(f"Downloading to: {out_file}")
        ys.download(output_path=temp_dir, filename=f"{video_id}.mp3")
        print(f"Download complete")
        sys.stdout.flush()
        
        # Verify file exists and has content
        if not os.path.exists(out_file):
            raise FileNotFoundError(f"Downloaded file not found at {out_file}")
            
        file_size = os.path.getsize(out_file)
        print(f"File size: {file_size} bytes")
        if file_size == 0:
            raise ValueError("Downloaded file is empty")
        
        # Create transcription request to DeepInfra
        deepinfra_url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3-turbo"
        headers = {
            "Authorization": f"bearer {os.getenv('DEEPINFRA_API_KEY')}"
        }
        
        # Send the file for transcription with improved error handling
        with open(out_file, 'rb') as audio_file:
            file_content = audio_file.read()  # Read file content into memory
            
        files = {'audio': (f"{video_id}.mp3", file_content, 'audio/mpeg')}
        response = requests.post(deepinfra_url, headers=headers, files=files, timeout=300)
        
        # Check response
        response.raise_for_status()
        result = response.json()
        
        print(f"!!!result: {result}")
        sys.stdout.flush()
        
        # Clean up the temporary files
        if os.path.exists(out_file):
            os.remove(out_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        # Extract the transcript from the response
        transcription = result.get("text", "")
        
        if not transcription:
            raise ValueError("No transcription returned from DeepInfra API")
        
        return {
            "success": True,
            "data": {
                "video_id": video_id,
                "transcript": transcription
            },
            "error": None
        }

    except Exception as e:
        # Clean up in case of an error
        if out_file and os.path.exists(out_file):
            try:
                os.remove(out_file)
            except:
                pass
            
        # Try to remove temp directory if it exists
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
        print(f"Error on generate_transcript_with_deepinfra: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.stdout.flush()
        
        return {
            "success": False,
            "error": {
                "type": "TranscriptionError",
                "message": str(e)
            }
        }
    
        
def generate_youtube_transcript(youtube_url):
    video_id = get_video_id(youtube_url)
    if not video_id:
        return {
            "success": False,
            "error": {
                "type": "InvalidURL",
                "message": "The provided YouTube URL is invalid."
            }
        }

    try:
        subtitles = get_srt(youtube_url)
        print(subtitles)
        
        return {
            "success": True,
            "data": {
                "video_id": video_id,
                "transcript": subtitles
            },
            "error": None
        }
    except Exception as e:
        try :
            print("perform failover")
            transcription_response = transcript_with_whisper(youtube_url=youtube_url)
            if not transcription_response['success']:
                print(transcription_response['error']['message'])
                raise Exception(f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n")
            
            transcript = transcription_response['data']['transcript']
            print(transcript)
            return {
                "success": True,
                "data": {
                    "video_id": video_id,
                    "transcript": transcript
                },
                "error": None
            }
        except Exception as e :
            print(e)
            return {
                "success": False,
                "error": {
                    "type": "Error",
                    "message": str(e)
                }
        }

def transcript_with_whisper(youtube_url: str):
    out_file = None  # Initialize the variable here
    try:
        # Download the audio from YouTube as an MP3 file 
        yt = YouTube(youtube_url, on_progress_callback=on_progress, use_oauth=True, allow_oauth_cache=True)
        
        print(f"Video Title: {yt.title}")
         
        ys = yt.streams.get_audio_only()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
            out_file = temp.name

        ys.download(filename=out_file)

        print(f"Temporary file: {out_file}")
        
        # Open the file in binary read mode
        with open(out_file, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up the temporary file
        os.unlink(out_file)

        # # Clean up the temporary file
        # os.remove(out_file)

        return {
            "success": True,
            "data": {
                "transcript": transcription
            },
            "error": None
        }

    except Exception as e:
        # Clean up in case of an error
        if out_file and os.path.exists(out_file):
            os.remove(out_file)
            
        return {
            "success": False,
            "error": {
                "type": "Error",
                "message": str(e)
            }
        }
    
def get_srt(url, lang='en'):
    video = YouTube(url)
    captions = video.captions.get(lang)

    # If no captions are found in the desired language, check for ASR captions
    if not captions:
        for c in video.captions:
            params = parse_qs(urlparse(c.url).query)
            asr_lang = params.get('asr_langs')
            if asr_lang and lang in asr_lang[0].split(','):
                captions = Caption({
                    'baseUrl': f'{c.url}&tlang={lang}',
                    'languageCode': lang,
                    'name': {'simpleText': 'ASR'}
                })
                break

    # If still no captions, raise an error
    if not captions:
        raise KeyError("Captions not found.")

    # Get the SRT captions
    srt_captions = captions.generate_srt_captions()

    # Parse the SRT format to extract only the text, skipping index and timestamp lines
    paragraphs = []
    for line in srt_captions.splitlines():
        # Ignore lines with index numbers and timestamps
        if line.isdigit() or "-->" in line:
            continue
        if line.strip():  # Add non-empty lines to paragraphs
            paragraphs.append(line.strip())

    # Join the extracted text lines into a single paragraph
    full_text = " ".join(paragraphs)

    return full_text