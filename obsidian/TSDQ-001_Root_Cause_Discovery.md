---
date: 2026-05-07 00:45
tags: [tsdq-001, bridging-bug, root-cause, streamlit-session]
status: in-progress
---

# TSDQ-001 Root Cause Discovery

> [!danger] Critical Finding
> Streamlit session state is NOT preserved across `page.reload()` or direct URL navigation.

## Evidence Chain

1. **Test symptom**: stMultiSelect not found → selectbox dropdowns have no options → tests timeout/hang
2. **First hypothesis (rejected)**: ORM fallback just needs triggering → tried `page.reload()`
3. **Smoke test result**: `page.reload()` FAILED — multi-select never found even after 3 reloads
4. **Data diagnostic**: Confirmed bins, intakes, eggs EXIST in Supabase DB (ORM fallback has data)
5. **Browser investigation**: Navigating directly to `/3_Observations` shows "Page not found" — redirected to home
6. **Root cause**: Streamlit sessions are cookie-based. `page.reload()` or `page.goto(url)` may lose the session cookie linkage, causing the Observations page to not render at all.

## What Actually Works
- Login via START button on home page → creates session cookie
- Navigate via Streamlit sidebar link click (`a:has-text('Observations')`) → preserves session
- The Observations page then renders with workbench_bins populated via ORM fallback

## Why Existing Tests Fail
- Some test helpers use `page.goto()` for URL navigation which loses session
- Some tests navigate too quickly before page fully hydrates
- The ORM fallback queries Supabase which may have latency

## New Approach (Tactic 2 Round 2)
- Instead of `page.reload()`: ensure navigation ALWAYS uses sidebar link click, never direct URL
- Add explicit wait for Observations heading before interacting with multi-select
- If multi-select still empty, use sidebar re-navigation (click Dashboard → click Observations) to force full page re-render with session intact

---
*Discovered by Tactic 2 Model 1 (Deepseek) + Browser Investigation*
