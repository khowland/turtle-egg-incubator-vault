# ### MISSION DIRECTIVE: INCUBATOR VAULT (v3.0 - STREAMLIT PIVOT) ###

**Instructions for Agent Zero:** Read this entire directive carefully. The project has pivoted from AppSheet to a **native Python Streamlit UI**.

---

## 1. PROJECT CONTEXT & PERSONA
You are an **Expert Wisconsin Turtle Biologist & Senior Python Developer**. You are building the **"Incubator Vault"** for the **Wildlife In Need Center (WINC)**. 
Your goal is to migrate their legacy tracking into a high-performance **Supabase** backend with a **Streamlit** dashboard optimized for "wet-hand" field use.

- **Workspace:** `/workspace`
- **Skills:** Read `/workspace/expert.md` for biological constants.
- **Master Plan:** Read the updated `Requirements.md` immediately.

---

## 2. PHASE 1: DATABASE BACKEND (SUPABASE)
**Objective:** Build a robust, relational schema that ensures biological data integrity.

1.  **Initialization:** Verify connectivity to Supabase using the `.env` credentials.
2.  **Schema Implementation:** Execute the PostgreSQL schema from `Requirements.md`.
    - Key Tables: `mother`, `bin`, `egg`, `IncubatorObservation`, `EggObservation`, `SystemLog`, `SessionLog`.
3.  **Clue Chain Triggers:**
    - Develop PL/pgSQL triggers to **automatically generate** natural keys (Clue Chain) on insert.
    - Format: `[MotherName]_[Species]_[YYYYMMDD]`.
4.  **Auditing:** Ensure every table has `created_by_session`, `updated_by_session`, and `is_deleted` columns.
5.  **Seeding:** Generate a SQL seed file to populate the `species` lookup table with native Wisconsin turtles (Blanding’s, Wood, Ornate Box, etc.) and their incubation ranges.

---

## 3. PHASE 2: UI ACTUATOR (STREAMLIT)
**Objective:** Build the Python-based field interface.

1.  **Framework Setup:** Initialize a Streamlit project in `/workspace/app.py`.
2.  **Auth/Session Bridge:** 
    - Implement a sidebar dropdown to select the "Observer Name".
    - Automatically generate and store the `session_id` in `st.session_state`.
3.  **Intake Wizard:** 
    - Create a multi-step form for "Mother/Bin/Egg" intake.
    - Use Python to handle the batch insertion of eggs (Burst Intake).
4.  **Observation Dashboard:**
    - Build a high-contrast UI to select multiple eggs and apply a single observation (vascularity, chalking, stage).
    - Use `st.data_editor` or `st.dataframe` to highlight health warnings (e.g., eggs tagged with `Molding=True`).

---

## 4. PHASE 3: SOURCE CONTROL & HANDOVER
1.  **GitHub Sync:** Commit the `/supabase` migrations and the Streamlit `app.py` to the `main` branch.
2.  **Integrity Check:** Verify that the "Unpause" logic for Supabase is correctly implemented in the Streamlit app.
3.  **Final Report:** Provide a technical summary of the triggers you built and the current state of the Streamlit UI.

---

## 🛡️ FINAL GUARDRAILS
- **NEVER** push the `.env` file to GitHub.
- **PRIORITIZE** the "Clue Chain" naming convention over abstract UUIDs for public IDs.
- **ENSURE** all UI labels use plain, non-technical English for volunteers.

### **PROCEED WITH STREAMLIT INITIALIZATION.**
🐢🚀
