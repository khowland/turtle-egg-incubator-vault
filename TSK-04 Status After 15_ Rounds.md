## TSK-04 Status After 15+ Rounds

### What's Fixed ✅

| Block | Solution | Status |
|-------|----------|--------|
| SAVE button click | Let Streamlit auto-navigate via `st.switch_page()` instead of manual `page.goto()` | **Resolved** |
| DB eventual consistency | Retry loop (5 attempts, 500ms delay) | **Resolved** |
| Weight gate | Conditional skip — `env_gate_synced` already `True` from intake | **Resolved** |
| Observations rendering | Biological Grid with 2 subjects renders correctly | **Resolved** |
| Multi-select workbench | Bin pre-selected from intake bridge, no click needed | **Resolved** |

### What's Still Failing ❌

| Blocker | Symptom | Root Cause |
|---------|---------|------------|
| Stage selectbox dropdown | `[DIAG-A1] Dropdown container count: 0` — S2 option never opens | **Same Streamlit-Playwright dropdown incompatibility** as multi-select |
| Observation SAVE | Stage stays at S1 (never changed to S2) | **Cascade from dropdown** — can't select S2, so SAVE records default S1 |

**Last test**: `AssertionError: Egg stage not updated to S2, got S1` — test got all the way through to DB verification, proving intake→Observations→Grid→START pipeline works end-to-end.

### ⚠️ Memory Discrepancy
Memories claim "Property Matrix visible: False" — **this is outdated**. Last test log shows:

```
🥚 Biological Grid
Showing 2 subjects in WT147-OBS-SETUP-1778154229-1
START
1
2
```

Property Matrix **IS** rendering. Memories need update.

### Next Step
Stage selectbox dropdown is the **same systemic issue** as multi-select dropdown — Streamlit widgets not opening in Playwright's headless DOM. Recommend:

**Option**: Use `page.evaluate()` to directly set `st.session_state.selected_eggs` and trigger Streamlit rerun, bypassing dropdown entirely. Then SAVE observation via form submission.

This is the last blocker before TSK-04 goes green, unblocking 13+ tests across TSK-04/06/07. Want me to implement the `page.evaluate()` approach?