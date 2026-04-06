# TurtleEggDB: Analysis & Implementation Report (v5.0)

## Executive Summary
TurtleEggDB (Incubator Vault) is a biological tracking system for the **Wildlife In Need Center (WINC)**. The system uses a **Supabase (PostgreSQL)** backend with a web-based UI for field data entry, observation logging, and season analytics. The UI framework is under active evaluation — the current POC uses Streamlit, but production may use a more capable framework depending on agent team recommendations.

---

## 1. Design Analysis & Critique

### **Strengths (The "Biologist's Dashboard")**
- **Domain Specialization**: The "Clue Chain" key strategy (e.g., `[MotherName]_[Species]_[YYYYMMDD]`) remains a core requirement for field readability.
- **Python-Native Logic**: Full access to Python's ecosystem (Pandas for analytics, Supabase-py for direct DB management).
- **Bulk Intake**: "Burst" data entry where a single mother might produce 20+ egg records at once.
- **Living Mother Support**: Mothers who are alive and laying over multiple days can receive additional bins over time.

### **Pivotal Risks & Mitigations**
- **Offline Reliability (CRITICAL)**: The WINC incubator room may have variable connectivity. 
    - *Mitigation*: Ensure the Supabase backend is highly responsive and investigate local caching/sync-later patterns if offline stability becomes a major issue.
- **UI Responsiveness**: Must work on mobile devices with wet, gloved hands.
    - *Mitigation*: 65–75px touch targets, high-contrast design, minimal keyboard input.
- **Supabase Auto-Unpause**: Programmatically waking Supabase from a "paused" state is a top-of-app requirement.

---

## 2. Development Roadmap

### **Phase 1: Database & Backend (Supabase)**
1.  **Schema Implementation**: Execute the PostgreSQL DDL with normalized tables for `mother`, `bin`, `egg`, plus lookup tables for `species`, `observer`, `incubator`.
2.  **Key Triggers**: Implement the `PL/pgSQL` functions to auto-generate "Clue Chain" Display IDs.
3.  **Auditing Hooks**: Ensure the `SessionLog` and `SystemLog` tables are populated by every UI transaction.

### **Phase 2: UI Development**
1.  **Observer Sidebar**: Dropdown for selecting current observer — persists across all pages.
2.  **Intake Wizard**: Multi-step form (Mother → Bin → Eggs → Confirm) with identity check for returning living mothers.
3.  **Rapid Observation Grid**: Multi-select eggs → apply batch observations with health flag toggles.
4.  **Environment Logging**: Quick temp/humidity readings per incubator with species-specific validation.
5.  **Admin CRUD**: Full management for Species, Observers, Incubators lookup tables.

### **Phase 3: Analytics & Polish**
1.  **Dashboard**: Real-time KPIs and biological guardrail alerts.
2.  **Analytics**: Season reports with hatch rate, stage distribution, failure analysis.
3.  **Data Export**: One-click CSV export.

---

## 3. Immediate Next Steps
1.  **Finalize schema v2** — add `observer`, `incubator` tables and ALTER existing tables.
2.  **Evaluate UI framework** — determine if Streamlit POC should be promoted or replaced.
3.  **Build core workflows** — Intake Wizard and Observation Logger are the highest priority.

🐢🚀
