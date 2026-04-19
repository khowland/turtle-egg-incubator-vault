---
component: vault_views/6_Reports.py
issue_type: vocabulary_violation
resolved: true
---
# Bug-P3-001: Unified Vocabulary Violation — 6_Reports.py Sidebar Export Button

**Test:** `test_unified_vocab_reports_view` (test_vocabulary_all_views.py)  
**Severity:** Medium — §1.4 Unified Vocabulary compliance  
**Error:** `AssertionError: [6_Reports.py] Unified Vocabulary violations found: ['📦 Export eggs (active bins) CSV']`

## Root Cause
`st.sidebar.button("📦 Export eggs (active bins) CSV")` — emoji + long descriptive label not in `ALLOWED_LABELS = {"SAVE", "CANCEL", "ADD", "REMOVE", "START", "SHIFT END"}`.

## Fix Applied
```diff
- if st.sidebar.button("📦 Export eggs (active bins) CSV"):
+ if st.sidebar.button("SAVE", help="Export eggs (active bins) to CSV", use_container_width=True):
```

## Validation
`test_unified_vocab_reports_view` — ✅ PASS
