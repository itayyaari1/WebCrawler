from fastapi import FastAPI
import logging

from app.db.crawl_db import CrawlDB
from app.queue.crawl_queue import CrawlQueue
from app.crawler.http_crawler import HTTPCrawler
from app.storage.html_storage import HTMLStorage
from app.notifications.dispatcher import NotificationDispatcher
from app.worker.crawler_worker import CrawlerWorker
from app.routes.crawl_routes import router as crawl_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize components (will be done in startup event)
db = None
queue = None
worker = None

# Create FastAPI app
app = FastAPI(title="Web Crawler System")

# Include routers
app.include_router(crawl_router)


@app.on_event("startup")
def startup_event():
    """Initialize all components and start worker on application startup."""
    global db, queue, worker
    
    logger.info("Starting Web Crawler System...")
    
    # Initialize database
    db = CrawlDB()
    logger.info("Database initialized")
    
    # Initialize queue
    queue = CrawlQueue()
    logger.info("Queue initialized")
    
    # Initialize crawler, storage, and dispatcher
    crawler = HTTPCrawler()
    storage = HTMLStorage()
    dispatcher = NotificationDispatcher()
    logger.info("Crawler, storage, and dispatcher initialized")
    
    # Initialize and start worker
    worker = CrawlerWorker(queue, db, crawler, storage, dispatcher)
    worker.start()
    logger.info("Worker started")
    
    logger.info("Web Crawler System ready!")


@app.on_event("shutdown")
def shutdown_event():
    """Stop worker on application shutdown."""
    if worker:
        worker.stop()
        logger.info("Worker stopped")

