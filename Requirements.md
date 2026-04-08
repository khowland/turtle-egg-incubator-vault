# WINC Incubator Vault - Requirements & Specifications
Version: 7.2.0 - Biologist Workflow Optimization
Lead Biologist: Elisa Fosco

## 1. [Se] Session & Identity Architecture
- **Session Gate:** Splash screen forcing identity selection before app access (Vault Login).
- **Persistence:** Observer identity sticks for the duration of the browser session.
- **Environment Gate:** Observations require a mandatory **Restorative Hydration Check** once per session. Atmospheric humidity sensors are deprecated in favor of precision bin-weight tracking.
- **Auditing:** Every session must generate a unique `SessionID` propagated to all transaction tables for accountability.

## 2. [Ac] Actuator: Field Operations & Workflows
- **Directed Intake Wizard (The "Auto-Pivot"):**
  - **Step 1: Mother Identity** (Species, Name/Case Number, Clinical Status, Intake Date).
  - **Step 2: Bin Setup** (Substrate, Bin Label, Shelf Location, **Target_Total_Weight**). MUST support selecting an Existing Bin to accept incremental additions (Staggered Intake).
  - **Step 3: Egg Generation** (Quantity + Intake Source).
  - **Step 4: Atomic Commit:** Auto-pivot directly to the Initial (T0) Observation screen.
- **The "Daily Loop" (Observation Engine):**
  - **Step A: Restorative Hydration.** User logs `Current_Bin_Weight`. System calculates `Moisture_Deficit` (Target - Current). User logs `Water_Added`.
  - **Step B: High-Density Observation.** Tile-based grid for multi-selecting eggs.
  - **Step C: Batch Processing.** Slide-up Action Tray for bulk-applying Stage and Property updates.
- **The "Neonate Pivot" (Hatchling Transition):**
  - Changing an egg to **"Hatched"** status MUST trigger an automatic transition workflow.
  - Data from the egg record (Parentage, Duration) is flattened and pushed to a **Hatchling_Ledger** for rehab tracking.

## 3. [St] Storage & Biological Entities
- **3.1 Maternal Entities (The "Source")**
  - **Identifiers:** GUID + WormD Case Number (Regex validated).
  - **Attributes:** Species, Initial Weight, Intake Date, Clinical Status.
- **3.2 Bin Logic (The "Container")**
  - **Clinical Coding:** `{Last Name}-{WormD Case#} {SpeciesCode}{Occurrence}-{Bin#}`.
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