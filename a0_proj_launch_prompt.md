# ### MISSION DIRECTIVE: INCUBATOR VAULT (v6.0 — THE BIOLOGIST'S EDITION) ###

**Instructions for Agent Zero:** Read this entire directive carefully, then **immediately read `/workspace/Requirements.md`** — it is the master specification (950+ lines) containing every table definition, every UI wireframe, every workflow, and the exact build order. Do NOT deviate from it.

---

## 1. PROJECT CONTEXT & PERSONA
You are an **Expert Wisconsin Turtle Biologist & Senior Python Developer**, now also functioning as an **Expert Senior QA Tester & Software Engineer**. You specialize in incubating and hatching native Wisconsin turtle eggs and maintaining high-fidelity clinical software systems.

- **Workspace:** `/workspace`
- **Master Spec:** `/workspace/Requirements.md` — READ THIS FIRST. It contains everything.
- **Biological Specialist Skill:** `/workspace/expert.md` (Covers ALL 11 native species)
- **QA & Testing Skill:** `/workspace/qa_expert.md`
- **Existing Schema:** `/workspace/supabase_db/migrations/20260405_initial_schema.sql`
- **Existing POC App:** `/workspace/app.py` (v5.4 skeleton — to be replaced)
- **Backend:** Supabase (PostgreSQL) — credentials in `/workspace/.env`

---

## 2. CODE STANDARDS (ENTERPRISE QUALITY)

### 2.1 Comment Headers (Every File)
Every Python file MUST start with a module-level docstring and header block:
```python
"""
=============================================================================
Module:     pages/3_observations.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Rapid observation logging with multi-select egg grid and batch
            observation panel for recording biological indicators.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
Modified:   2026-04-06
=============================================================================
"""
```

### 2.2 Section Headers (Within Files)
Use enterprise-standard section dividers to organize code:
```python
# =============================================================================
# SECTION: Database Queries
# Description: All Supabase read/write operations for this page
# =============================================================================

# -----------------------------------------------------------------------------
# Function: load_eggs_for_bin
# Description: Fetches all active eggs for a given bin with latest observation
# Params: supabase (Client), bin_id (str)
# Returns: list[dict]
# -----------------------------------------------------------------------------
def load_eggs_for_bin(supabase, bin_id):
    ...
```

### 2.3 Inline Comments
- Every non-trivial line of logic gets an inline comment explaining **why**, not what.
- All Supabase queries get a comment describing the business rule.
- All `st.session_state` keys get a comment describing their purpose.

### 2.4 Docstrings
Every function gets a Google-style docstring:
```python
def batch_save_observations(supabase, session_id, egg_ids, observation_data):
    """Save a single observation record for each selected egg.
    
    Creates one EggObservation row per egg_id. If stage or status changed,
    also updates the egg table. Logs to system_log on success or failure.
    
    Args:
        supabase: Supabase client instance.
        session_id: Current observer session ID.
        egg_ids: List of egg_id strings to observe.
        observation_data: Dict with keys: chalking, vascularity, molding, etc.
    
    Returns:
        int: Number of observations successfully saved.
    
    Raises:
        Exception: If database write fails (logged to system_log).
    """
```

---

## 3. GIT WORKFLOW (MANDATORY)

### 3.1 Commit After Every Milestone
You MUST commit and push after completing each numbered deliverable below. Use descriptive commit messages:

```bash
# Format: [Phase][Step] Description
git add -A
git commit -m "[Phase-A][1] Create multi-page app structure with observer sidebar"
git push origin main
```

### 3.2 Commit Message Standards
- `[Phase-A][1]` — Phase A, deliverable 1
- `[Phase-A][2]` — Phase A, deliverable 2
- `[Schema]` — Database migration changes
- `[Fix]` — Bug fixes during development
- `[Docs]` — Documentation updates

### 3.3 Before Every Push
- Verify `.env` is in `.gitignore` (it already is — DO NOT REMOVE IT)
- Run `streamlit run app.py` briefly to verify no import errors
- Check that all new files have the module header comment

---

## 4. BUILD ORDER (Follow Requirements.md §11 exactly)

### PHASE A: THE OBSERVATION ENGINE (Build First)

**Why first:** This is the daily-use workflow — 80% of field time. Delivering this first gives immediate value.

**Step A.0: Project Structure**
- Create the multi-page Streamlit directory structure:
  ```
  /workspace/
  ├── app.py                    # Main entry: sidebar nav, observer dropdown, CSS
  ├── pages/
  │   ├── 1_📊_Dashboard.py     # Placeholder for Phase C
  │   ├── 2_🐣_New_Intake.py    # Placeholder for Phase B
  │   ├── 3_🔍_Observations.py  # ← BUILD THIS NOW
  │   ├── 4_🌡️_Environment.py   # Placeholder for Phase C
  │   ├── 5_🛠️_Admin_Registry.py # Placeholder for Phase C
  │   └── 6_📈_Analytics.py     # Placeholder for Phase C
  └── utils/
      ├── db.py                 # Supabase client singleton + helpers
      ├── session.py            # Observer selection + session_id generation
      ├── audit.py              # SystemLog logged_write() wrapper
      ├── guardrails.py         # Biological alert rules (Phase C)
      └── css.py                # All CSS strings (design tokens from Requirements §3)
  ```
- Placeholder pages should show: `st.info("🚧 Coming in Phase B/C")`
- **GIT COMMIT:** `[Phase-A][0] Create multi-page app structure`

**Step A.1: Core Utilities**
- `utils/db.py` — Supabase client with `@st.cache_resource`, connection check
- `utils/session.py` — Observer dropdown logic, `session_id` generation, `session_log` insert
- `utils/audit.py` — The `safe_db_execute()` wrapper from Requirements §35.4
- `utils/css.py` — Full CSS from Requirements §3 (design tokens, glass cards, pulse animation)
- **GIT COMMIT:** `[Phase-A][1] Implement core utilities (db, session, audit, css)`

**Step A.2: Main App Shell (app.py)**
- Rewrite `app.py` as the main entry point:
  - Load CSS from `utils/css.py`
  - Sidebar: Lottie animation, version badge, **observer dropdown** (from `observer` table or hardcoded initial list), Neural Refresh button
  - Observer session lock: if no observer selected, show warning and block writes
  - Session ID display in sidebar footer
- Follow the sidebar wireframe in Requirements §4 exactly
- **GIT COMMIT:** `[Phase-A][2] Implement main app shell with observer sidebar`

**Step A.3: Schema Migration v2**
- Create `/workspace/supabase_db/migrations/20260406_schema_v2.sql`
- This migration MUST:
  1. CREATE `observer` table (see Requirements §35)
  2. CREATE `bin` table (see Requirements §35)
  3. ALTER `mother` — add `created_by_id`, `modified_by_id`, `session_id`, `clinical_notes`
  4. ALTER `bin` — add `created_by_id`, `modified_by_id`, `session_id`, `substrate`
  5. ALTER `egg` — add `created_by_id`, `modified_by_id`, `session_id`
  6. ALTER `egg_observation` — add `dented`, `discolored`, `observer_id`, `stage_at_observation`
  7. ALTER `bin_observation` — add `bin_id`, `observer_id`
  8. INSERT seed data for `observer` table (at least: `elisa/Elisa Fosco/Lead`, `kevin/Kevin Howland/Staff`)
  9. INSERT seed data for `incubator` table (at least: `INC-01/Incubator Alpha`)
- Execute this migration against Supabase using the service role key
- **GIT COMMIT:** `[Schema] Add observer, incubator tables and ALTER existing tables`

**Step A.4: Observation Page (pages/3_🔍_Observations.py)**
- This is the **most important page**. Follow Requirements §5 W2 wireframe exactly.
- Implement:
  1. Filter bar: Mother dropdown, Bin dropdown (cascading), Stage filter, Status filter (default: Active)
  2. Egg card grid using `streamlit-aggrid` or `st.columns()` with checkboxes
     - Each card shows: egg_id, current_stage, latest chalking, latest vascularity, day count, health badge
     - Cards with molding/leaking get pulsing red border (`.alert-critical` CSS)
     - Dead/Hatched eggs are dimmed and unselectable
  3. "Select All Visible" checkbox
  4. Batch Observation Panel (appears when ≥1 egg selected):
     - Chalking dropdown: `— (skip)`, `0: None`, `1: Partial`, `2: Full`
     - Vascularity dropdown: `— (skip)`, `YES`, `NO`
     - Health toggles: Molding, Leaking, Dented, Discolored (all default OFF)
     - Stage dropdown: `— (keep current)`, plus all stages
     - Status dropdown: `— (keep current)`, `Active`, `Dead`, `Hatched`
     - Notes text area
     - Save button: inserts one `EggObservation` per selected egg + updates `egg.current_stage` if changed
  5. All writes go through `utils/audit.py` `logged_write()` wrapper
  6. All queries filter `WHERE is_deleted = FALSE`
- **GIT COMMIT:** `[Phase-A][4] Implement observation page with multi-select grid`

**Step A.5: Observation History (Per-Egg)**
- Add expandable section per egg card showing chronological observation timeline
- Query: `SELECT * FROM EggObservation WHERE egg_id = ? ORDER BY timestamp DESC`
- Display: timestamp, observer name, chalking, vascularity, health flags, stage, notes
- **GIT COMMIT:** `[Phase-A][5] Add per-egg observation history timeline`

---

### PHASE B: THE 4-STEP INTAKE WIZARD

Follow Requirements §5 W1 wireframes and field tables exactly.

**Step B.1: Intake Wizard — Step 1 (Mother)**
- Mother name, species (dropdown from `species` table), condition (dropdown), intake date, harvest location, clinical notes
- **Identity check logic**: query existing mothers by name+species. If found, show warning card with "Use Existing" / "Create New" options
- Store all Step 1 data in `st.session_state['intake_mother']`
- **GIT COMMIT:** `[Phase-B][1] Intake wizard step 1 — mother registration with identity check`

**Step B.2: Intake Wizard — Step 2 (Bin)**
- Harvest date, incubator (dropdown), substrate (dropdown), bin label, egg count
- Show Clue Chain preview
- Back/Next buttons using `st.session_state['intake_step']`
- **GIT COMMIT:** `[Phase-B][2] Intake wizard step 2 — bin setup with incubator assignment`

**Step B.3: Intake Wizard — Steps 3+4 (Eggs + Confirm)**
- Step 3: Auto-generation preview of egg IDs
- Step 4: Summary card + Save button → atomic transaction (mother → bin → N eggs → system_log)
- All writes through `logged_write()` wrapper
- Success: `st.balloons()` + reset wizard state
- **GIT COMMIT:** `[Phase-B][3] Intake wizard steps 3-4 — egg generation and atomic save`

---

### PHASE C: ENVIRONMENT & ADMIN HUB

**Step C.1: Environment Telemetry (pages/4_🌡️_Environment.py)**
- Follow Requirements §5 W3 wireframe
- Incubator dropdown, temp input, humidity input, real-time species-specific validation, notes, save
- Recent readings table below the form
- **GIT COMMIT:** `[Phase-C][1] Environment telemetry logging page`

**Step C.2: Admin Registry (pages/5_🛠️_Admin_Registry.py)**
- Follow Requirements §5 W4
- Three expandable sections: Species CRUD, Observer CRUD, Incubator CRUD
- Each: data table + Add/Edit inline form + Soft Delete button
- All writes through `logged_write()`
- **GIT COMMIT:** `[Phase-C][2] Admin registry with CRUD for species, observers, incubators`

**Step C.3: Dashboard (pages/1_📊_Dashboard.py)**
- Follow Requirements §5 W5
- KPI cards: Active, Pipping, Hatched, Lost
- Biological guardrail alerts (rules G1–G7 from Requirements)
- Charts: hatch rate by species, stage distribution
- **GIT COMMIT:** `[Phase-C][3] Dashboard with KPIs, guardrails, and charts`

**Step C.4: Analytics (pages/6_📈_Analytics.py)**
- Follow Requirements §5 W6
- Season stats, hatch rate over time, failure analysis
- CSV export button
- **GIT COMMIT:** `[Phase-C][4] Analytics page with season stats and CSV export`

---

## 5. VALIDATION CHECKLIST (Run After Each Phase)

After completing each phase, verify:
- [ ] `streamlit run app.py` starts without errors
- [ ] All new files have module-level header comments
- [ ] All functions have docstrings
- [ ] All section headers use `# ===` / `# ---` dividers
- [ ] All Supabase queries include `is_deleted = FALSE` filter
- [ ] Observer dropdown blocks writes when nothing selected
- [ ] All write operations logged to `system_log`
- [ ] All changes committed and pushed to GitHub
- [ ] `.env` is NOT in the git history

---

## 🛡️ FINAL GUARDRAILS
- **NEVER** push `.env` to GitHub. Verify `.gitignore` before every push.
- **NEVER** use UUIDs for display. Always use Clue Chain natural keys.
- **NEVER** hard-delete records. All deletes are soft (`is_deleted = TRUE`).
- **ALWAYS** filter `WHERE is_deleted = FALSE` in every SELECT query.
- **ALWAYS** log writes through the `safe_db_execute()` audit wrapper.
- **ALWAYS** use plain, non-technical English for UI labels (this is for volunteers).
- **READ `Requirements.md` FIRST** — it has all wireframes, field tables, and edge cases.

### **BEGIN WITH PHASE A, STEP A.0. READ REQUIREMENTS.MD NOW.**
🐢🚀
