import unittest
from unittest.mock import MagicMock, patch

import requests

from app.config import settings
from app.usecases.generation.whisperx_client import (
    get_whisperx_transcribe_audio_url,
    get_whisperx_transcribe_url,
    post_whisperx_transcription,
)


class TestWhisperxClient(unittest.TestCase):
  def test_get_whisperx_transcribe_url(self):
    with patch.object(settings, "WHISPERX_BASE_URL", "https://example.workers.dev"):
      self.assertEqual(
        get_whisperx_transcribe_url(),
        "https://example.workers.dev/transcribe/",
      )

  def test_get_whisperx_transcribe_audio_url(self):
    with patch.object(settings, "WHISPERX_BASE_URL", "https://example.workers.dev/"):
      self.assertEqual(
        get_whisperx_transcribe_audio_url(),
        "https://example.workers.dev/transcribe-audio/",
      )

  @patch("app.usecases.generation.whisperx_client.requests.post")
  def test_post_whisperx_transcription_success(self, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"transcription": "hello world"}
    mock_post.return_value = mock_response

    result = post_whisperx_transcription(
      "https://example.workers.dev/transcribe/",
      {"url": "https://youtube.com/watch?v=abc", "language": "en"},
    )

    self.assertTrue(result["success"])
    self.assertEqual(result["data"]["transcription"], "hello world")
    mock_post.assert_called_once()

  @patch("app.usecases.generation.whisperx_client.requests.post")
  def test_post_whisperx_transcription_error_payload(self, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
      "transcription": "Error downloading audio: blocked",
    }
    mock_post.return_value = mock_response

    result = post_whisperx_transcription(
      "https://example.workers.dev/transcribe/",
      {"url": "https://youtube.com/watch?v=abc"},
    )

    self.assertFalse(result["success"])
    self.assertEqual(result["error"]["type"], "TranscriptionError")

  @patch("app.usecases.generation.whisperx_client.requests.post")
  def test_post_whisperx_transcription_request_error(self, mock_post):
    mock_post.side_effect = requests.exceptions.Timeout("timed out")

    result = post_whisperx_transcription(
      "https://example.workers.dev/transcribe/",
      {"url": "https://youtube.com/watch?v=abc"},
    )

    self.assertFalse(result["success"])
    self.assertEqual(result["error"]["type"], "TranscriptionError")


class TestGenerateTranscriptRouting(unittest.TestCase):
  @patch("app.usecases.generation.youtube_transcript_extraction.post_whisperx_transcription")
  @patch("app.usecases.generation.youtube_transcript_extraction.get_whisperx_transcribe_url")
  def test_generate_transcript_uses_configured_base_url(
    self,
    mock_get_url,
    mock_post,
  ):
    from app.usecases.generation.youtube_transcript_extraction import generate_transcript

    mock_get_url.return_value = "https://example.workers.dev/transcribe/"
    mock_post.return_value = {
      "success": True,
      "data": {"transcription": "sample transcript"},
      "error": None,
    }

    result = generate_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "en")

    self.assertTrue(result["success"])
    self.assertEqual(result["data"]["transcript"], "sample transcript")
    mock_post.assert_called_once_with(
      "https://example.workers.dev/transcribe/",
      {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "language": "en",
      },
      timeout=3600,
    )


if __name__ == "__main__":
  unittest.main()
