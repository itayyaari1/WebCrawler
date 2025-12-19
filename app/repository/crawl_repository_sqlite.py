import sqlite3
import json
from typing import Optional
from datetime import datetime
from app.models.crawl import CrawlMetadata, CrawlStatus


class CrawlRepositorySQLite:
    def __init__(self, db_file: str = "data/crawl_metadata.db"):
        self.db_file = db_file
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create table if not exists."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawls (
                    crawl_id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    result_location TEXT,
                    error_message TEXT,
                    notification_config TEXT
                )
            """)
            conn.commit()
    
    def create(self, crawl_metadata: CrawlMetadata):
        """Store new crawl metadata."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                INSERT INTO crawls VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crawl_metadata.crawl_id,
                crawl_metadata.url,
                crawl_metadata.status.value,
                crawl_metadata.created_at.isoformat(),
                crawl_metadata.updated_at.isoformat(),
                crawl_metadata.result_location,
                crawl_metadata.error_message,
                json.dumps(crawl_metadata.notification_config)
            ))
            conn.commit()
    
    def update_status(
        self, 
        crawl_id: str, 
        status: CrawlStatus, 
        result_location: Optional[str] = None, 
        error_message: Optional[str] = None
    ):
        """Update crawl status and related fields."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                UPDATE crawls 
                SET status = ?, updated_at = ?, result_location = ?, error_message = ?
                WHERE crawl_id = ?
            """, (
                status.value,
                datetime.now().isoformat(),
                result_location,
                error_message,
                crawl_id
            ))
            conn.commit()
    
    def get(self, crawl_id: str) -> Optional[CrawlMetadata]:
        """Retrieve crawl metadata by ID."""
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM crawls WHERE crawl_id = ?", 
                (crawl_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return CrawlMetadata(
                crawl_id=row['crawl_id'],
                url=row['url'],
                status=CrawlStatus(row['status']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                result_location=row['result_location'],
                error_message=row['error_message'],
                notification_config=json.loads(row['notification_config'])
            )

