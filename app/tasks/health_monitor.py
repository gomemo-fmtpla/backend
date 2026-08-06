import logging
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.openai_health import OpenAIHealthStatus, check_openai_health
from app.services.slack_notifier import send_slack_health_alert

logger = logging.getLogger(__name__)

ALERT_COOLDOWN_SEC = 4 * 3600
_last_alert_sent: dict[str, float] = {}


def _format_alert_message(result) -> str:
    app_name = os.getenv("APP_NAME", "GoMemo")
    if result.status in {OpenAIHealthStatus.MISSING_KEY, OpenAIHealthStatus.QUOTA_EXHAUSTED}:
        emoji = "🚨"
    else:
        emoji = "⚠️"
    return (
        f"{emoji} *[{app_name}] OpenAI health alert*\n"
        f"*Status:* `{result.status.value}`\n"
        f"*Detail:* {result.message}\n"
        f"*Action:* Check billing at https://platform.openai.com/settings/organization/billing"
    )


def run_openai_health_check() -> None:
    result = check_openai_health()
    logger.info("OpenAI health check: %s — %s", result.status.value, result.message)

    if result.status == OpenAIHealthStatus.OK:
        return

    status_key = result.status.value
    now = time.time()
    last_sent = _last_alert_sent.get(status_key, 0)
    if now - last_sent < ALERT_COOLDOWN_SEC:
        logger.info("Skipping Slack alert for %s (cooldown active)", status_key)
        return

    message = _format_alert_message(result)
    if send_slack_health_alert(message):
        _last_alert_sent[status_key] = now
        logger.info("Posted OpenAI health alert to Slack for status=%s", status_key)


def init_health_monitor_scheduler() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_openai_health_check,
        "interval",
        hours=1,
        id="openai_health_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("OpenAI health monitor scheduler initialized (hourly)")
    run_openai_health_check()
