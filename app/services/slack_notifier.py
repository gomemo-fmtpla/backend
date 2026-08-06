import logging
import os

import requests

logger = logging.getLogger(__name__)


def send_slack_health_alert(message: str, channel_id: str | None = None) -> bool:
    token = (os.getenv("SLACK_BOT_TOKEN") or "").strip()
    channel = (channel_id or os.getenv("SLACK_HEALTH_CHANNEL_ID") or "").strip()
    if not token or not channel:
        logger.warning(
            "Slack health alert skipped: SLACK_BOT_TOKEN or SLACK_HEALTH_CHANNEL_ID not configured"
        )
        return False

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={"channel": channel, "text": message},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        logger.error("Slack post failed: %s", payload.get("error"))
        return False
    return True
