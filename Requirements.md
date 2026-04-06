PROJECT: TurtleEggDB (Streamlit / Supabase)
VERSION: 3.0 (Python Actuator)
TARGET: Streamlit Web UI (Optimized for Mobile/Desktop)
[St] STORAGE: Supabase (PostgreSQL)
ROOT: c:\dev\projects\turtle-db

---

## 1. PERSONA & MISSION
You are an **Expert Wisconsin Turtle Biologist**. 
You harvest eggs from dead or injured mother turtles at the **Wildlife In Need Center (WINC)**.
Your mission is to track these eggs through their lifecycle using a reliable, relational database.
The interface must be fast, high-contrast, and "wet-hand friendly" for field use.

---

## 2. DATABASE BACKEND (SUPABASE)
- **Persistence:** Use Supabase for the relational backbone.
- **Auto-Unpause Logic:** 
    - The project may go dormant in winter.
    - The Streamlit app must detect a "paused" state and trigger the **Supabase Management API** to wake it up.
    - Show a `st.spinner("Waking up the Incubator Vault...")` for 30–60 seconds if needed.
- **Auditing:** Every table must include `created_by_session`, `updated_by_session`, and `is_deleted` (Soft Delete).

---

## 3. SESSION MANAGEMENT
- **SessionID:** On app launch, generate a `session_id` using `[UserShortName]_[YYYYMMDDHHMMSS]`.
- **Observer Cache:** Use `st.session_state` to remember the current observer's name across page refreshes.
- **Logging:** Maintain a `SystemLog` for session starts, data entry events, and error traces.

---

## 4. DATA MODEL (CLUE CHAIN)
**[Lo] LOGIC: No abstract UUIDs for keys. Use Natural Keys.**
- **Mother ID:** `[MotherName]_[Species]_[YYYYMMDD]`
- **Bin ID:** `[MotherID]_B[Number]`
- **Egg ID:** `[BinID]_E[Number]`

### **DB Schema**
*Refer to the following tables (standardized for Supabase):*
- `SessionLog` (Audit)
- `SystemLog` (Traces)
- `mother` (Biological Asset)
- `bin` (Container)
- `egg` (Individual Unit)
- `IncubatorObservation` (Environment/Telemetry)
- `EggObservation` (Health Status)

---

## 5. UI INTERFACE (STREAMLIT ACTUATOR)
**Objective: Replace AppSheet with a native Python Streamlit UI.**

### **A. Global Navigation (Sidebar)**
- **Observer Identity:** Dropdown to select "Observations made by [Name]".
- **Status Dashboard:** Quick stats on "Active Eggs", "Pipping Ready", and "System Health".

### **B. Phase 1: Intake Wizard (The Burst Script)**
- **Bulk Entry:** A multi-step form to:
    1.  Select/Create Mother.
    2.  Define Bin (Harvest Date, Target Temp).
    3.  Enter `n` number of eggs.
- **Auto-Generation:** Streamlit automatically creates rows for all eggs and a baseline `EggObservation` for each.

### **C. Phase 2: Rapid Observation UI**
- **Bin Selector:** High-contrast list of active bins.
- **Multi-Select Eggs:** Use `st.multiselect` to choose one or many eggs for a single observation.
- **Quick-Edit Toggles:**
    - `Vascularity` (Checkbox/Toggle)
    - `Molding` (Toggle)
    - `Chalking` (Selectbox 0-2)
    - `Stage` (Selectbox: Intake -> Developing -> Established -> Mature -> Pipping -> Hatched)

### **D. Visualization & Analytics**
- **Health Indicators:** Color-coded dataframes (using `st.dataframe.style`) to highlight eggs with `Molding=True` or `Chalking=0` after 10 days.
- **Incubation Countdown:** Progress bars showing how close each egg is to its species-specific incubation window (60–90 days).

---

## 6. WORKFLOW & INTEGRITY
- **Anticipated Intake:** User inputs "Shelly_Blanding_20240501" -> System generates 15 egg records instantly.
- **Exporting:** "One-Click Export" to Google Sheets or CSV directly via Streamlit download buttons.
- **Field Use:** Ensure text is large and buttons are spaced for use with gloves/wet hands.

---

## 🛡️ GUARDRAILS
- **BIO-LOGIC:** If an egg is in `Mature` stage for > 60 days, show a Pulsing Red Warning.
- **ACCURACY:** Validate `session_id` is present before every COMMIT.
- **OFFLINE:** (Note: Streamlit is primarily online; ensure the server is responsive and the "Wake Up" logic is bulletproof).