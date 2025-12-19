from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
import logging

from app.models.crawl import CrawlMetadata, CrawlStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["crawls"])


class CrawlRequest(BaseModel):
    url: str
    notification_config: dict = {}


class CrawlResponse(BaseModel):
    crawl_id: str


class StatusResponse(BaseModel):
    crawl_id: str
    status: str
    url: str
    created_at: str
    updated_at: str
    result_location: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/crawl", response_model=CrawlResponse)
def create_crawl(request: CrawlRequest):
    """
    Accept a crawl request.
    
    - Generate unique crawl_id
    - Store metadata with status ACCEPTED
    - Enqueue crawl job
    - Return crawl_id immediately
    """
    from app.main import db, queue
    
    # Generate unique crawl_id
    crawl_id = str(uuid.uuid4())
    
    # Create crawl metadata
    crawl_metadata = CrawlMetadata(
        crawl_id=crawl_id,
        url=request.url,
        status=CrawlStatus.ACCEPTED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        notification_config=request.notification_config
    )
    
    # Store metadata
    db.create(crawl_metadata)
    logger.info(f"Crawl created: {crawl_id}, URL: {request.url}")
    
    # Enqueue crawl job
    queue.enqueue(crawl_id)
    logger.info(f"Crawl enqueued: {crawl_id}")
    
    return CrawlResponse(crawl_id=crawl_id)


@router.get("/status/{crawl_id}")
def get_status(crawl_id: str):
    """
    Get crawl status.
    
    - If crawl exists: return status with details
    - If COMPLETE: include result_location
    - If ERROR: include error_message
    - If not found: return NOT_FOUND
    """
    from app.main import db
    
    crawl = db.get(crawl_id)
    
    if not crawl:
        return {
            "crawl_id": crawl_id,
            "status": "NOT_FOUND"
        }
    
    response = StatusResponse(
        crawl_id=crawl.crawl_id,
        status=crawl.status.value,
        url=crawl.url,
        created_at=crawl.created_at.isoformat(),
        updated_at=crawl.updated_at.isoformat(),
        result_location=crawl.result_location,
        error_message=crawl.error_message
    )
    
    return response

