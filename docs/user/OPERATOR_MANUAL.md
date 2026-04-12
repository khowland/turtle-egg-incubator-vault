# 🐢 WINC Clinical Incubator Operating System (CIOS) v10.0
## "The Clinical Bible" — Sovereign Reference Manual

**North Star Objective:** To provide a screen-by-screen tactical manual that transforms physical clinical workflows into simple, failure-proof digital steps—ensuring every staff member knows exactly what data to enter, where to enter it, and why it matters to the mission.

---

### 📑 TABLE OF CONTENTS
1.  **📟 DASHBOARD**: Real-Time Operational Awareness
2.  **📥 INTAKE**: Accessioning & Smart-ID Generation
3.  **🥚 EGGS & BINS**: Inventory Management
4.  **🔍 OBSERVATIONS**: The Daily Maintenance Round
5.  **🐣 HATCHLINGS**: The Transition Ledger
6.  **📉 REPORTS**: Forensic Audit & Data Exports
7.  **🛠️ ADVANCED WORKFLOWS**: (Batch & Injured Mother Use-Cases)
8.  **🆘 TROUBLESHOOTING**: Correcting Mistakes

---

### 1. 📟 DASHBOARD: The Command Center
**The Goal:** Use this screen to instantly identify which eggs or bins require immediate biological intervention.

*   **Help Needed Metric:** If this number is greater than zero, eggs are currently in a "Molding" or "Leaking" state.
*   **Active Inventory:** A real-time count of all living subjects currently in the vault.

**Tactical Step:** Check the **Health Alerts** section first thing every morning. If an alert is red, proceed immediately to the **Observations** page for that Bin.

---

### 2. 📥 INTAKE: Accessioning
**The Goal:** Legally and clinically enroll a Mother turtle into the WINC registry.

**Standard Workflow (New Case):**
1.  Select **Species**.
2.  Enter **Mother Name** (Internal WINC label or Case Number).
3.  Enter **Intake Date** and **Condition Notes**.
4.  **Click [Complete Intake]**: This generates the unique **Mother ID** used for all child records.

**The "Why":** Without a Mother ID, the system cannot link eggs to their genetic lineage.

---

### 3. 🛠️ ADVANCED WORKFLOWS
**The Goal:** Handle non-standard biological events without corrupting the database.

#### A. The "Batch Intake" (Efficiency)
When processing 50+ eggs, do not enter them separately.
*   **Workflow:** Use the **Bulk Enrollment** tool on the Egg Ledger page. Enter the total count, and the system will auto-increment suffixes (e.g., -01, -02).

#### B. The "Injured Mother" (Delayed Clutch)
**Use Case:** An injured mother is held in the clinic and provides a second clutch 3 days after the first.
1.  **DO NOT** create a new Mother record.
2.  Search for the existing **Mother ID**.
3.  Select **[Add New Bin to Existing Case]**.
4.  Populate the new bin with the secondary clutch.
*   **Success Measure:** The system shows two Bins (Bin A & Bin B) under a single Mother ID.

---

### 4. 🔍 OBSERVATIONS: The Daily Round
**The Goal:** Record the biological trajectory of each egg using the 0–3 Clinical Scale.

**The Health Slider Logic:**
*   **0 (Clean):** No visible mold, leaks, or dents.
*   **1 (Trace):** Minimal fuzzy growth or slight fluid glistening.
*   **2 (Moderate):** Significant mold requiring sanitation; clear moisture deficit (dent).
*   **3 (Critical):** Immediate isolation required; high risk of non-viability.

**Weight Gate:**
*   If the system displays a **Negative Mass Deficit**, you must add water to the substrate until the weight matches the **Target Weight** displayed on the screen.

---

### 5. 🆘 TROUBLESHOOTING: Fixing Mistakes
**I entered the wrong egg weight:**
*   Navigate to the Observations grid, find the timestamped entry, and use the **[Edit]** tool (Admin only) or enter a **New Corrective Observation** immediately. The system prioritizes the most recent timestamp.

**An ID was generated for a non-existent egg:**
*   Set the status to **"Void/Error."** Do not attempt to re-use the ID for a different egg, as this breaks the audit trail.

---

<div style="page-break-after: always;"></div>

**WINC Sovereign Documentation © 2026**  
*Validated by SME, SWE, and Technical Writing Master Editor.*
