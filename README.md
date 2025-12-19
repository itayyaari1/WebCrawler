# Web Crawler System

A simple web crawler system that accepts crawl requests, processes them sequentially, stores HTML content, and sends notifications upon completion.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd WebCrawler
```

2. **Create virtual environment**
```bash
python3 -m venv venv
```

3. **Activate virtual environment**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on **http://localhost:8000**

---

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

---

## 🔌 API Endpoints

### 1. Submit a Crawl Request

**Endpoint:** `POST /crawl`

**Description:** Submit a URL to be crawled. Returns immediately with a unique `crawl_id`.

**Request Body:**
```json
{
  "url": "https://example.com",
  "notification_config": {
    "email": ["user@example.com"],
    "slack_user": ["@john"],
    "slack_channel": ["#crawl-notifications"]
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "notification_config": {
      "email": ["admin@example.com"]
    }
  }'
```

**Response:**
```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Note:** The `notification_config` is optional. Supported channels:
- `email` - Email notifications (mocked)
- `slack_user` - Slack direct messages (mocked)
- `slack_channel` - Slack channel messages (mocked)

---

### 2. Check Crawl Status

**Endpoint:** `GET /status/{crawl_id}`

**Description:** Get the current status of a crawl request.

**Example:**
```bash
curl "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

**Response - ACCEPTED (just submitted):**
```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ACCEPTED",
  "url": "https://example.com",
  "created_at": "2025-12-19T12:00:00.123456",
  "updated_at": "2025-12-19T12:00:00.123456",
  "result_location": null,
  "error_message": null
}
```

**Response - RUNNING (being processed):**
```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "RUNNING",
  "url": "https://example.com",
  "created_at": "2025-12-19T12:00:00.123456",
  "updated_at": "2025-12-19T12:00:01.234567",
  "result_location": null,
  "error_message": null
}
```

**Response - COMPLETE (finished successfully):**
```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETE",
  "url": "https://example.com",
  "created_at": "2025-12-19T12:00:00.123456",
  "updated_at": "2025-12-19T12:00:05.789012",
  "result_location": "data/html/550e8400-e29b-41d4-a716-446655440000.html",
  "error_message": null
}
```

**Response - ERROR (failed):**
```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ERROR",
  "url": "https://invalid-url.com",
  "created_at": "2025-12-19T12:00:00.123456",
  "updated_at": "2025-12-19T12:00:02.345678",
  "result_location": null,
  "error_message": "HTTPSConnectionPool(host='invalid-url.com', port=443): Max retries exceeded"
}
```

**Response - NOT_FOUND (invalid crawl_id):**
```json
{
  "crawl_id": "invalid-crawl-id",
  "status": "NOT_FOUND"
}
```

---

## 📋 Crawl Status Flow

```
ACCEPTED → RUNNING → COMPLETE
                  ↘ ERROR
```

1. **ACCEPTED** - Crawl request received and queued
2. **RUNNING** - Crawler is currently fetching the URL
3. **COMPLETE** - HTML successfully crawled and saved
4. **ERROR** - Crawl failed (network error, invalid URL, etc.)

---

## 🧪 Complete Example

**Step 1: Submit a crawl**
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Output:**
```json
{"crawl_id": "abc123..."}
```

**Step 2: Check status (immediately)**
```bash
curl "http://localhost:8000/status/abc123..."
```

**Output:**
```json
{"status": "ACCEPTED", ...}
```

**Step 3: Check status (after a few seconds)**
```bash
curl "http://localhost:8000/status/abc123..."
```

**Output:**
```json
{"status": "COMPLETE", "result_location": "data/html/abc123....html", ...}
```

**Step 4: View the crawled HTML**
```bash
cat data/html/abc123....html
```

---

## 🧰 Advanced Usage

### View All Crawls in Database
```bash
sqlite3 data/crawl_metadata.db -header -column "SELECT crawl_id, url, status FROM crawls;"
```

### Count Crawls by Status
```bash
sqlite3 data/crawl_metadata.db "SELECT status, COUNT(*) FROM crawls GROUP BY status;"
```

### Filter by Status
```bash
sqlite3 data/crawl_metadata.db -header -column "SELECT * FROM crawls WHERE status = 'COMPLETE';"
```

---

## 🗂️ Project Structure

```
WebCrawler/
├── app/
│   ├── main.py              # Application setup
│   ├── routes/              # API endpoints
│   ├── models/              # Data models
│   ├── db/                  # Database (SQLite)
│   ├── queue/               # Job queue
│   ├── worker/              # Background worker
│   ├── crawler/             # HTTP crawler
│   ├── storage/             # HTML storage
│   └── notifications/       # Notification system
├── data/
│   ├── html/                # Crawled HTML files
│   └── crawl_metadata.db    # Crawl metadata (SQLite)
├── requirements.txt
└── DesignReview.md          # Detailed design documentation
```

---

## 🛠️ Development

### Run with auto-reload (development mode)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run in production mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

---

## 📝 Features

- ✅ **Concurrent request handling** - API accepts multiple requests simultaneously
- ✅ **Sequential processing** - Crawls are processed one at a time
- ✅ **Persistent storage** - SQLite database (survives restarts)
- ✅ **HTML archival** - Saves complete HTML of crawled pages
- ✅ **Status tracking** - Real-time status updates
- ✅ **Notification support** - Email, Slack user, and Slack channel (mocked)
- ✅ **Error handling** - Graceful error capture and reporting

---

## 🔧 Configuration

### Clear all crawl data
```bash
rm -f data/crawl_metadata.db
rm -f data/html/*.html
```

### Reinstall dependencies
```bash
pip install --force-reinstall -r requirements.txt
```

### View server logs
Server logs are printed to the terminal where you started uvicorn.

---

## 📦 Dependencies

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Requests** - HTTP client
- **SQLite** - Database (built-in Python)

---

## 📖 Additional Documentation

- **DesignReview.md** - Detailed system design and implementation guide

---

## 🤝 Notes

- All notifications are **mocked** (logged to console only)
- Crawls are processed **sequentially** (one at a time)

---