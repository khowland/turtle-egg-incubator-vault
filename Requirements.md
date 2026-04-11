# 🛡️ Project Requirements: Incubator Vault v7.9.4
# (Standard §35 & §36 Enforcement Edition)

## 🌐 Project Scope & Boundaries
*   **In-Scope**: Intake of mother turtles, clinical incubation management, real-time biological triage, and hatching outcome recording (S0-S6).
*   **Out-of-Scope**: Long-term juvenile care, wild release tracking, and pediatric health modeling.
*   **The Bridge (§1.2)**: Once an egg reaches Stage S6, it transitions to the **WormD** data export pipeline. The Vault serves as the authoritative source for prenatal history.

## 1. [Se] Session & Identity Architecture
*   **Session Gate**: Splash screen forcing identity selection (Vault Login).
*   **Persistence**: Observer identity sticks for the duration of the browser session.
*   **Auditing (§6.59)**: Every transactional table carries the standard audit header: `session_id`, `created_at`, `created_by_id`, `modified_at`, `modified_by_id`.
*   **Global Shift Continuity (§36)**: Any activity on the vault within 4 hours is unified under a single `session_id` to ensure clinical shift legibility.

## 2. [Ac] Actuator: Field Operations
*   **Clinical Intake Command**: Single-screen atomic transaction to establish Bins and Eggs.
*   **The Workbench Grid**: 4-column high-visibility grid for daily observations.
*   **Hydration Gate**: Mandatory weight check to unlock the biological grid.

## 3. [St] Storage & Biological Entities
*   **Mothers (Cases)**: Master biological source with clinical health markers.
*   **Bins (Incubators)**: Physical containers with mass and substrate metadata.
*   **Eggs (Subjects)**: Individual records with development stage and cached health markers (Vasc/Chalk).

## 4. [Lo] Logic & Auditing
*   **Forensic Narrative (§4.1)**: Every major success path is logged as a text entry in `system_log`.
*   **Surgical Correction (§4.2)**: One-click deletion of erroneous observations with automated biological state rollback.

## 5. [η] Resilience & Lifecycle (v7.9.7)
*   **§5.1 Two-Stage Retirement**: Dashboard-level detection of completed bins with dual-action confirmation (Toggle + Push).
*   **§5.2 Atomic Persistence**: No data is physically deleted; `is_deleted` is the only mechanism for removal.
*   **§5.3 Resurrection Vault**: UI-accessible archive to 'Un-retire' Bins or Case Intakes instantly.
*   **§5.4 Save Point Parity**: Due to soft-delete architecture, the current DB state is a permanent, persistent 'Save Point'.

## 6. Technical Stack
*   **Stack**: Streamlit (UI), Supabase (DB), Python (Logic).

### **§35. Enterprise Naming Standards (The Measuring Stick)**
To ensure clinical data integrity and software engineering excellence, the following naming conventions are mandatory across the entire stack (Database, API, and Code):

1.  **Table Naming**: Must be **Singular** and **Snake_case** (e.g., `bin_observation`, `egg_observation`, `session_log`).
2.  **Primary Key (PK) Convention**: Every table must utilize a contextual identifier following the pattern `{table_name}_id` (e.g., `egg_observation_id`, `mother_id`). Generic labels like `id` or `obs_id` are strictly prohibited.
3.  **Foreign Key (FK) Convention**: Must match the PK of the referenced table (e.g., `species_id`, `mother_id`). 
4.  **Authorship Metadata**: Every transactional table must include:
    *   `created_by_id`: UUID/Text FK to the `observer_id` who created the record.
    *   `modified_by_id`: UUID/Text FK to the `observer_id` who last edited the record.
    *   `session_id`: Tracking identifier for the specific field session.
5.  **Boilerplate Consistency**: Use `snake_case` for all column names and variables. Avoid acronyms; use full descriptive terms (e.g., `bin_weight_g` instead of `bw_g`).

### **§36. Global Shift Continuity Standard**
To maximize audit legibility for small teams, the Vault implements a shared-session model:
1.  **Shift Window**: 4 hours from the most recent database transaction.
2.  **ID Adoption**: New logins within the window adopt the previous `session_id`.
3.  **Cross-Actor Integrity**: While the `session_id` is shared, individual records maintain forensic accountability via `created_by_id` / `modified_by_id` columns, correctly identifying the specific Biologist who performed the work.
4.  **Transparency**: Resumed sessions are visually identified in the Command Center.