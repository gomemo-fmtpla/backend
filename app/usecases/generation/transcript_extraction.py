# do it from youtube
# do it from audio record --> can be handled in the client side
import json
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import pytube as pt
from app.commons.environment_manager import load_env
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
load_env()

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
        print(video_id)
        proxy = os.getenv("PROXY_URL")
        print("using proxy ", proxy)
        transcript = YouTubeTranscriptApi.get_transcript(video_id=video_id, proxies=proxy)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return {
            "success": True,
            "data": {
                "video_id": video_id,
                "transcript": transcript_text
            },
            "error": None
        }
    except Exception as e:
        try :
            print("perform failover")
            transcription_response = transcript_with_whisper(youtube_url=youtube_url)
            if not transcription_response['success']:
                print(transcription_responsep['error']['message'])
                raise Exception(f"data: {json.dumps({'status': 'error', 'message': 'Failed to transcribe audio'})}\n\n")
            
            transcript = transcription_response['data']['transcript']
            return {
                "success": True,
                "data": {
                    "video_id": video_id,
                    "transcript": transcript
                },
                "error": None
            }
        except Exception as e :
            return {
                "success": False,
                "error": {
                    "type": "Error",
                    "message": str(e)
                }
        }

def transcript_with_whisper(youtube_url: str):
    try:
        # Download the audio from YouTube as an MP3 file
        yt = pt.YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        temp_audio_file = "temp.mp3"
        stream.download(filename=temp_audio_file)
        
        # Transcribe the audio using Whisper
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
            
        return {
            "success": False,
            "error": {
                "type": "Error",
                "message": str(e)
            }
        }
