#!/usr/bin/env python3
"""Log test batch results to Obsidian vault."""
import sys
import json
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path("/a0/usr/workdir")

def log_batch_results(batch_json: str, batch_id: str):
    """Append batch results to Obsidian vault note."""
    results = json.loads(batch_json)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    note_path = VAULT_ROOT / "obsidian" / f"Test_Batch_{batch_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    
    content = f"""---
date: {now}
tags: [test-batch, qa, tsk]
status: completed
batch_id: {batch_id}
---

# Test Batch {batch_id} — {now}

> [!info] Architecture
> A0 (deepseek) orchestrated this batch. Claude subagent executed UI tests with vision.

## Results Summary

| Metric | Count |
|--------|-------|
| Total | {results['summary']['total']} |
| Passed | {results['summary']['passed']} |
| Failed | {results['summary']['failed']} |
| Timeout | {results['summary']['timeout']} |
| Error | {results['summary']['error']} |

## Individual Results

| Test | Status | Duration | Failure Reason |
|------|--------|----------|---------------|
"""
    for r in results['results']:
        status_icon = "✅" if r['status'] == 'PASSED' else "❌" if r['status'] == 'FAILED' else "⏱️" if r['status'] == 'TIMEOUT' else "⚠️"
        reason = r.get('failure_reason') or '-'
        content += f"| {r['test_name']} | {status_icon} {r['status']} | {r['duration_seconds']}s | {reason} |\n"
    
    content += f"""
## Notes

{results.get('notes', 'No observations recorded.')}

---
*Logged by A0 test team archiver*
"""
    
    note_path.write_text(content)
    print(f"✅ Obsidian note written: {note_path}")
    return note_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: obsidian_log_test_batch.py <batch_json> <batch_id>")
        sys.exit(1)
    log_batch_results(sys.argv[1], sys.argv[2])
