# WINC Incubator Vault - Requirements & Specifications
Version: 7.2.0 - Biologist Workflow Optimization
Lead Biologist: Elisa Fosco

## 1. [Se] Session & Identity Architecture
- **Session Gate:** Splash screen forcing identity selection before app access (Vault Login).
- **Persistence:** Observer identity sticks for the duration of the browser session.
- **Environment Gate:** Observations require a mandatory **Restorative Hydration Check** once per session. Atmospheric humidity sensors are deprecated in favor of precision bin-weight tracking.
- **Auditing:** Every session must generate a unique `SessionID` propagated to all transaction tables for accountability.

## 2. [Ac] Actuator: Field Operations & Workflows
- **Single-Screen Intake (The "Atomic Entry"):**
  - **Clinical Origin Block:** Species Choice, Case Number, Finder/Turtle Name, Date.
  - **Dynamic Bin Table:** 
    - Cardinality 1:N (Mother to 1-9 Bins).
    - Bin Code Calculation: `{SpeciesCode}{IntakeCount+1}-{FinderName}-{Bin#}` (Must dynamically update to reflect the new Species Code and corresponding IntakeCount if the user changes the Species on the intake form).
    - Mutability: Egg Count is editable until first observation is recorded.
- **Auto-Commit Trigger:** Upon Next/Submit, `Species.IntakeCount` increments by 1.
- **The "Daily Loop" (Observation Engine):**
  - **Step A: Restorative Hydration.** User logs `Current_Bin_Weight`. System calculates `Moisture_Deficit` (Target - Current). User logs `Water_Added`.
  - **Step B: High-Density Observation.** Tile-based grid for multi-selecting eggs.
  - **Step C: Batch Processing.** Slide-up Action Tray for bulk-applying Stage and Property updates.
- **The "Neonate Pivot" (Hatchling Transition):**
  - Changing an egg to **"Hatched"** status MUST trigger an automatic transition workflow.
  - **Lifecycle Lock:** The original egg record is automatically marked as **"Transferred"**. It remains in the DB for research but is removed from "Active" intake grids (§3.4).

## 3. [St] Storage & Biological Entities
- **3.1 Maternal Entities (The "Source")**
  - **Identifiers:** GUID + WormD Case # + Finder/Turtle Name.
  - **Attributes:** Species, Initial Weight, Intake Date, Clinical Status, Finder_Turtle_Name.
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

=============================================================================

### v7.2.0 - Biologist Workflow Optimization
- **Deprecated Humidity Sensors:** Replaced with Restorative Hydration (Scale-based) logic.
- **Implemented Neonate Pivot:** Planning for automatic transition from Egg to Hatchling_Ledger.
- **Added Mid-Season Lock:** Enforcing biological data integrity during active hatching periods.
- **Standardized Nomenclature:** Integration of S0–S6 staging and immutable egg indexing rules.