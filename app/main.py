from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
import logging

from app.models.crawl import CrawlMetadata, CrawlStatus
from app.repository.crawl_repository import CrawlRepository
from app.queue.crawl_queue import CrawlQueue
from app.crawler.http_crawler import HTTPCrawler
from app.storage.html_storage import HTMLStorage
from app.notifications.dispatcher import NotificationDispatcher
from app.worker.crawler_worker import CrawlerWorker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize components (will be done in startup event)
repository = None
queue = None
worker = None

app = FastAPI(title="Web Crawler System")


@app.on_event("startup")
def startup_event():
    """Initialize all components and start worker on application startup."""
    global repository, queue, worker
    
    logger.info("Starting Web Crawler System...")
    
    # Initialize repository
    repository = CrawlRepository()
    logger.info("Repository initialized")
    
    # Initialize queue
    queue = CrawlQueue()
    logger.info("Queue initialized")
    
    # Initialize crawler, storage, and dispatcher
    crawler = HTTPCrawler()
    storage = HTMLStorage()
    dispatcher = NotificationDispatcher()
    logger.info("Crawler, storage, and dispatcher initialized")
    
    # Initialize and start worker
    worker = CrawlerWorker(queue, repository, crawler, storage, dispatcher)
    worker.start()
    logger.info("Worker started")
    
    logger.info("Web Crawler System ready!")


@app.on_event("shutdown")
def shutdown_event():
    """Stop worker on application shutdown."""
    if worker:
        worker.stop()
        logger.info("Worker stopped")


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


@app.post("/crawl", response_model=CrawlResponse)
def create_crawl(request: CrawlRequest):
    """
    Accept a crawl request.
    
    - Generate unique crawl_id
    - Store metadata with status ACCEPTED
    - Enqueue crawl job
    - Return crawl_id immediately
    """
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
    repository.create(crawl_metadata)
    logger.info(f"Crawl created: {crawl_id}, URL: {request.url}")
    
    # Enqueue crawl job
    queue.enqueue(crawl_id)
    logger.info(f"Crawl enqueued: {crawl_id}")
    
    return CrawlResponse(crawl_id=crawl_id)


@app.get("/status/{crawl_id}")
def get_status(crawl_id: str):
    """
    Get crawl status.
    
    - If crawl exists: return status with details
    - If COMPLETE: include result_location
    - If ERROR: include error_message
    - If not found: return NOT_FOUND
    """
    crawl = repository.get(crawl_id)
    
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

