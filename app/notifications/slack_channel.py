import logging
from app.notifications.base import NotificationChannel


logger = logging.getLogger(__name__)


class SlackChannelNotification(NotificationChannel):
    def send(self, recipient: str, message: str):
        """Send Slack channel notification (mocked)."""
        logger.info(f"[SLACK CHANNEL] To: {recipient}, Message: {message}")

