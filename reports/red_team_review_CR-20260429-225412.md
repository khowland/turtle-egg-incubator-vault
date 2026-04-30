# Red Team Review — CR-20260429-225412
**Reviewer:** Adversarial Engineering Review  
**Date:** 2026-04-29  
**Status:** BLOCKING ISSUES FOUND — DO NOT AUTHORIZE UNTIL RESOLVED  
**Files Reviewed:** `vault_views/2_New_Intake.py`, `vault_views/3_Observations.py` (full source), `supabase_db/migrations/RPC_VAULT_FINALIZE_INTAKE.sql`, `turtledb_schema_generated_04282026.txt`

---

## Executive Risk Summary

This CR consolidates two working (if imperfect) workflows into a single screen. The consolidation goal is correct. However, the plan as written contains **5 blocking issues** that will cause silent data corruption or hard production failures on real clinical data, **7 high-severity gaps**, and **9 additional risks** that are not addressed. The primary danger is that the code being ported from `3_Observations.py` already contains live bugs — and the CR plan does not flag them for correction during the port.

| Severity | Count |
|---|---|
| 🔴 BLOCKING — data corruption or hard failure | 5 |
| 🟠 HIGH — production failure under specific conditions | 7 |
| 🟡 MEDIUM — incorrect behavior, bad UX, or test gap | 9 |

---

## 🔴 BLOCKING ISSUES

### RT-01 — `append_eggs()` Has a Live DB Constraint Violation That Will Be Ported

**File:** `3_Observations.py` lines 179–190  
**Schema:** `bin_observation.observer_name TEXT NOT NULL` (confirmed in schema)

The `append_eggs()` function inserts a `bin_observation` recalibration record **without** an `observer_name` field:

```python
get_resilient_table(supabase, "bin_observation").insert({
    "bin_observation_id": str(uuid.uuid4()),
    "session_id": ...,
    "bin_id": target_b,
    "observer_id": st.session_state.observer_id,
    ...
    # observer_name is ABSENT
}).execute()
```

The `NOT NULL` constraint means this insert either **fails today in production** (throwing a Postgres error on every "Add Eggs to Existing Bin" save) or the constraint was relaxed in a migration that postdates the schema file. **Verify the actual live column definition before porting this code.** If the constraint is still active, the function is currently broken and must be fixed during the port:

```python
"observer_name": st.session_state.get("observer_name", ""),
```

By contrast, `commit_sup_bin()` correctly includes `observer_name` (line 407). The inconsistency confirms this was missed in `append_eggs`, not deliberately omitted.

**Cross-check:** `vault_finalize_intake` RPC also omits `observer_name` from its `bin_observation` INSERT. If the constraint is live, the initial intake path is equally broken. This needs an immediate DB-level audit.

---

### RT-02 — `PENDING` Can Be Committed as a Real Bin ID

**File:** `3_Observations.py` lines 302, 365 / `2_New_Intake.py` line 171

In `commit_sup_bin`, the bin code is taken from the data editor row:
```python
new_bid = row.get("bin_id_preview", next_bin_id)
```
`next_bin_id` is initialized to `"PENDING"` and only updated if existing bin IDs parse as `{prefix}-{digit}`. Failure conditions that leave `next_bin_id = "PENDING"`:
- Intake has 0 bins (edge case: intake created but all bins deleted)
- Any existing bin_id has a non-digit trailing segment (legacy records)
- The intake query returns empty due to a transient DB error

There is **no guard** that blocks SAVE when `new_bid == "PENDING"`. A save with this code inserts `bin_id='PENDING'` and eggs `'PENDING-E1'`, `'PENDING-E2'`, etc. These cannot be corrected without a direct DB admin intervention.

In `2_New_Intake.py`, the same risk applies in supplemental mode: `bin_id_preview` shows `"PENDING"` when `finder_name` is empty (line 171). If Step 1 is hidden (Ad-5) before finder data is pre-populated, the data editor renders with `"PENDING"` bin codes and the existing duplicate-check logic (line 241–244) will **pass** (only one row, no duplicates), allowing a `PENDING` bin to be committed.

**Required fix:** Add an explicit guard before SAVE:
```python
if new_bid == "PENDING" or not new_bid:
    st.error("❌ Bin code could not be determined. Cannot save.")
    st.stop()
```

---

### RT-03 — `commit_all()` Validation Is Not Mode-Aware: Supplemental Save Is Permanently Blocked

**File:** `2_New_Intake.py` lines 216–221

```python
if not finder_name.strip():
    st.error("❌ Missing Information: Finder Name is required...")
    st.stop()
if not case_number.strip():
    st.error("❌ Missing Information: Please provide a WINC Case Number...")
    st.stop()
```

These validations run **unconditionally for all modes**. If Ad-5 (hide Step 1 in supplemental mode) is implemented by conditionally not rendering the Step 1 container, the `finder_name` and `case_number` widgets do not render. Their Streamlit session state keys retain their last-seen values — but the **local variables** `finder_name` and `case_number` are assigned from the widget return values at render time. If the widgets don't render, these variables are either undefined (NameError) or empty strings (if initialized before the conditional block).

Result: **Every supplemental SAVE attempt is blocked** by the case_number validation, or crashes with NameError, depending on implementation order.

The CR plan (Ad-5) recommends hiding Step 1 but **does not say to make these validations mode-aware**. This is the most likely implementation defect — it looks correct at code-review time because the validation logic exists, but it silently prevents the entire supplemental workflow from functioning.

**Required fix:** Wrap all Step 1 validations in `if intake_mode == "New Intake":`. Populate `finder_name`, `case_number`, `selected_species` from the selected existing intake's data when in supplemental mode.

---

### RT-04 — Supplemental Bin Code Uses Wrong Intake Number

**File:** `2_New_Intake.py` line 148, supplemental path

```python
next_intake_number = (selected_species.get("intake_count") or 0) + 1
```

This computes the **next new intake's ordinal** for the selected species — e.g., if there have been 3 Blanding's intakes, this equals 4. For supplemental mode, the bin code must use the **existing intake's ordinal** (3, to continue the `BL3-` prefix).

The `species.intake_count` field is a running total of all intakes for that species. The individual intake's number is embedded in its bin codes (e.g., `BL1-6E6E-1` → intake 1) but is **not stored as a discrete column** in the `intake` table. The CR plan acknowledges this and proposes either parsing from existing bin codes or deriving from `intake.intake_count` — but **`intake.intake_count` does not exist**. Only `species.intake_count` exists. The proposed formula in the plan is undefined.

If `next_intake_number` from the formula is used in supplemental bin code generation, the supplemental bin will get a code like `BL4-...` when it should be `BL3-...`, breaking the clinical identifier linkage.

The `3_Observations.py` workaround gets this right by parsing `rsplit('-', 1)` on existing bin IDs. The new implementation in `New_Intake.py` must replicate this approach, querying `bin` WHERE `intake_id = supp_intake_id` and parsing the prefix from existing bin codes.

**There is no fallback if the parsing fails** — the CR needs to define what happens for an intake with zero bins or unparseable bin codes.

---

### RT-05 — No Transaction Wrapping for Client-Side Supplemental Save Path

**File:** `3_Observations.py` `commit_sup_bin()` / proposed New_Intake.py equivalent

The initial intake path calls `vault_finalize_intake` — a single PostgreSQL transaction. The supplemental path makes **3–4 separate HTTP round-trips** to the Supabase REST API:

1. `INSERT INTO bin`
2. `INSERT INTO egg` (bulk)
3. `INSERT INTO bin_observation`
4. `INSERT INTO egg_observation` (bulk, missing from current but required per CR)

If any step fails after step 1 completes, the DB is left in a partial state:
- Step 2 fails → orphaned bin with no eggs (FK violation on any downstream query expecting eggs)
- Step 3 fails → bin and eggs exist, no baseline observation; Observations hydration gate fires indefinitely for this bin, blocking clinical work
- Step 4 fails → eggs exist with no S1 baseline; any stage-tracking query that assumes baseline existence will return incorrect results

`safe_db_execute` wraps the entire `commit_sup_bin()` function, but its error handling logs and re-raises — it does **not** roll back already-committed REST API calls.

**Required fix:** Either (a) create a `vault_finalize_supplemental_bin` RPC that wraps the supplemental inserts in a single Postgres transaction, or (b) implement explicit compensating deletes in the error handler. Option (a) is strongly preferred for a clinical system. The CR plan does not mention this.

---

## 🟠 HIGH SEVERITY

### RT-06 — Race Condition in Bin Number Derivation

Both `commit_sup_bin` and the proposed New_Intake.py path derive the next bin number by querying `MAX(existing bin nums)` and adding 1. Two concurrent supplemental bin additions to the same intake both read `max=2`, both derive `next=3`, both attempt `INSERT bin_id='BL1-6E6E-3'`. The second insert fails with a primary key violation.

The failure surfaces as an unhandled DB error mid-save. No retry logic exists. The clinical user sees a red error and must restart the workflow. The first user's bin was committed successfully; the second user's data is lost.

The RPC path is protected by `SELECT ... FOR UPDATE` on the species row. The supplemental path has no equivalent locking.

---

### RT-07 — Double-Submit Risk on SAVE Button

**File:** `2_New_Intake.py` line 215

```python
if btn_col2.button("SAVE", type="primary", use_container_width=True, key="intake_save"):
```

No `disabled=st.session_state.get("is_submitting", False)` parameter. The `is_submitting` flag is set **inside** `commit_all()` after the click is processed. A fast double-click before the first rerun fires two commit executions. For the initial intake path, the RPC's `FOR UPDATE` lock provides some protection against duplicate intakes. For the new client-side supplemental path, there is no such protection — a double-click creates duplicate bins and duplicate egg records.

The Observations screen SAVE button correctly uses `disabled=st.session_state.get("is_submitting", False)` (line 117). Apply the same pattern to `2_New_Intake.py`.

---

### RT-08 — `workbench_bins` Type Inconsistency Causes `AttributeError` on Supplemental Save

**File:** `3_Observations.py` lines 39, 243, 416

```python
# Line 39: initialized as Set
st.session_state.workbench_bins = set()

# Line 243: multiselect OVERWRITES it with a List
st.session_state.workbench_bins = st.multiselect(...)

# Line 416: commit_sup_bin calls .add() — Set method, not List method
st.session_state.workbench_bins.add(new_bid)  # AttributeError: 'list' object has no attribute 'add'
```

Any session where the Observations page has rendered the workbench multiselect (which it always does on load) will have `workbench_bins` as a `list`. If the user then triggers supplemental bin creation, `commit_sup_bin` calls `.add()` and crashes with `AttributeError` **after the bin, eggs, and bin_observation have already been committed to the DB** — leaving the records in the DB but the UI in an error state.

This is a **current production bug** in the Observations sidebar tool. The new New_Intake.py path navigates to Observations after save via `st.switch_page`. After the page switch, `workbench_bins` is a list (populated by the active case hydration at lines 52–60 using `.add()`). Actually wait — lines 52–60 call `.add()` on `workbench_bins`, which at that point has been set to `set()` at line 39 (since this is a fresh page render after switch). So the crash only occurs if supplemental save happens **during** an active Observations session, not on fresh load.

Regardless: the type inconsistency is a latent bug. The fix is to normalize in the multiselect assignment: `st.session_state.workbench_bins = set(st.multiselect(...))`. Also add workbench update logic to `_intake_success_ui` in New_Intake.py, setting `active_case_id = supp_intake_id` so Observations auto-hydrates the correct intake's bins.

---

### RT-09 — `active_case_id` Not Set for Supplemental Navigation

**File:** `2_New_Intake.py` `_intake_success_ui()` lines 246–264

After a successful supplemental bin save, `_intake_success_ui(first_bin_id, intake_id)` is called. `intake_id` would be `supp_intake_id`. The function sets `active_case_id = intake_identifier` (line 250) — **only if `intake_identifier` is passed**.

The proposed supplemental save path in the CR must pass `supp_intake_id` as the second argument. If it is not passed (or if the developer calls `_intake_success_ui(new_bin_id)` with one arg), `active_case_id` is not updated. The Observations page auto-hydration (lines 52–60) then has no `active_case_id` to query, the workbench does not populate, and the user lands on Observations with an empty workbench — the new bin is invisible unless manually searched.

The CR plan says "Navigate to Observations with new bin active" but does not specify this mechanism explicitly.

---

### RT-10 — Intake Query Does Not Exclude Soft-Deleted Records

**File:** `2_New_Intake.py` line 92

```python
res_cases = supabase.table("intake").select("intake_id, intake_name, finder_turtle_name").execute()
```

No `.eq("is_deleted", False)` filter. The Observations sidebar equivalent at line 70 correctly filters `.eq("is_deleted", False)`. A user can select a soft-deleted intake and add a new bin to it, creating a bin that belongs to a logically deleted case. This record will be invisible in filtered clinical views but exists in the DB — a silent data integrity hazard.

---

### RT-11 — Egg Append Race Condition (Concurrent Egg Addition to Same Bin)

**File:** `3_Observations.py` lines 140–158

```python
current = supabase.table("egg").select("egg_id", count="exact").eq("bin_id", target_b).execute()
start_num = current.count + 1
new_eggs = [{"egg_id": f"{target_b}-E{i}", ...} for i in range(start_num, start_num + egg_count)]
```

Two concurrent appends to the same bin both read `count=5`, both generate `E6` through `E(6+n-1)`, both attempt insert. PK violation on `egg_id`. Same structural problem as RT-06. A new RPC for the append path would solve both RT-05 and RT-11 simultaneously.

---

### RT-12 — `bin_observation_id` Format Divergence Creates Future Migration Trap

Three different formats are used for `bin_observation_id`:

| Location | Format |
|---|---|
| `vault_finalize_intake` RPC | `'BO-' \|\| bin_id \|\| '-' \|\| timestamp` (e.g., `BO-BL1-6E6E-1-20260429120000`) |
| `commit_sup_bin` (Observations) | `str(uuid.uuid4())` |
| `append_eggs` (Observations) | `str(uuid.uuid4())` |

The column is `TEXT NOT NULL` with a PK constraint — any format works today. But the RPC-generated format is **not a valid UUID**. Any future migration, audit query, or external integration that validates or parses `bin_observation_id` as a UUID will fail for all RPC-created records. The discrepancy also makes forensic auditing harder. The CR should standardize on `uuid.uuid4()` and update the RPC accordingly.

---

## 🟡 MEDIUM SEVERITY

### RT-13 — Session State Pollution on Mode Switch

When a user selects a case in supplemental mode, `supp_intake_id` and `supp_date` are written to session state (lines 97–98). If the user switches back to "New Intake" mode, these values persist. If the supplemental save branch checks `if 'supp_intake_id' in st.session_state` instead of `if intake_mode == 'Add Eggs or Bins to Existing Intake'`, a leftover `supp_intake_id` from a previous supplemental attempt would cause a new intake to use the wrong branch. Always gate on `intake_mode` string value, never on presence of session state keys.

---

### RT-14 — `supp_date` Is Stored but Never Used

**File:** `2_New_Intake.py` line 98

`st.session_state.supp_date = str(supp_date)` is set but never referenced in any save path. The actual intake date used in bin/egg inserts comes from local variables. If the intent was to use `supp_date` as the egg intake date for supplemental bins (distinct from the original intake date), this is a silent data integrity failure — eggs will be created with an incorrect intake date.

---

### RT-15 — Duplicate Bin Code Check Produces False Positive in Supplemental Mode

**File:** `2_New_Intake.py` lines 241–244

```python
previews = [r.get("bin_id_preview") for r in st.session_state.bin_rows]
if len(set(previews)) != len(previews):
    st.error("❌ Data Integrity Error: Duplicate Bin Codes detected...")
```

In supplemental mode, if Step 1 is hidden before finder data is pre-populated, all `bin_id_preview` values are `"PENDING"`. If the data editor has multiple rows, all show `"PENDING"` — the duplicate check fires as a false positive and blocks save.

Conversely, the check does **not** validate against existing bin codes already in the DB. A supplemental bin could generate a code that already exists (e.g., if the bin number parsing logic is wrong), pass the local duplicate check, and then fail with a PK violation at the DB level.

**Required:** The check should (a) exclude `"PENDING"` values from the duplicate set comparison, and (b) include a DB-level uniqueness query against existing bin codes for the selected intake.

---

### RT-16 — `data_editor` `bin_num` Reassignment Changes Codes After User Review

**File:** `2_New_Intake.py` lines 204–206

```python
for idx, r in enumerate(st.session_state.bin_rows):
    r["bin_num"] = idx + 1
```

If a user deletes a middle row in the dynamic `data_editor`, this reassigns `bin_num` for all subsequent rows, changing their `bin_id_preview`. The user saw and approved codes `BL1-ABC-1`, `BL1-ABC-3` — after reassignment they become `BL1-ABC-1`, `BL1-ABC-2`. The preview column doesn't update until the next widget rerun. The user submits thinking they're creating `BL1-ABC-3` but `BL1-ABC-2` is committed. For supplemental mode, this is worse — if the existing intake already has bins 1 and 2, the reassigned code `BL1-ABC-2` will collide.

---

### RT-17 — Forensic Backdoor Active in All Modes

**File:** `2_New_Intake.py` lines 224–226

```python
if finder_name.startswith("FORENSIC"):
    for r in st.session_state.bin_rows:
        r["mass"] = 15.5
```

This silently overrides all bin masses when finder starts with `"FORENSIC"`. In supplemental mode, `finder_name` will be pre-populated from the existing intake's `finder_turtle_name`. If any real finder's name begins with "FORENSIC" (unlikely but possible in clinical forensic salvage cases), this triggers incorrectly in production. The backdoor should be gated on a debug mode flag or removed from the supplemental path entirely.

---

### RT-18 — `num_rows` Strategy Undefined for Supplemental Data Editor

The Observations workaround uses `num_rows="fixed"` for the supplemental bin data editor (1 bin at a time). The New_Intake.py main form uses `num_rows="dynamic"`. The CR does not specify which to use for the supplemental path in New_Intake.py.

If `"dynamic"` is used, users can add multiple supplemental bins in one save. This creates N separate `INSERT bin` calls (or requires the RPC). If `"fixed"`, only one bin per operation — consistent with the Observations workaround but less efficient for multi-bin supplementals.

This is a product decision but must be made explicit before implementation. The race condition in RT-06 applies to all bins in a multi-bin supplemental save.

---

### RT-19 — Phase Gate Criteria Not Defined

The CR specifies Phase 1 must be "tested" before Phase 2 (removal of sidebar tools). In a clinical system, "tested" must mean:
- Specific test scenarios passing (Te-2 scenarios)
- Verified in staging against real intake data
- Confirmed with clinical staff that the workflow is usable

If Phase 2 removal happens before Phase 1 is validated by clinical users, there is a window where **no working supplemental workflow exists** — neither the old sidebar tools nor the new New_Intake.py path. For a live incubation system in season, this could mean lost clinical data if staff discover bins to add and have no tooling.

**Recommendation:** Define explicit phase gate criteria in the CR before authorization.

---

### RT-20 — Missing Test Scenarios in Te-2

The CR's test plan covers happy paths only. Required adversarial tests not listed:

| Test | Maps To |
|---|---|
| Save with `bin_id_preview = "PENDING"` must be blocked | RT-02 |
| Concurrent supplemental bin creation — second save must fail gracefully, not silently | RT-06 |
| Partial failure simulation (mock step 3 failure) — DB state must be clean | RT-05 |
| Supplemental to a soft-deleted intake must be blocked | RT-10 |
| Mode switch supplemental→new→supplemental — no state bleed | RT-13 |
| Double-click SAVE — only one bin created | RT-07 |
| `workbench_bins` is a list after page render — `.add()` must not crash | RT-08 |
| Supplemental with 0-bin intake — PENDING code handled | RT-02 |
| `observer_name` present in all `bin_observation` inserts | RT-01 |

---

## Design Decisions to Challenge

### DC-01 — Client-Side Sequential Inserts vs. RPC for Supplemental Path

The architectural inconsistency between the initial intake path (single RPC transaction) and the proposed supplemental path (client-side sequential HTTP calls) is the root cause of RT-05, RT-06, RT-07, and RT-11. The correct solution is a `vault_finalize_supplemental_bin` RPC that mirrors `vault_finalize_intake` in structure but accepts an existing `intake_id` instead of creating one. This eliminates the partial-failure class, moves race condition protection to Postgres-level locking, and creates a single authoritative code path for all bin creation logic.

### DC-02 — Intake Number Not Stored as a Column

The intake ordinal number (the `1` in `BL1-`) is reconstructable only by parsing existing bin codes. This is fragile. As the CR defers CR-20260429-221541 (bin_id separation), an `intake_number INTEGER` column on the `intake` table would eliminate RT-04, simplify bin code generation in all paths, and make the schema self-describing. Consider adding this column in a migration concurrent with this CR.

### DC-03 — Step 1 Hide vs. Render as Read-Only

The CR recommends hiding Step 1 in supplemental mode. An alternative is rendering Step 1 fields as **disabled/read-only widgets** pre-populated from the selected intake. This approach: (a) avoids the variable scope/NameError risk from hidden widgets, (b) keeps the validation logic mode-agnostic, (c) gives clinical staff visible confirmation of which case they are appending to. The UX cost is a slightly busier form, which is acceptable given the clinical stakes.

---

## Summary Checklist for Authorization

- [ ] **RT-01** Verify live `observer_name` constraint; fix `append_eggs()` bin_observation insert  
- [ ] **RT-01** Verify `vault_finalize_intake` RPC is not also violating this constraint  
- [ ] **RT-02** Add `PENDING` guard before SAVE in all supplemental paths  
- [ ] **RT-03** Make `commit_all()` Step 1 validation mode-aware  
- [ ] **RT-04** Derive intake number from existing bin code parsing, not `species.intake_count + 1`  
- [ ] **RT-05** Write `vault_finalize_supplemental_bin` RPC **OR** implement compensating deletes  
- [ ] **RT-06** Document race condition risk; consider RPC with locking as fix  
- [ ] **RT-07** Add `disabled=st.session_state.get("is_submitting", False)` to New_Intake.py SAVE button  
- [ ] **RT-08** Normalize `workbench_bins` to `set()` after multiselect assignment  
- [ ] **RT-09** Confirm `_intake_success_ui` passes `supp_intake_id` as `intake_identifier`  
- [ ] **RT-10** Add `.eq("is_deleted", False)` to intake dropdown query  
- [ ] **RT-13** Gate all supplemental branches on `intake_mode` string, not session state key presence  
- [ ] **RT-14** Ensure `supp_date` is used as egg intake date or remove it  
- [ ] **RT-15** Fix duplicate check to handle PENDING and check against DB  
- [ ] **RT-19** Define Phase 1 → Phase 2 gate criteria before authorization  
- [ ] **RT-20** Add adversarial tests to Te-2 test plan  

---

*Generated by adversarial engineering review against live source code.*  
*All line references are against commit state as of 2026-04-29 23:02 CST.*
