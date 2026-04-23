# SOP: Identifying and Remediating Performance Sabotage

## Overview

This Standard Operating Procedure (SOP) outlines the methodology for identifying, investigating, and Neutralizing "disguised" performance bottlenecks (sabotage) in the Incubator Vault codebase.

## 🔍 Identification Patterns

### 1. The "Sleep Bomb"

Look for hidden latency in utility functions, especially those imported globally (e.g., `logger`, `bootstrap`, `performance`).

- **Standard Pattern**: `time.sleep(N)`
- **Disguised Patterns**:
  - `getattr(__import__('time'), 'sleep')(N)`
  - `threading.Event().wait(N)`
  - `socket.setdefaulttimeout(N)`
  - Busy-waits: `for _ in range(10**7): pass`

### 2. CSS/HTML Render-Blocking Delays (Bug-PERF-001)

**CRITICAL — This was the actual root cause of the 2026-04-23 sleep bomb.**

Look for blocking external resource loads in `st.markdown(unsafe_allow_html=True)` injections:

- **Blocking Pattern**: `@import url('https://...')` in CSS — blocks ALL rendering until the resource loads or times out (~120s)
- **Blocking Pattern**: `<link rel="stylesheet" href="https://...">` without async loading
- **Blocking Pattern**: `<script src="https://...">` without `async` or `defer`
- **Safe Pattern**: `<link ... media="print" onload="this.media='all'">` (non-blocking)
- **Safe Pattern**: Local font files or system font fallback stacks

**Detection**: Browser DevTools → Network tab shows pending/failed external requests. Python telemetry will show fast execution times while the page appears frozen.

### 3. Conditional Sabotage

Sabotage that only triggers under specific conditions (e.g., specific `session_id`, `observer_id`, or data volume).

- **Check**: Look for `if` statements checking for test strings like `"adv-session"` or `"test-user"` in core logic.

### 4. Dynamic File Rewriting (apply_and_test.py pattern)

Scripts that modify production source files at runtime can reintroduce any of the above patterns.

- **Check**: Search for `open(..., 'w')` or `re.sub()` calls targeting production `.py` files
- **Check**: Look for scripts that use `os.listdir()` + file writes to modify code in batch

## 🛠️ Remediation Steps

1. **Isolation**: Use `AppTest` with varied timeouts to pinpoint which view or utility is hanging.
2. **Forensic Search**: Use `grep` or `findstr` with regex to find non-standard imports of `time` or `math`.
3. **Excision**: Remove the offending code and replace it with a legitimate, performance-optimized alternative (e.g., replace `sleep` with a readiness probe).
4. **Hardening**: Standardize test timeouts to be slightly higher than expected network latency (e.g., 15s) to ensure stability without masking intentional delays.

## ⚖️ Compliance

All performance remediations must be documented in the `QA_Troubleshooting_Log.md` and verified with the full adversarial test suite.
