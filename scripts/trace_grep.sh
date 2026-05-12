#!/bin/bash
# scripts/trace_grep.sh — search all log sources by trace_id
# Usage: ./scripts/trace_grep.sh <trace_id>
if [ -z "$1" ]; then
    echo "Usage: $0 <trace_id>"
    exit 1
fi
tid="$1"
echo "=== app.log ===" && grep "$tid" logs/app.log 2>/dev/null
echo "=== error.log ===" && grep "$tid" logs/error.log 2>/dev/null
echo "=== audit.log ===" && grep "$tid" logs/audit.log 2>/dev/null
