from dataclasses import dataclass
from enum import Enum
import os

from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError


class OpenAIHealthStatus(str, Enum):
    OK = "ok"
    MISSING_KEY = "missing_key"
    INVALID_KEY = "invalid_key"
    QUOTA_EXHAUSTED = "quota_exhausted"
    ERROR = "error"


@dataclass(frozen=True)
class OpenAIHealthResult:
    status: OpenAIHealthStatus
    message: str


def _quota_exhausted_from_error(exc: RateLimitError) -> bool:
    body = getattr(exc, "body", None) or {}
    error = body.get("error", {}) if isinstance(body, dict) else {}
    code = str(error.get("code", "")).lower()
    message = str(error.get("message", "")).lower()
    if code in {"insufficient_quota", "billing_not_active", "credit_balance_exhausted"}:
        return True
    return "insufficient_quota" in message or "credit_balance" in message or "billing" in message


def check_openai_health() -> OpenAIHealthResult:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return OpenAIHealthResult(
            OpenAIHealthStatus.MISSING_KEY,
            "OPENAI_API_KEY is not set",
        )

    client = OpenAI(api_key=api_key, timeout=30.0)

    try:
        client.models.list()
    except AuthenticationError:
        return OpenAIHealthResult(
            OpenAIHealthStatus.INVALID_KEY,
            "OpenAI API key is invalid or unauthorized",
        )
    except APIConnectionError as exc:
        return OpenAIHealthResult(
            OpenAIHealthStatus.ERROR,
            f"OpenAI API unreachable: {exc}",
        )
    except Exception as exc:
        return OpenAIHealthResult(
            OpenAIHealthStatus.ERROR,
            f"OpenAI models check failed: {exc}",
        )

    try:
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
    except AuthenticationError:
        return OpenAIHealthResult(
            OpenAIHealthStatus.INVALID_KEY,
            "OpenAI API key rejected during completion probe",
        )
    except RateLimitError as exc:
        if _quota_exhausted_from_error(exc):
            return OpenAIHealthResult(
                OpenAIHealthStatus.QUOTA_EXHAUSTED,
                "OpenAI credits exhausted or billing inactive",
            )
        return OpenAIHealthResult(
            OpenAIHealthStatus.ERROR,
            f"OpenAI rate limited during health probe: {exc}",
        )
    except Exception as exc:
        return OpenAIHealthResult(
            OpenAIHealthStatus.ERROR,
            f"OpenAI completion probe failed: {exc}",
        )

    return OpenAIHealthResult(OpenAIHealthStatus.OK, "OpenAI API key healthy")
