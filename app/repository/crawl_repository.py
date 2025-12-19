import threading
from typing import Optional
from datetime import datetime
from app.models.crawl import CrawlMetadata, CrawlStatus


class CrawlRepository:
    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()
    
    def create(self, crawl_metadata: CrawlMetadata):
        """Store new crawl metadata."""
        with self._lock:
            self._store[crawl_metadata.crawl_id] = crawl_metadata
    
    def update_status(
        self, 
        crawl_id: str, 
        status: CrawlStatus, 
        result_location: Optional[str] = None, 
        error_message: Optional[str] = None
    ):
        """Update crawl status and related fields."""
        with self._lock:
            if crawl_id in self._store:
                crawl = self._store[crawl_id]
                crawl.status = status
                crawl.updated_at = datetime.now()
                if result_location is not None:
                    crawl.result_location = result_location
                if error_message is not None:
                    crawl.error_message = error_message
    
    def get(self, crawl_id: str) -> Optional[CrawlMetadata]:
        """Retrieve crawl metadata by ID."""
        with self._lock:
            return self._store.get(crawl_id)

