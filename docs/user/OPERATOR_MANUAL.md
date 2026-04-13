![WINC Manual Cover Poster](../../assets/manual/operators_manual_cover_page.png)

---

# 🐢 WINC Sovereign Clinical Incubator System
## Operator's Guide and Clinical Protocol
**Release v10.5.1**

---

## 📖 PREFACE

### Audience
This guide is intended for clinical observers, field biologists, and system administrators responsible for the monitoring and health management of turtle embryos within the WINC Sovereign Vault.

### Documentation Accessibility
WINC is committed to providing accessible documentation. This manual is optimized for high-glare field environments and screen readers. For alternative formats, contact the System Administrator.

### Related Information
*   *WINC Maintenance and Deployment Guide*
*   *Biological Field Protocol v2026.4*

### Conventions
The following text conventions are used in this document:

| Convention | Meaning |
| :--- | :--- |
| **Boldface** | Indicates button names, menu items, or user interface fields. |
| `Monospace` | Indicates system identifiers, egg IDs, or technical variables. |
| *Italics* | Indicates emphasis, glossary terms, or references to other sections. |
| > [!NOTE] | Provides additional information or helpful tips. |
| > [!IMPORTANT] | Highlights critical clinical rules that must be followed. |
| > [!CAUTION] | Indicates actions that may result in data loss or subject risk. |

---

## 🏗️ 1. SYSTEM ARCHITECTURE

The WINC Clinical Incubator System is a sovereign data environment designed for maximum reliability in remote clinical settings.

*   **Clinical Vault (The Database)**: A hardened repository storing every biological signature and developmental transition.
*   **The Workbench (The Application Tier)**: A responsive interface optimized for the "5th-Grader" intuitiveness standard, ensuring clinical excellence even under stress.
*   **Audit Engine**: A background service that tracks every intake, observation, and state change to maintain case sovereignty.
*   **Data Residency**: All clinical records are stored within the project's dedicated cloud instance, ensuring that WINC maintains 100% ownership and control over the biological data (Sovereign Residency).

---

## 🏁 2. CORE OPERATIONS: IDENTITY AND SESSION

### 2.1 Starting a Shift
**Goal**: Establish an audit trail for clinical sessions and ensure data continuity.

**Prerequisites**: Observer must be registered in the system.

**Procedure**:
1.  Locate the **Observer Name** selection list on the entry screen.
2.  Select your name to initialize the session signature.
3.  **The 4-Hour Rule**: If you return to the system within four hours of your last activity, the system will automatically resumed your previous session.
    > [!NOTE]
    > This rule ensures that a single day's work is consolidated into one clean report rather than fragmented logs.
4.  Verify the status message: `"Session Active: [Your Name] is here."`

### 2.2 The Clinical Pulse (Dashboard)
**Goal**: Monitor real-time status and perform high-level resource management.

The Home screen (Dashboard) displays key biological indicators (KPIs):
*   **Active Subject Count**: Total embryos currently in the vault.
*   **Success Rate (Hatched)**: Total subjects that have reached S6.
*   **Critical Alerts**: A red indicator showing subjects with "Critical" (Level 3) Mold or Leaking observations.
*   **Hydration Status**: Percentage of bins that have passed the **Hydration Gate** in the current 24-hour cycle.

### 2.3 Season-End Archival (Cleanup)
**Goal**: Decommission empty bins once all subjects have hatched or been transferred.

**Procedure**:
1.  Locate the **Remove Empty Bins** interface on the dashboard.
2.  Select the target bin (Only bins with 0 active subjects are eligible).
3.  Activate the **Confirm Archival** toggle.
4.  Click **REMOVE BIN**.
    > [!CAUTION]
    > Archiving a bin removes it from the active workbench. Use the **Resurrection Vault** if a bin is archived prematurely.

---

## 📥 3. CORE OPERATIONS: CLINICAL INTAKE

### 3.1 Establishing Case Sovereignty
**Goal**: Transform a field discovery into a permanent clinical record.

**Procedure**:
1.  **Species Selection**: Select the subject species (e.g., *Blanding’s*, *Wood Turtle*).
2.  **The Clue-Chain ID Generation**: The system dynamically creates a unique identifier (e.g., `BL14-HOWLAND-1`).
    *   `BL`: Species Alpha-Code.
    *   `14`: Seasonal Sequence.
    *   `HOWLAND`: Finder/Case Holder Name.
    *   `1`: Target Bin Assignment.
3.  **Metric Documentation**: Record Mother's carapace length (mm) and extraction conditions.
4.  **Finalization**: Click **ESTABLISH CASE**.
    > [!CAUTION]
    > Clicking Establish Case creates the Mother, Bin, and unique Egg records (Baseline S0) in a single atomic transaction. Ensure all intake data is accurate before clicking.

---

## 🔬 4. THE CLINICAL WORKBENCH: OBSERVATIONS

### 4.1 The Hydration Gate
**Goal**: Ensure bin moisture levels are addressed before biological assessment begins.

**Protocol**:
1.  Access the Bin grid.
2.  Input the **Total Mass (g)** of the bin.
3.  Compare against the **Last Recorded Weight**.
4.  Add water as required by clinical assessment.
5.  Input the **Actual Water Added (ml)**.
6.  Click **START WORKING** to unlock the individual egg grid.

### 4.2 Biological Lifecycle Assessment
**Goal**: Record developmental markers and health indicators.

> [!IMPORTANT]
> **THE GOLDEN RULE: NEVER ROTATE EGGS.**
> Embryos are oriented to the top of the shell. Rotating an egg can result in developmental failure or drowning of the subject. Maintain original orientation during all weighing and candling.

**Procedures**:
1.  **Stage Assignment**: Determine the developmental stage from **S0** (Baseline) to **S6** (Hatched).
2.  **Property Matrix**: Record health sliders for **Mold**, **Leaking**, and **Denting** on a scale of 0 (Safe) to 3 (Critical).
3.  **Signature**: Save your observation to apply your digital signature and timestamp.

---

## 🐣 5. TRANSITION AND HATCHING

### 5.1 S6 Transition (Vitality Records)
**Goal**: Record the health markers at the moment of emergence.

**Procedure**:
1.  Select the subject egg in the workbench grid.
2.  Change the status to **S6 (Hatched)**.
3.  Assign a **Vitality Score**:
    *   **5 (Optimal)**: Strong, eyes open, active movement.
    *   **3 (Guarded)**: Lethargic or large yolk sac present.
    *   **0 (Failed)**: Death during pipping or emergence.
4.  System will automatically log the **Incubation Duration** (Days).

---

## ⚙️ 6. GOVERNANCE AND ADMINISTRATION

### 6.1 Registry Protection (Mid-Season Lock)
The **Mid-Season Lock** prevents accidental modifications to core registries (Species codes, Observer names) while active clinical work is in progress.

### 6.2 Data Resurrection Vault
If a bin or case is accidentally archived or deleted, use the **Resurrection Vault** to restore the subject record and its full history from the audit log.

### 6.3 Bio-Analytics and WormD Export
Navigate to the **REPORTS** module for:
*   **Mortality Heatmaps**: Identification of critical loss windows.
*   **WormD Export**: Standardized bundle generation (CSV/JSON) for data sharing with external biological agencies.

---

## 🆘 7. CONTINUITY AND DISASTER RECOVERY

### 7.1 Crisis Mode (Connectivity Failure)
In the event of network disruption:
1.  **DO NOT REFRESH** the browser window.
2.  Transition to **Physical Field Sheets** immediately.
3.  Maintain subject identifiers as generated by the system.
4.  Transcribe manual logs back into the system once the **Connectivity Restored** indicator is green.

---

## 📖 8. GLOSSARY AND VOCABULARY

*   **Chalking**: The white calcification of the shell during subject development.
*   **Mass Deficit**: Water loss through the shell membrane.
*   **Pipping**: The initial break of the shell by the hatchling.
*   **Sovereign Documentation**: Data that is archived locally and owner-controlled, preventing third-party platform lock-in.

---

**WINC Sovereign Documentation © 2026**  
*Platinum Rated. Clinical Excellence. Failure-Proof.*
