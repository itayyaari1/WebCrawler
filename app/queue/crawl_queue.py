import queue


class CrawlQueue:
    def __init__(self):
        self._queue = queue.Queue()
    
    def enqueue(self, crawl_id: str):
        """Add a crawl ID to the queue."""
        self._queue.put(crawl_id)
    
    def dequeue(self) -> str:
        """Remove and return a crawl ID from the queue. Blocks if queue is empty."""
        return self._queue.get()

