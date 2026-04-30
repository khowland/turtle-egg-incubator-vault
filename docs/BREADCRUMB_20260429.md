# 🐢 SESSION BREADCRUMB: 2026-04-29
**Last Updated**: 23:14 CST
**Status**: Clinical workflow fixes + supplemental intake CR planning complete

---

## ✅ FIXED THIS SESSION (Commits)

| Commit | What |
|--------|------|
| `77b6355` | Renamed 'Add a Bin to a Case' → 'Add Bin to Intake'; removed DEBUG `st.write` from Hydration Gate |
| `57d4a1e` | Built supplemental bin form on Observations screen (auto-increment bin code, intake-style table) |
| `05d4355` | Fixed ghost `⚪ (0/0)` entry — filtered empty bin_ids from workbench options and valid_defaults |
| `a049cff` | Fixed `observer_name NOT NULL` violation in `bin_observation` inserts (Hydration SAVE error) |
| `81ad572` | CR-20260429-210932: bin code anatomy + requirements.md §6.A updated |
| `df31d1e` | CR-20260429-221541: bin_code/bin_id separation plan filed (DO_NOT_FIX_YET) |
| `df5d8b8` | CR-20260429-224325: Intake Date label, finder pre-pop, supplemental wiring gap |
| `887ea8e` | CR-20260429-225412: Consolidate supplemental intake plan filed |
| `c83b887` | Red team review of CR-20260429-225412 — 5 blocking issues found |

---

## 🗂️ OPEN CHANGE REQUESTS (PENDING AUTHORIZATION)

### 🟡 CR-20260429-224325 — Intake Form Fixes + Supplemental Wiring
`change_requests/change_request_20260429224325.txt`
- [ ] Lo-1: `"Date"` → `"Intake Date"` label (line 108, 2_New_Intake.py)
- [ ] Lo-2: Auto-populate Finder from selected intake in supplemental mode
- [ ] Lo-3: Wire `commit_all()` to branch on intake_mode (supp path broken — ALWAYS creates new intake)
- [ ] Lo-4: Add `egg_observation` S1 baseline inserts to `commit_sup_bin()` in Observations

### 🔴 CR-20260429-225412 — Consolidate Supplemental Intake (BLOCKED BY RED TEAM)
`change_requests/change_request_20260429225412.txt`
`reports/red_team_review_CR-20260429-225412.md`

**DO NOT START until red team blockers are resolved:**

| ID | Blocking Issue |
|----|----------------|
| RT-01 | `append_eggs()` has live `observer_name NOT NULL` violation — fix before porting |
| RT-02 | `"PENDING"` can be committed as real bin_id — add guard before SAVE |
| RT-03 | `commit_all()` Step 1 validation blocks supplemental SAVE — make mode-aware |
| RT-04 | Supplemental bin code uses wrong intake number (`species.intake_count+1` instead of existing intake's ordinal) |
| RT-05 | No transaction wrapping — partial failure leaves orphaned bins blocking Hydration Gate permanently |

**Recommended pre-work (design challenges):**
- DC-01: Write `vault_finalize_supplemental_bin` RPC (eliminates RT-05, RT-06, RT-11)
- DC-02: Add `intake_number INTEGER` to `intake` table (eliminates RT-04 permanently)
- DC-03: Render Step 1 read-only (not hidden) in supplemental mode (eliminates RT-03)

**Full item list (pending auth after RT fixes):**
- [ ] Ad-1: Radio labels → `"New Intake"` / `"Add Eggs or Bins to Existing Intake"`
- [ ] Ad-2: Sub-mode selector in supplemental (Add New Bin / Add Eggs to Existing Bin)
- [ ] Ad-3: Wire supplemental save path in `commit_all()`
- [ ] Ad-4: `"Intake Date"` label
- [ ] Ad-5: Step 1 read-only in supplemental mode
- [ ] Rm-1: Remove `Add Bin to Intake` expander + `sup_bin_mode` blocks from Observations
- [ ] Rm-2: Remove `Add Eggs to Existing Bin` expander from Observations
- [ ] Te-1: Update Observations tests (remove sidebar tool refs)
- [ ] Te-2: New supplemental intake path tests (including all 8 adversarial scenarios from RT-20)

### 🗄️ DO_NOT_FIX_YET — CR-20260429-221541 — bin_code / bin_id Separation
`change_requests/DO_NOT_FIX_YET_change_request_20260429221541.txt`
Major architecture refactor. Save for dedicated sprint. ~14.5 hours LOE.

---

## 🐞 KNOWN LIVE BUGS (not yet authorized to fix)

| Bug | Location | Notes |
|-----|----------|-------|
| `append_eggs()` missing `observer_name` | `3_Observations.py` ~line 184 | NOT NULL violation on every append save (RT-01) |
| `workbench_bins.add()` AttributeError | `3_Observations.py` line 416 | multiselect returns list; `.add()` crashes post-save (RT-08) |
| Intake dropdown includes soft-deleted intakes | `2_New_Intake.py` line 92 | bins can be added to ghost cases (RT-10) |
| `supp_date` stored but never used | `2_New_Intake.py` line 98 | eggs may get wrong intake date (RT-14) |
| FORENSIC finder backdoor | `2_New_Intake.py` line 224 | silently overwrites mass to 15.5 in all modes (RT-17) |

---

## 📋 FROM PREVIOUS SESSION (QA Test Suite — still pending)

**Status:** 99/112 tests passing (13 failing) — was active before this session

- [ ] Fix WF-0 Wipe: Debug 'OBLITERATE' button in `AppTest` (wipe_day1 click + RPC completion)
- [ ] Refactor Observation Selection: Use `at.checkbox[index].set_value(True)` in `test_clinical_record_lifecycles.py` and `test_mid_season_data_generator.py`
- [ ] Verify Reports Fahrenheit labels in downloaded CSV/JSON
- [ ] Reach 100% pytest pass rate

---

## 📁 KEY FILE LOCATIONS

| What | Where |
|------|-------|
| All change requests | `change_requests/` |
| Red team review | `reports/red_team_review_CR-20260429-225412.md` |
| Requirements.md | `docs/user/operators_manual_requirements.md` |
| Intake view | `vault_views/2_New_Intake.py` |
| Observations view | `vault_views/3_Observations.py` |
| DB schema | `supabase_db/turtledb_schema_generated_04282026.txt` |
| Migrations | `supabase_db/migrations/` |
| RPC (finalize intake) | `supabase_db/migrations/RPC_VAULT_FINALIZE_INTAKE.sql` |
| Test suite | `tests/` |

---

## 🎯 RECOMMENDED NEXT SESSION ORDER

1. **Audit `observer_name` constraint live in DB** (RT-01 pre-flight check)
2. **Fix RT-01, RT-07, RT-08, RT-10** — quick code-level bugs, no auth needed for the 2 already-deployed features
3. **Authorize and implement DC-01** (new RPC `vault_finalize_supplemental_bin`)
4. **Authorize and implement DC-02** (`intake_number` column migration)
5. **Authorize CR-20260429-224325** (Intake Date label + finder pre-pop + Lo-3 + Lo-4)
6. **Authorize CR-20260429-225412** with red team fixes applied
7. **Resume QA test suite** (13 remaining failures)
