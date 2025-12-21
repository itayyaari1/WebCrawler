from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CrawlStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"


class CrawlMetadata(BaseModel):
    crawl_id: str
    url: str
    status: CrawlStatus
    created_at: datetime
    updated_at: datetime
    result_location: Optional[str] = None
    error_message: Optional[str] = None
    notification_config: dict = Field(default_factory=dict)

