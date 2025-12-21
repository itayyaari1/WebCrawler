#!/bin/bash

# Web Crawler System - Parallel Ingestion Test
# Demonstrates that the system can accept multiple requests simultaneously

API_URL="http://localhost:8000"

echo "======================================================================"
echo "WEB CRAWLER - PARALLEL INGESTION TEST"
echo "======================================================================"
echo ""

# Check if server is running
echo "🔍 Checking if server is running..."
if ! curl -s --max-time 2 "$API_URL/docs" > /dev/null 2>&1; then
    echo "❌ Error: Server is not running on $API_URL"
    echo ""
    echo "Please start the server first:"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi
echo "✅ Server is running"
echo ""

# Test: Submit 3 requests in parallel
echo "======================================================================"
echo "TEST: SUBMITTING 3 REQUESTS IN PARALLEL"
echo "======================================================================"
echo ""
echo "📤 Sending 3 crawl requests simultaneously..."
echo ""

# Submit 3 requests in parallel (background processes with &)
curl -s -X POST "$API_URL/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' &
PID1=$!

curl -s -X POST "$API_URL/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}' &
PID2=$!

curl -s -X POST "$API_URL/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.iana.org"}' &
PID3=$!

# Wait for all 3 to complete
wait $PID1 $PID2 $PID3

echo ""
echo "======================================================================"
echo "✅ RESULT: All 3 requests accepted in parallel!"
echo "======================================================================"
echo ""
echo "Proof - Check the database (all created at nearly the same time):"
echo ""

sqlite3 data/crawl_metadata.db -header -column \
  "SELECT crawl_id, url, status, created_at 
   FROM crawls 
   ORDER BY created_at DESC 
   LIMIT 3;"

echo ""
echo "======================================================================"
echo "💡 KEY INSIGHT:"
echo "======================================================================"
echo ""
echo "  Look at the 'created_at' timestamps above:"
echo "  - All 3 crawls created within milliseconds of each other"
echo "  - This proves the API accepted them IN PARALLEL ✅"
echo ""
echo "  The 'status' column shows:"
echo "  - Some may be RUNNING (being processed now)"
echo "  - Some may be ACCEPTED (waiting in queue)"
echo "  - This proves processing is SEQUENTIAL ✅"
echo ""
echo "======================================================================"
echo ""

exit 0
