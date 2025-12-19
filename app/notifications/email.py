import logging
from app.notifications.base import NotificationChannel


logger = logging.getLogger(__name__)


class EmailNotification(NotificationChannel):
    def send(self, recipient: str, message: str):
        """Send email notification (mocked)."""
        logger.info(f"[EMAIL] To: {recipient}, Message: {message}")

