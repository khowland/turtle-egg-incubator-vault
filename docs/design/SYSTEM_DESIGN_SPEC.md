# 🐢 WINC Incubator Vault: System Design Specification (v8.1.3)
**Technical Architecture, Data Dictionary, and Clinical Bill of Materials**

## 1. System Architecture Matrix
This diagram depicts the zero-deviation flow of biological data from high-mobility field tablets through the Streamlit application layer and into the hardened Supabase PostgreSQL ledger.

```mermaid
graph TD
    subgraph "Field Layer (Clinical Hub)"
        A[Biologist Tablet] -- "HTTPS/Streamlit" --> B[WINC Web App]
        A2[Volunteer Phone] -- "HTTPS/Streamlit" --> B
    end

    subgraph "Application Layer (GCP Runtime)"
        B -- "Identity Gate" --> C{Session Context}
        C -- "Active" --> D[Vault Logic Engine]
        D -- "Atomic Transaction" --> E[Supabase Client]
    end

    subgraph "Data Layer (Hardened PostgreSQL)"
        E -- "REST API" --> F[(Biological Ledger)]
        F -- "RLS Policies" --> G[Secure Storage]
    end

    subgraph "Maintenance Ops"
        H[Cloud Scheduler] -- "Heartbeat" --> I[Ping Utility]
        I -- "Prevention" --> F
    end
```

---

## 2. Module Dependency Hierarchy
The "Nervous System" of the application. This hierarchy governs how scripts inherit identity and connectivity.

```mermaid
graph LR
    BS[bootstrap.py] --> DB[db.py]
    BS --> SL[logger.py]
    BS --> SS[session.py]
    BS --> RB[rbac.py]
    BS --> VS[visuals.py]
    
    SS --> L["Welcome (0_Login.py)"]
    SS --> D["Home (1_Dashboard.py)"]
    SS --> I["Add New Eggs (2_New_Intake.py)"]
    SS --> O["Check on Eggs (3_Observations.py)"]
    SS --> S["Manage Staff (5_Settings.py)"]
    SS --> R["Download Data (6_Reports.py)"]

    style BS fill:#10b981,stroke:#333,stroke-width:2px
    style SS fill:#3b82f6,stroke:#333,stroke-width:2px
    style VS fill:#f59e0b,stroke:#333,stroke-width:1px
    style RB fill:#ef4444,stroke:#333,stroke-width:1px
```

---

## 3. Biological State Machine
Individual eggs progress through the ledger according to the following state logic. "Correction Mode" permits manual state reversal while maintaining the audit trail.

```mermaid
stateDiagram-v2
    [*] --> S0: Intake
    S0 --> S1: Early Dev
    S1 --> S2: Vascular
    S2 --> S3: Chalking
    S3 --> S4: Late Stage
    S4 --> S5: Pipping
    S5 --> S6: Hatched
    S6 --> [*]: Transferred
    
    S6 --> S5: Correction (Void Ledger)
    S5 --> S4: Correction
    S4 --> S3: Correction
```

---

## 4. Shift Continuity Timeline
The Vault unifies multi-observer activity during a 4-hour clinical window to ensure a coherent "Shift Folder" for forensics.

```mermaid
sequenceDiagram
    participant O1 as Observer A
    participant DB as Vault Ledger
    participant O2 as Observer B
    
    O1->>DB: Login (New Session ID: 101)
    DB-->>O1: Start Shift
    Note over O1,DB: 2 Hours Pass...
    O2->>DB: Login
    DB->>DB: Check Timestamp (< 4hrs)
    DB-->>O2: Adoption Path (Session ID: 101)
    Note right of O2: Shift adopted from Observer A
```

---

## 5. Data Dictionary (The Clinical Ledger)

### A. Audit Header Standard (§6.59)
Every transactional table in the ledger contains the following mandatory columns:
*   **`session_id`** (TEXT): The unique shift/session identifier.
*   **`created_at`** (TIMESTAMPTZ): Automatic record creation timestamp.
*   **`modified_at`** (TIMESTAMPTZ): Automatic last-edit timestamp.
*   **`created_by_id`** (UUID): FK to `observer.observer_id`.
*   **`modified_by_id`** (UUID): FK to `observer.observer_id`.
*   **`is_deleted`** (BOOLEAN): Soft-delete flag for clinical preservation.

### B. Session Continuity Protocol (§36)
The implementation utilizes a **Global Resumption** mechanism:
1.  **Persistence**: Browsing sessions are validated against the `session_log`.
2.  **Resumption**: Any new authentication within 4 hours of the *global* last activity adopts the existing `session_id`.
3.  **Traceability**: Session adoption unifies the "Shift Folder" in reporting while identifying multiple observers in shared shifts.

### C. Unified Vocabulary (v8.1.3 Standard)
The system mandates the following button labeling for cross-module consistency:
*   **`SAVE`**: Primary database commit action (Green).
*   **`CANCEL`**: Transaction abort/exit action (Red/Secondary).
*   **`ADD`**: Row or record creation (Blue).
*   **`REMOVE`**: Soft-delete or row removal action.
*   **`START` / `START WORKING`**: Gateway or check-in completion.

---

## 4. Hardware and Environment Specification
- **Incubator Topology**: SINGLE Physical Unit.
- **Organization**: Multiple "Bins" (Containers) per Incubator.
- **Terminology**: The word "Incubator" is reserved for the machine; "Bin" is used for the plastic egg boxes.

---

## 5. Software Bill of Materials (SBOM)

### Core Frameworks
*   **Streamlit (1.35+)**: Frontend user interface and navigation routing.
*   **Supabase (2.4+)**: Secure communication with the PostgreSQL backend.
*   **Pandas**: Analytical data processing.
*   **Plotly**: Interactive visualization.

---

## 6. Maintenance Protocol
*   **Heartbeat**: `scripts/heartbeat_ping.py` must be executed via Cron every 24 hours.
*   **Atomic Intake**: All clutches must be committed via `vault_finalize_intake` RPC to ensure maternal/bin/egg parity.
*   **Temporal Precision**: Eggs use `intake_timestamp` (TIMESTAMPTZ) for sub-second audit forensic tracking.

---
*Verified for v8.1.3 Production Release (2026 Season)*
