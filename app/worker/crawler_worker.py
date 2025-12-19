import threading
import logging
from app.queue.crawl_queue import CrawlQueue
from app.repository.crawl_repository import CrawlRepository
from app.crawler.http_crawler import HTTPCrawler
from app.storage.html_storage import HTMLStorage
from app.notifications.dispatcher import NotificationDispatcher
from app.models.crawl import CrawlStatus


logger = logging.getLogger(__name__)


class CrawlerWorker:
    def __init__(
        self,
        queue: CrawlQueue,
        repository: CrawlRepository,
        crawler: HTTPCrawler,
        storage: HTMLStorage,
        dispatcher: NotificationDispatcher
    ):
        self.queue = queue
        self.repository = repository
        self.crawler = crawler
        self.storage = storage
        self.dispatcher = dispatcher
        self._thread = None
        self._running = False
    
    def start(self):
        """Start the worker in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Crawler worker started")
    
    def stop(self):
        """Stop the worker."""
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("Crawler worker stopped")
    
    def _process_loop(self):
        """Main processing loop."""
        while self._running:
            try:
                # Dequeue crawl_id
                crawl_id = self.queue.dequeue()
                logger.info(f"Processing crawl: {crawl_id}")
                
                # Get crawl metadata
                crawl = self.repository.get(crawl_id)
                if not crawl:
                    logger.error(f"Crawl {crawl_id} not found in repository")
                    continue
                
                try:
                    # Update status to RUNNING
                    self.repository.update_status(crawl_id, CrawlStatus.RUNNING)
                    logger.info(f"Crawl {crawl_id} status: RUNNING")
                    
                    # Fetch HTML
                    html = self.crawler.fetch(crawl.url)
                    
                    # Save HTML
                    result_location = self.storage.save(crawl_id, html)
                    
                    # Update status to COMPLETE
                    self.repository.update_status(
                        crawl_id, 
                        CrawlStatus.COMPLETE, 
                        result_location=result_location
                    )
                    logger.info(f"Crawl {crawl_id} status: COMPLETE, location: {result_location}")
                    
                    # Dispatch notifications
                    self.dispatcher.dispatch(
                        crawl_id,
                        "COMPLETE",
                        crawl.notification_config,
                        result_location=result_location
                    )
                
                except Exception as e:
                    # Update status to ERROR
                    error_message = str(e)
                    self.repository.update_status(
                        crawl_id,
                        CrawlStatus.ERROR,
                        error_message=error_message
                    )
                    logger.error(f"Crawl {crawl_id} status: ERROR, error: {error_message}")
                    
                    # Dispatch notifications
                    self.dispatcher.dispatch(
                        crawl_id,
                        "ERROR",
                        crawl.notification_config,
                        error_message=error_message
                    )
            
            except Exception as e:
                logger.error(f"Worker error: {e}")

