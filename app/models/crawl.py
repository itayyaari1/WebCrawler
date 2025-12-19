from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class CrawlStatus(Enum):
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class CrawlMetadata:
    crawl_id: str
    url: str
    status: CrawlStatus
    created_at: datetime
    updated_at: datetime
    result_location: Optional[str] = None
    error_message: Optional[str] = None
    notification_config: dict = None
    
    def __post_init__(self):
        if self.notification_config is None:
            self.notification_config = {}

