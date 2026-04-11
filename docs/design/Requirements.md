# 🐢 Project Requirements: Incubator Vault v8.1.0
**(Industry Best Practice & Clinical Sovereignty Edition)**

## 🌐 Project Scope & Framework
The **Incubator Vault** is a high-integrity clinical ledger designed for the Wildlife In Need Center (WINC). It adheres to **Industry Best Practices** for enterprise software engineering, focusing on data durability, system transparency, and biological accuracy.

*   **In-Scope**: Maternal intake, clinical incubation management, real-time biological triage, and hatching outcome recording (S0-S6).
*   **The Bridge (§1.2)**: Prenatal history is captured in the Vault until Stage S6 (Hatched). **Operator-initiated** export packages (flattened CSV and versioned JSON, best-effort WormD intake mapping) support handoff to external systems; full API automation is applied when agency schemas and credentials are available.
*   **Infrastructure Standard**: Hosted on **Google Cloud Platform (GCP)** with a **Supabase (PostgreSQL)** backend, utilizing containerized Streamlit for maximum availability.

---

## 🏗️ 1. Software Engineering Standards
To ensure long-term maintainability for nonprofit staff, the following standards are mandatory:

1.  **Project Organization**: All technical documentation, migration guides, and specifications must reside in the `/docs` folder.
2.  **Naming Convention (§35)**: Strict adherence to `singular_snake_case` for all database columns and code variables (e.g., `target_total_weight_g`).
3.  **Atomic Transactions**: Multi-table clinical writes (e.g., Intake) **prefer** a single database transaction via `vault_finalize_intake` RPC when deployed; legacy sequential writes remain as fallback with explicit **Incomplete Intake** logging to `system_log` on failure.
4.  **Decoupled Logic**: UI rendering and biological logic must be separated into dedicated utility modules (e.g., `utils/visuals.py`, `utils/wormd_export.py`).

---

## 🩺 2. Clinical Workflow & Session Logic
*   **Session Persistence (§36)**: Implements a 4-hour **global** resumption window: a new login within four hours of the last `session_log` entry **adopts the existing shift `session_id`** so observations group under one shift folder. **Authorship** remains on each row via `observer_id`.
*   **Hydration Gate**: A mandatory "Weight Check" screen blocks access to the biological grid until the incubator's mass and water addition are recorded.
*   **Help & Manual**: The **Operator Manual** is directly accessible via a dedicated "Help" tab in the GUI, ensuring clinical protocols are always available.
*   **Diagnostics**: The **Diagnostics** view is available only to trusted clinical roles (Admin, Staff, Biologist) from the main navigation.

---

## 🧬 3. Biological Entities & Storage
*   **Mothers (Cases)**: Master maternal record with species and health markers (including salvage-program context fields where captured).
*   **Bins (Incubators)**: Physical containers with timestamp-precise IDs (`bin_id`).
*   **Eggs (Subjects)**: Individual biological subjects with developmental stages (S0-S6).
*   **Hatchling Ledger**: Final outcome records including `vitality_score` and `incubation_duration_days`; rows are **created or updated** when eggs transition to S6 in the workbench.

---

## 🛡️ 4. Resilience & Security
*   **Soft Delete**: Clinical facts are not physically removed. **`is_deleted`** retires bins and cases; **`egg_observation`** rows are **voided** (`is_deleted` + optional `void_reason`) rather than hard-deleted. **Trusted clinical roles** (Admin, Staff, Biologist) may void observations, restore archives, retire bins, and run WormD-oriented exports.
*   **Surgical Resurrection**: Elevated mode on Observations to void individual observation records while preserving audit history; **Resurrection Vault** restores archived bins and cases.
*   **Forensic Auditing**: All **transactional clinical tables** in the ledger (`mother`, `bin`, `egg`, `egg_observation`, `bin_observation`, `hatchling_ledger`, etc.) record `created_by_id`, `modified_by_id`, and `session_id` where applicable. Reference lookups (e.g., `species`) follow the data dictionary in `SYSTEM_DESIGN_SPEC.md`.

---
*Verified for the 2026 Turtle Season.*
