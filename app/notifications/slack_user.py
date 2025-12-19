import logging
from app.notifications.base import NotificationChannel


logger = logging.getLogger(__name__)


class SlackUserNotification(NotificationChannel):
    def send(self, recipient: str, message: str):
        """Send Slack user notification (mocked)."""
        logger.info(f"[SLACK USER] To: {recipient}, Message: {message}")

