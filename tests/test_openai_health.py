from unittest.mock import MagicMock, patch

from app.services.openai_health import OpenAIHealthStatus, check_openai_health


def test_missing_api_key():
    with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
        result = check_openai_health()
    assert result.status == OpenAIHealthStatus.MISSING_KEY


def test_invalid_api_key():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
        with patch("app.services.openai_health.OpenAI") as mock_openai:
            client = MagicMock()
            mock_openai.return_value = client
            from openai import AuthenticationError

            client.models.list.side_effect = AuthenticationError("invalid", response=MagicMock(), body={})
            result = check_openai_health()
    assert result.status == OpenAIHealthStatus.INVALID_KEY


def test_quota_exhausted():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
        with patch("app.services.openai_health.OpenAI") as mock_openai:
            client = MagicMock()
            mock_openai.return_value = client
            client.models.list.return_value = MagicMock()
            from openai import RateLimitError

            client.chat.completions.create.side_effect = RateLimitError(
                "quota",
                response=MagicMock(),
                body={"error": {"code": "insufficient_quota", "message": "exhausted"}},
            )
            result = check_openai_health()
    assert result.status == OpenAIHealthStatus.QUOTA_EXHAUSTED


def test_healthy():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
        with patch("app.services.openai_health.OpenAI") as mock_openai:
            client = MagicMock()
            mock_openai.return_value = client
            client.models.list.return_value = MagicMock()
            client.chat.completions.create.return_value = MagicMock()
            result = check_openai_health()
    assert result.status == OpenAIHealthStatus.OK
