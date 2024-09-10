import os

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tempfile
