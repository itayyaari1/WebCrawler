import threading
import json
import os
from typing import Optional
from datetime import datetime
from app.models.crawl import CrawlMetadata, CrawlStatus


class CrawlRepository:
    def __init__(self, storage_file: str = "data/crawl_metadata.json"):
        self._store = {}
        self._lock = threading.Lock()
        self._storage_file = storage_file
        self._load_from_file()
    
    def _load_from_file(self):
        """Load metadata from JSON file on initialization."""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, 'r') as f:
                    data = json.load(f)
                    for crawl_id, crawl_dict in data.items():
                        self._store[crawl_id] = CrawlMetadata.model_validate(crawl_dict)
            except Exception as e:
                print(f"Warning: Could not load metadata from {self._storage_file}: {e}")
    
    def _save_to_file(self):
        """Save metadata to JSON file."""
        try:
            os.makedirs(os.path.dirname(self._storage_file), exist_ok=True)
            data = {crawl_id: crawl.model_dump(mode='json') for crawl_id, crawl in self._store.items()}
            with open(self._storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata to {self._storage_file}: {e}")
    
    def create(self, crawl_metadata: CrawlMetadata):
        """Store new crawl metadata."""
        with self._lock:
            self._store[crawl_metadata.crawl_id] = crawl_metadata
            self._save_to_file()
    
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
                self._save_to_file()
    
    def get(self, crawl_id: str) -> Optional[CrawlMetadata]:
        """Retrieve crawl metadata by ID."""
        with self._lock:
            return self._store.get(crawl_id)

