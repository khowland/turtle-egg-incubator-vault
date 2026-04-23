#!/bin/bash
set -euo pipefail

echo "🚀 Starting Streamlit Server in background on port 8501..."
nohup streamlit run app.py --server.port 8501 > streamlit_e2e.log 2>&1 &
ST_PID=$!

cleanup() {
  echo "\n🧹 Shutting down Streamlit (PID: $ST_PID)..."
  kill "$ST_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "⏳ Waiting for Streamlit readiness on http://localhost:8501 ..."
for i in $(seq 1 60); do
  if curl -fsS http://localhost:8501 >/dev/null 2>&1; then
    echo "✅ Streamlit ready after ${i}s"
    break
  fi
  sleep 1
  if [ "$i" -eq 60 ]; then
    echo "❌ Streamlit failed to become ready on port 8501 within timeout"
    exit 1
  fi
done

echo "\n🛡️ Running Playwright End-to-End Tests..."
python3 -m pytest tests/e2e_playwright/ -v
