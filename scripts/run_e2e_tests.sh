#!/bin/bash
set -euo pipefail

PORT=8501

if command -v fuser >/dev/null 2>&1; then
  fuser -k ${PORT}/tcp 2>/dev/null || true
else
  pkill -f "streamlit run app.py --server.port ${PORT}" || true
  pkill -f "streamlit run app.py" || true
fi
sleep 1

echo "🚀 Starting Streamlit Server in background on port ${PORT}..."
nohup streamlit run app.py --server.port ${PORT} > streamlit_e2e.log 2>&1 &
ST_PID=$!

cleanup() {
  echo "\n🧹 Shutting down Streamlit (PID: $ST_PID)..."
  kill "$ST_PID" 2>/dev/null || true
  if command -v fuser >/dev/null 2>&1; then
    fuser -k ${PORT}/tcp 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "⏳ Waiting for Streamlit readiness on http://localhost:${PORT} ..."
for i in $(seq 1 60); do
  if curl -fsS http://localhost:${PORT} >/dev/null 2>&1; then
    echo "✅ Streamlit ready after ${i}s"
    break
  fi
  sleep 1
  if [ "$i" -eq 60 ]; then
    echo "❌ Streamlit failed to become ready on port ${PORT} within timeout"
    exit 1
  fi
done

echo "\n🛡️ Running Playwright End-to-End Tests..."
python3 -m pytest tests/e2e_playwright/ -v
