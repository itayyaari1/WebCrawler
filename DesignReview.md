# Web Crawler System – Design Review

## Purpose

This project implements a **web crawler system** according to the assignment requirements.

The system:
- Accepts crawl requests under load
- Processes crawls sequentially (one at a time)
- Stores the HTML of crawled pages
- Exposes crawl status via an API
- Sends notifications upon crawl completion

The focus is on **system design and correctness**, not advanced crawling logic.

---

## Tech Stack

- Python 3.10+
- FastAPI
- `requests`
- Standard library (`threading`, `queue`, `uuid`, `datetime`)
- No external infrastructure (DB, queue, email, Slack are mocked)

---

## Project Structure

```
project/
│
├── app/
│   ├── main.py
│   │
│   ├── models/
│   │   └── crawl.py
│   │
│   ├── routes/
│   │   └── crawl_routes.py
│   │
│   ├── db/
│   │   ├── crawl_db.py (JSON storage)
│   │   └── crawl_db_sqlite.py (SQLite storage)
│   │
│   ├── queue/
│   │   └── crawl_queue.py
│   │
│   ├── worker/
│   │   └── crawler_worker.py
│   │
│   ├── crawler/
│   │   └── http_crawler.py
│   │
│   ├── storage/
│   │   └── html_storage.py
│   │
│   ├── notifications/
│   │   ├── base.py
│   │   ├── email.py
│   │   ├── slack_user.py
│   │   ├── slack_channel.py
│   │   └── dispatcher.py
│
├── data/
│   ├── html/
│   └── crawl_metadata.db (SQLite database - auto-created)
│
├── requirements.txt
└── DesignReview.md
```

---

## Crawl Statuses

- `ACCEPTED`
- `RUNNING`
- `COMPLETE`
- `ERROR`
- `NOT_FOUND` (API response only)

---

## Data Model

### CrawlMetadata

Fields:
- `crawl_id: str`
- `url: str`
- `status: CrawlStatus`
- `created_at: datetime`
- `updated_at: datetime`
- `result_location: Optional[str]`
- `error_message: Optional[str]`
- `notification_config: dict`

---

# Step-by-Step Implementation Plan

Each step should be implemented **in order**.  
Cursor should fully complete one step before moving to the next.

---

## Step 1 – Project Skeleton

- Create the directory structure exactly as defined above
- Add empty Python files for each component
- Create `requirements.txt` with:
  - `fastapi`
  - `uvicorn`
  - `requests`

No logic in this step.

---

## Step 2 – Crawl Status and Data Models

Implement in `app/models/crawl.py`:

- `CrawlStatus` enum with:
  - ACCEPTED
  - RUNNING
  - COMPLETE
  - ERROR

- `CrawlMetadata` data class containing all required fields

No persistence or logic yet.

---

## Step 3 – Crawl Database (Metadata Store)

Implement in `app/db/crawl_db_sqlite.py`:

Responsibilities:
- Store crawl metadata
- Act as the source of truth

Implementation details:
- SQLite database (persistent storage)
- Thread-safe (SQLite handles locking)
- Alternative JSON implementation available in `crawl_db.py`

Required methods:
- `create(crawl_metadata)`
- `update_status(crawl_id, status, result_location=None, error_message=None)`
- `get(crawl_id)`

No business logic here.

---

## Step 4 – Crawl Queue

Implement in `app/queue/crawl_queue.py`:

Responsibilities:
- Decouple ingestion from processing

Implementation details:
- FIFO in-memory queue
- Thread-safe

Required methods:
- `enqueue(crawl_id: str)`
- `dequeue() -> str`

---

## Step 5 – HTTP Crawler

Implement in `app/crawler/http_crawler.py`:

Responsibilities:
- Fetch raw HTML from a URL

Behavior:
- Perform HTTP GET
- Raise exception on failure
- Return HTML string

No retries or parsing.

---

## Step 6 – HTML Storage

Implement in `app/storage/html_storage.py`:

Responsibilities:
- Persist HTML to disk
- Return location reference

Behavior:
- Save HTML to:
```
data/html/{crawl_id}.html
```

Required method:
- `save(crawl_id: str, html: str) -> str`

---

## Step 7 – Notification Interfaces

Implement in `app/notifications/base.py`:

- Abstract `NotificationChannel` class
- Method:
  - `send(recipient: str, message: str)`

No logic here.

---

## Step 8 – Notification Channel Implementations

Implement mocks:

- `email.py`
- `slack_user.py`
- `slack_channel.py`

Each implementation:
- Implements `NotificationChannel`
- Logs notifications instead of sending real messages

---

## Step 9 – Notification Dispatcher

Implement in `app/notifications/dispatcher.py`:

Responsibilities:
- Receive crawl result
- Iterate over notification configuration
- Dispatch notifications via appropriate channels

Behavior:
- Triggered on `COMPLETE` and `ERROR`
- Supports multiple channels and recipients

No hard-coded channel logic.

---

## Step 10 – Crawl Worker

Implement in `app/worker/crawler_worker.py`:

Responsibilities:
- Process crawls sequentially

Behavior loop:
1. Dequeue `crawl_id`
2. Update status → RUNNING
3. Fetch HTML
4. Save HTML
5. Update status → COMPLETE
6. Dispatch notifications

Error handling:
- On exception:
  - Update status → ERROR
  - Save error message
  - Dispatch notifications

Concurrency:
- Exactly one worker
- Runs in background thread

---

## Step 11 – Ingestion API

Implement in `app/routes/crawl_routes.py`:

### POST /crawl

Responsibilities:
- Accept crawl requests
- Generate unique `crawl_id`
- Store metadata with status `ACCEPTED`
- Enqueue crawl job
- Return `crawl_id` immediately

Must:
- Support concurrent requests
- Not perform crawling

---

## Step 12 – Status API

Implement in `app/routes/crawl_routes.py`:

### GET /status/{crawl_id}

Behavior:
- If crawl exists:
  - Return status
  - If COMPLETE → include result location
  - If ERROR → include error message
- If not found:
  - Return NOT_FOUND

Important:
- Read-only
- No external calls

---

## Step 13 – Application Startup

Implement in `app/main.py`:

On startup:
- Initialize database
- Initialize queue
- Initialize storage and notification dispatcher
- Start crawl worker in background thread
- Register API routes
- Start FastAPI app

---

## Logging

Log:
- Crawl creation
- Status changes
- Crawl completion or failure
- Notifications sent

---

## Out of Scope

- Recursive crawling
- JavaScript rendering
- Authentication
- Retry logic
- Real email or Slack integrations

---

## Summary

This implementation:
- Matches the assignment requirements exactly
- Separates concerns cleanly: routes, business logic, storage, and notifications
- Uses SQLite for persistent storage (JSON alternative available)
- Clean architecture with dedicated routes module
- Is easy to extend and reason about
- Is suitable for a production design discussion
