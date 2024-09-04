# do it from youtube
# do it from audio record --> can be handled in the client side
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

from app.commons.environment_manager import load_env
from app.usecases.generation.audio_transcribe_extraction import transcribe_audio

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
        print("URL invalid")
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
            transcription_response = transcribe_audio(audio_url=youtube_url)
            if not transcription_response['success']:
                # print(transcription_response[])
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
            print(e)
            return {
                "success": False,
                "error": {
                    "type": "Error",
                    "message": str(e)
                }
            }