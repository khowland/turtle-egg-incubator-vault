# 🐢 Project Requirements: Incubator Vault v8.0.0
**(Industry Best Practice & Clinical Sovereignty Edition)**

## 🌐 Project Scope & Framework
The **Incubator Vault** is a high-integrity clinical ledger designed for the Wildlife In Need Center (WINC). It adheres to **Industry Best Practices** for enterprise software engineering, focusing on data durability, system transparency, and biological accuracy.

*   **In-Scope**: Maternal intake, clinical incubation management, real-time biological triage, and hatching outcome recording (S0-S6).
*   **The Bridge (§1.2)**: Prenatal history is captured in the Vault until Stage S6 (Hatched), at which point data transitions to the **WormD** export pipeline.
*   **Infrastructure Standard**: Hosted on **Google Cloud Platform (GCP)** with a **Supabase (PostgreSQL)** backend, utilizing containerized Streamlit for maximum availability.

---

## 🏗️ 1. Software Engineering Standards
To ensure long-term maintainability for nonprofit staff, the following standards are mandatory:

1.  **Project Organization**: All technical documentation, migration guides, and specifications must reside in the `/docs` folder.
2.  **Naming Convention (§35)**: Strict adherence to `singular_snake_case` for all database columns and code variables (e.g., `target_total_weight_g`).
3.  **Atomic Transactions**: All multi-table clinical writes (e.g., Intake) must be wrapped in a single logical block with explicit "Incomplete" error logging to the `system_log`.
4.  **Decoupled Logic**: UI rendering and biological logic must be separated into dedicated utility modules (e.g., `utils/visuals.py`).

---

## 🩺 2. Clinical Workflow & Session Logic
*   **Session Persistence (§36)**: Implements a 4-hour "Global Resumption" window. Obsevers moving between devices adopt the active session ID to ensure shift continuity.
*   **Hydration Gate**: A mandatory "Weight Check" screen blocks access to the biological grid until the incubator's mass and water addition are recorded.
*   **Help & Manual**: The **Operator Manual** is directly accessible via a dedicated "Help" tab in the GUI, ensuring clinical protocols are always available.

---

## 🧬 3. Biological Entities & Storage
*   **Mothers (Cases)**: Master maternal record with species and health markers.
*   **Bins (Incubators)**: Physical containers with timestamp-precise IDs (`bin_id`).
*   **Eggs (Subjects)**: Individual biological subjects with developmental stages (S0-S6).
*   **Hatchling Ledger**: Final outcome records including `vitality_score` and `incubation_duration_days`.

---

## 🛡️ 4. Resilience & Security
*   **Soft Delete**: No clinical data is ever physically deleted. The `is_deleted` flag is the only mechanism for removal.
*   **Surgical Resurrection**: A dedicated admin mode for correcting observation errors and restoring archived bins without compromising audit integrity.
*   **Forensic Auditing**: Every row records `created_by_id`, `modified_by_id`, and `session_id` for absolute accountability.

---
*Verified for the 2026 Turtle Season.*