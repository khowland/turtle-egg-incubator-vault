---
date: 2026-05-06 23:39
tags: [architecture, test-team, token-efficiency, claude, deepseek]
status: active
---

# Token-Efficient Test Team Architecture

> [!info] Design Principle
> **Claude (vision)** runs UI Playwright tests in fresh contexts. **Deepseek (A0)** orchestrates, fixes code, and handles non-visual tasks.

## Architecture Diagram

```
A0 (deepseek/v4-pro)              Claude Subagent (vision)
     │                                    │
     ├─ Launch Batch N ──────────────────►│
     │  (fresh context,                    │
     │   exact test command,               ├─ Verify app running: http://127.0.0.1:8599
     │   JSON report format)              ├─ Run pytest batch
     │                                    ├─ Capture failures + reasons
     │◄── JSON results + notes ──────────┤
     │                                    │
     ├─ Parse results                      │
     ├─ Log to Obsidian vault              │
     ├─ Log to remediation log             │
     ├─ Advance QA_TRIAD_LEDGER if needed  │
     ├─ Fix code if needed (deepseek)      │
     │                                    │
     ├─ Launch Batch N+1 ─────────────────► (fresh Claude, reset=true)
```

## Token Economics

| Component | Tokens/Invocation | Model |
|-----------|-------------------|-------|
| Claude subagent prompt | ~2,000 | Claude (vision) |
| Claude subagent output | ~1,000 | Claude (vision) |
| **Total per batch** | **~3,000** | Claude (vision) |
| A0 parsing + logging | ~500 | Deepseek (cheap) |

**vs. maintaining long Claude conversation**: Each turn adds ~3K tokens accumulated context. After 5 batches, a single Claude session would have ~15K+ tokens just in history. Fresh-context approach saves ~60%+ token cost.

## Batch Definitions

| Batch | TSKs | Tests | Status | Risk |
|-------|------|-------|--------|------|
| BATCH_1 | TSK-03 | `test_intake_extended.py` (5 tests) | COMPLETED | 2 fails (RPC bug, race condition) |
| BATCH_2 | TSK-07 | `test_phase5_scalability_loop.py` | READY | Strike 1 - race condition maybe fixed |
| BATCH_3 | TSK-04 | `test_observation_workflows.py` (7 tests) | BLOCKED | active_case_id bridging hang |
| BATCH_4 | TSK-06 | `test_adversarial_observations.py` | NEEDS_WORK | Writer fixes needed |
| BATCH_5 | TSK-08 | `test_adversarial_input.py` | NEEDS_WORK | Writer fixes needed |

## Infrastructure Files

- **Subagent prompt**: `/a0/usr/workdir/tmp/TEST_BATCH_RUNNER_PROMPT.md`
- **Remediation log**: `/a0/usr/workdir/tmp/TOKEN_EFFICIENT_TEST_TEAM_LOG.md`
- **Obsidian logger**: `/a0/usr/workdir/scripts/obsidian_log_test_batch.py`

## Launch Command (from A0 deepseek context)

```json
{
  "tool_name": "call_subordinate",
  "tool_args": {
    "profile": "default",
    "message": "You are a Claude test runner with vision. Run: cd /a0/usr/workdir && python -m pytest tests/e2e_playwright/test_intake_extended.py -v --tb=line --timeout=300 2>&1 | tail -50. Report JSON: {\"batch_id\":\"BATCH_2\",\"results\":[...],\"summary\":{...}}",
    "reset": true
  }
}
```

---
*Architecture designed by A0 (deepseek) + Claude collaboration, 2026-05-06*
