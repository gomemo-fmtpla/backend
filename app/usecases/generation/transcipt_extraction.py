# do it from youtube
# do it from audio record --> can be handled in the client side

# nice to have -> from pdf
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

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
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return {
            "success": True,
            "data": {
                "video_id": video_id,
                "transcript": transcript_text
            },
            "error": None
        }
    except YouTubeTranscriptApi.CouldNotRetrieveTranscript as e:
        return {
            "success": False,
            "error": {
                "type": "TranscriptUnavailable",
                "message": "Transcript could not be retrieved. The video might not have subtitles."
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "UnknownError",
                "message": str(e)
            }
        }
