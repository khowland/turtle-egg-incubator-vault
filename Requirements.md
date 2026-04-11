# WINC Incubator Vault - Requirements & Specifications
Version: 7.5.0 - Egg Sovereignty & Chronological Audit Individualization
Lead Biologist: Elisa Fosco

## 1. [Se] Session & Identity Architecture
- **Session Gate:** Splash screen forcing identity selection before app access (Vault Login).
- **Persistence:** Observer identity sticks for the duration of the browser session. Furthermore, the UI must physically read/write the last authenticated user to disk (`last_user.txt`) to dynamically pre-sort the dropdown list, accelerating shared-tablet workflows between shifts.
- **Environment Gate:** Observations require a mandatory **Restorative Hydration Check** once per session. Atmospheric humidity sensors are deprecated in favor of precision bin-weight tracking.
- **Auditing (§6.59):** Every shift generates a unique `session_id`. To ensure clinical continuity, the system supports **Resilient Session Recovery**: if a user re-authenticates within 4 hours of their last activity, the app automatically resumes the previous `session_id` to maintain a contiguous audit thread.
- **Audit Columns:** All transactional tables MUST carry the following standard audit header: `session_id`, `created_at`, `created_by_id`, `modified_at`, `modified_by_id`.

## 2. [Ac] Actuator: Field Operations & Workflows
- **Single-Screen Intake (The "Atomic Entry"):**
  - **Clinical Origin Block:** Species Choice, Case Number, Finder/Turtle Name, Date.
  - **Dynamic Bin Table:** 
    - Cardinality 1:N (Mother to 1-9 Bins).
    - Bin Code Calculation: `{SpeciesCode}{IntakeCount+1}-{FinderName}-{Bin#}` (Must dynamically update to reflect the new Species Code, corresponding IntakeCount, and Finder Name in real-time if the user alters them on the intake form).
    - Mutability & UI: Egg Count is editable until first observation is recorded. The input must strictly be a numeric entry field (range 1-99) with NO +/- step controls. Users must directly type the number via keyboard for maximum data-entry efficiency.
- **Auto-Commit Trigger:** Upon Next/Submit, `Species.IntakeCount` increments by 1.
- **Individual Egg Sovereignty:** Every egg is its own chronological clock.
  - **Intake Date:** Stored at the `egg` level (not bin). This allows a single mother to have eggs in a single bin that come from different days/clutches while tracking each egg's incubation progress individually.
- **The "Daily Loop" (Observation Engine v7.5.0):**
  - **The Workbench:** Users "pin" bins pull for the shift to their session. Pinned bins persist for the session duration.
  - **Clinical Throughput Icons:** Bins display completion status via icons (🟢 Done, 🌓 Partial, ⚪ Pending) and a ratio (X/Y eggs observed in current shift).
  - **Visual Selection Grid:** Eggs are displayed in a compact grid with current-shift status badges (✅/⚪).
  - **Selection Verification:** A dynamic CSV bar displays the specific Egg IDs targeted for modification (e.g. `[E1, E4, E9]`).
  - **Hydration Lock:** Mandatory weight check per bin once per shift.
- **Supplemental Intake Logic:**
  - Support adding new bins to existing Case #/Animal records.
  - Support appending eggs to existing bins without restarting the intake form.
  - **Step A: Restorative Hydration.** User logs `Current_Bin_Weight`. System calculates `Moisture_Deficit` (Target - Current). User logs `Water_Added`.
  - **Step B: High-Density Observation.** Tile-based grid for multi-selecting eggs.
  - **Step C: Batch Processing.** Slide-up Action Tray for bulk-applying Stage and Property updates.
- **The "Neonate Pivot" (Hatchling Transition):**
  - Changing an egg to **"Hatched"** status MUST trigger an automatic transition workflow.
  - **Lifecycle Lock:** The original egg record is automatically marked as **"Transferred"**. It remains in the DB for research but is removed from "Active" intake grids (§3.4).

## 3. [St] Storage & Biological Entities
- **3.1 Maternal Entities (The "Source")**
  - **Identifiers:** GUID + WormD Case # + Finder/Turtle Name.
- **3.1 Species Registry (The "Biological Assets")**
  - **Internal ID (`species_id`):** Primary Key within the database. Hidden from end-user UI to prevent clinical confusion.
  - **Clinical Code (`species_code`):** Unique 2-character user-facing code (e.g., 'BL' for Blanding's). Editable by administrators and utilized in automated Bin ID generation.
  - **Attributes:** Common Name, Scientific Name, Vulnerability Status, Intake Counter.
  - **Clinical Coding:** `{SpeciesCode}{IntakeCount}-{FinderName}-{Bin#}`.
- **3.2 Bin Logic (The "Container")**
  - **Clinical Coding:** `{SpeciesCode}{IntakeCount}-{FinderName}-{Bin#}`.
  - **Metric Logic:** Uses "Target Total Weight" as the primary proxy for incubation hydration.
- **3.3 Egg Entity (The "Subject")**
  - **Index:** Immutable Integer (1–N). Re-indexing remaining eggs after terminal losses is strictly prohibited to maintain historical binary integrity.
  - **Terminal Protocol:** Selection of terminal properties (e.g., DIS, Exploded) triggers a soft-delete from active views.
- **3.4 Hatchling Entity (The "Output")**
  - **Table:** `Hatchling_Ledger`.
  - **Attributes:** Egg_ID Link, Hatch_Date, Hatch_Weight, Vitality Score (Yolk sac absorption status).

## 4. [Lo] Logic & Biological Context
- **Stage-Linked Lookups:** Properties are dynamically filtered based on the selected "Stage of Development" (S0–S6).
- **Mid-Season Lock (The "Drift Guard"):**
  - **Constraint:** Editing of Species, Stages, or Property lookup tables is locked while there are any records in the "Active" state.
  - **Seasonal Versioning:** Existing records remain anchored to the lookup version active at the time of observation.

## 5. [η] Resonance: Analytics & Reporting
- **Velocity Report:** Stage distribution across species.
- **Mortality Heatmap:** Stage-specific loss analysis to identify "Critical Windows."
- **Hydration Correlation:** Linking `Water_Added` frequency and volume to hatching success percentages.

## 6. Technical Stack & Integrity
- **Backend:** Supabase (PostgreSQL). Proper PK/FK enforcement.
- **Frontend:** Streamlit (v1.31+ Navigation API).
- **Audit:** Consistent enterprise headers and mandatory `Created_datetime` / `Modified_datetime` for all tables.
- **User Assistance:** Context-aware Help dialogues (fast, hard-coded components to avoid DB/CMS payload latency) will be available on all major interactive screens.
- **Accessibility:** The default system font size must be boosted (18px+) to accommodate mobile field tablets. The scale must be globally persistent and configurable via the Settings screen.
- **Audit Integrity (§6.59):** Transactional entity tables (`mother`, `bin`, `egg`) utilize the `created_by_session` column for primary audit linkage, while telemetry logs (`systemlog`, `eggobservation`) associate via the direct `session_id` column.
- **Change Management:** Change Requests (CR) are tracked via independent text files (`ChangeRequest_MMDD_HHMM.txt`). Agents must treat existing CRs as immutable and only execute their requirements upon explicit user command.

=============================================================================

### Observation Workflow Addendum (Phase 2)
- **Water Logic:** Water constraint is rigorously enforced as >= 0 (Add-Only). A calculated Moisture Deficit acts as the suggestion baseline.
- **Mandatory Baseline:** S0 (Intake) phase demands an initial verified physical observation: [Stage=S0, Chalking=0, Vascularity=False, Molding/Leaking explicitly False]. 
- **Visual Completion Cues:** Heavy multi-egg grids utilize a top-level **Bin Header Progress Bar** instead of individual UI egg color coding to prevent confusing "unobserved" with "biological warning".
- **Density Presentation:** 
  - Bin Metrics (Temp, Weight) are tightly pinned horizontally at the top workspace.
  - Historical constraints are simplified on the UI via comma-separated string codes, condensing previous egg audits to simple UI list-box strings (e.g., `Egg 14: [D4: S0-C0-V-]`).
- **Confirmation Layer:** Pending changes are grouped numerically by Egg ID to map directly to physical rows, avoiding property abstraction grouping.
- **Auto-Navigation:** Finalizing the New Intake instantly provisions the first array Bin into memory (`active_bin_id`) and transitions seamlessly to the Observation UI for unbroken data entry flow.