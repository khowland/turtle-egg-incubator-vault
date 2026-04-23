---
title: "Bug-PERF-001: Adversarial Sleep Bomb (CSS @import Blocking Delay)"
tags: [bug, performance, adversarial, sleep-bomb, css, remediation]
date: 2026-04-23
severity: CRITICAL
status: RESOLVED
---

# Bug-PERF-001: Adversarial Sleep Bomb — CSS @import Blocking Delay

## Summary
A ~120-second startup delay on the Login/Splash page was traced to a **blocking CSS `@import url()` for Google Fonts** in `utils/bootstrap.py`. This was originally characterized as a "sleep bomb" from adversarial testing, but the root cause was **not** a Python `time.sleep()` call — it was a **browser-level network timeout** caused by the CSS rendering engine blocking on an unreachable external CDN.

## Symptoms
- ~120-second (2-minute) delay when loading the starting page
- Delay appeared on **every** page load (not just first)
- The delay "kept coming back" after Python-only remediations
- Performance telemetry showed Python view rendering in < 1 second (the delay was not in Python)

## Root Cause Analysis

### Primary Cause: Blocking CSS `@import`
In `utils/bootstrap.py`, the `bootstrap_page()` function injected CSS via `st.markdown()` containing:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
```

Per the CSS specification, `@import` is a **synchronous, render-blocking** operation. When the browser encounters it:
1. It **pauses all CSS parsing** until the external resource is fetched
2. If the network request fails (Docker container without internet, firewall, DNS failure), the browser **waits for the full TCP connection timeout** (~60-120 seconds)
3. Only AFTER the timeout does the page render with fallback fonts

This creates an **invisible 2-minute delay** with no visible error, no Python-level evidence, and no server-side logging — the perfect "hidden sleep bomb."

### Why Previous Remediations Failed
- **Commit `0265b8b`** ("remediation: remove performance sabotage") only modified test file timeouts (`at.run(timeout=15)`), not the actual CSS code
- The `QA_Troubleshooting_Log.md` incorrectly attributed the bomb to `utils/performance.py`, which **never contained a sleep call** (verified across all 6 git commits touching that file)
- All previous searches focused on Python `time.sleep()` patterns, while the actual delay was in the CSS/HTML rendering layer

### Contributing Factor: Supabase Auto-Wake
`utils/supabase_mgmt.py` → `wait_for_restoration()` has a 90-second polling loop with `time.sleep(5)` intervals, triggered when Supabase returns 503/404. If both the CSS timeout AND Supabase wake occur simultaneously, total delay could exceed 3 minutes.

## Fix Applied (2026-04-23)

### File: `utils/bootstrap.py`
1. **Removed** the blocking `@import url(...)` CSS directive
2. **Added** non-blocking font loading via HTML `<link>` tags with:
   - `rel="preconnect"` for DNS/TLS pre-warming
   - `media="print" onload="this.media='all'"` pattern for async CSS loading
3. **Added** comprehensive system font fallback stack:
   ```css
   font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
   ```
4. **Added** detailed inline CSS comments explaining the bug and fix for future developers

### File: `apply_and_test.py`
- **Quarantined** with security warning — this script dynamically rewrites source files at runtime and is a potential vector for reintroducing adversarial code

## How to Detect If This Bug Returns
1. **Symptom**: Page takes > 5 seconds to render the Login splash
2. **Check**: Open browser DevTools → Network tab → look for a pending/failed request to `fonts.googleapis.com`
3. **Check**: Search `utils/bootstrap.py` for `@import url(` — if found, it's back
4. **Check**: Run `grep -rn '@import url' utils/ vault_views/` to scan all files
5. **Telemetry**: `reports/performance_telemetry.jsonl` will show fast Python times (< 1s) even when the page appears slow — this confirms the delay is in the browser, not Python

## Prevention Rules
1. **NEVER** use CSS `@import url()` for external resources in Streamlit apps
2. **ALWAYS** use `<link>` tags with `font-display: swap` or async loading patterns
3. **ALWAYS** include a comprehensive system font fallback stack
4. **ALWAYS** test in a network-restricted Docker container to verify no blocking external dependencies

## Related Documentation
- [[00_CENTRAL_HUB|Central Information Hub]]
- [[../docs/Performance_Sabotage_SOP|Performance Sabotage SOP]]
- [[../docs/QA_Troubleshooting_Log|QA Troubleshooting Log]]

## Commit Reference
- Original (incomplete) remediation: `0265b8b` — only changed test timeouts
- Actual fix: Current commit — removed blocking @import, added async font loading
