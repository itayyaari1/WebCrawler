from app.notifications.base import NotificationChannel
from app.notifications.email import EmailNotification
from app.notifications.slack_user import SlackUserNotification
from app.notifications.slack_channel import SlackChannelNotification


class NotificationDispatcher:
    def __init__(self):
        self.channels = {
            "email": EmailNotification(),
            "slack_user": SlackUserNotification(),
            "slack_channel": SlackChannelNotification(),
        }
    
    def dispatch(self, crawl_id: str, status: str, notification_config: dict, result_location: str = None, error_message: str = None):
        """
        Dispatch notifications based on configuration.
        
        Args:
            crawl_id: The crawl identifier
            status: The crawl status (COMPLETE or ERROR)
            notification_config: Dictionary with notification channel and recipient info
            result_location: Location of crawled HTML (for COMPLETE)
            error_message: Error message (for ERROR)
        """
        # Build message
        if status == "COMPLETE":
            message = f"Crawl {crawl_id} completed successfully. Result: {result_location}"
        elif status == "ERROR":
            message = f"Crawl {crawl_id} failed. Error: {error_message}"
        else:
            return  # Only dispatch on COMPLETE or ERROR
        
        # Dispatch to each configured channel
        for channel_type, recipients in notification_config.items():
            if channel_type in self.channels:
                channel = self.channels[channel_type]
                if isinstance(recipients, list):
                    for recipient in recipients:
                        channel.send(recipient, message)
                else:
                    # Single recipient
                    channel.send(recipients, message)

