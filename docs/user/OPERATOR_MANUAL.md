# WINC INCUBATOR SYSTEM: OFFICIAL OPERATOR MANUAL
**Institutional Archive Edition | Version 10.5.1**

![WINC Manual Cover Page](../../assets/manual/operators_manual_cover_page.png)

---

## TABLE OF CONTENTS
1. [Sign-In: Starting Your Shift](#1-sign-in-starting-your-shift)
2. [Introduction to the Secure Data Network](#-introduction-to-the-secure-data-network)
3. [Intake: Adding New Mothers and Eggs](#2-intake-adding-new-mothers-and-eggs)
4. [Daily Checks: Recording Egg Health](#3-daily-checks-recording-egg-health)
5. [Lifecycle: Egg Development Stages](#4-lifecycle-egg-development-stages-s0-to-s6)
6. [Admin: Fixing Errors and Settings](#5-admin-fixing-errors-and-settings)
7. [Reports: Reading the Clinical Data](#-6-reports-reading-the-clinical-data-analytics)
8. [Crisis: When the Internet Fails](#-7-crisis-when-the-internet-fails-continuity)
9. [Glossary](#8-glossary)

---

## 1. SIGN-IN: STARTING YOUR SHIFT

Recording clinical data begins with identifying yourself to the database. This ensures that every entry is linked to a specific observer for accountability.

1.  **Select Your Name**: Pick your name from the observer registry.
2.  **Sign-In**: Click **[START]** to begin your session.
3.  **The 4-Hour Rule**: The system keeps you signed in for 4 hours. After 4 hours of inactivity, you must sign in again to start a new shift. This prevents unauthorized entries under your name if a tablet is left unattended.

### 1.3 Documentation Conventions
To help you find information fast, we use a specific "Visual Logic" system:

| Style | Clinical Meaning |
| :--- | :--- |
| **BRIGHT BOLD** | This is a real thing you see on the screen. It might be a button like **[SAVE]** or a field like **Mother Name**. |
| `Monospace Code` | This is a computer-specific code (like a Subject ID `BL-2026-001`) that must be read exactly as written. |
| 📘 **NOTE** | Helpful advice that makes your work faster or easier. |
| 🛑 **IMPORTANT** | A **MANDATORY** rule. Breaking this rule may risk the life of an embryo. |
| ⚠️ **CAUTION** | An action that might delete data or cause a system error. |

---

---

## 🏗️ INTRODUCTION TO THE SECURE DATA NETWORK

The WINC System is a secure, high-integrity database designed to protect turtle research data from loss or corruption.

### 1.4 The Three Pillars of the System
To use WINC correctly, you must understand how the pieces fit together:

#### Pillar A: The Database
This is where the actual records live. When you click **[SAVE]**, your data travels to a high-security container. Every piece of data has a "Timestamp" and a "Signature" (your name).

#### Pillar B: The Main App Screen
This is the simple screen you use on your tablet or phone. It has been designed for **Field Simplicity**, filtering out the noise so you can focus only on the eggs in front of you.

#### Pillar C: The Audit System
A background system that logs all changes for accuracy. If you correct an entry, the audit system keeps a copy of what you changed and why you changed it.

### 1.5 System Hierarchy: From Machine to Egg
WINC follows a "Family Tree" logic:
1.  **The Incubator**: The large physical machine in the lab.
2.  **The Bin**: The plastic box inside the machine.
3.  **The Mother**: The turtle that provided the eggs.
4.  **The Egg**: The individual life we are protecting.

---

---

## 2. INTAKE: ADDING NEW MOTHERS AND EGGS

When a mother turtle is found and eggs are collected, we must add the new records to the database. This creates a permanent digital history for the mother, her plastic bin, and every individual egg.

### 2.1 Standard Clinical Intake Workflow
Follow these steps to register a new discovery:

1.  **Species Identification**: Select the correct turtle type (e.g., *Blanding’s* or *Wood Turtle*).
2.  **Assign WINC Case #**: Type the year and the sequence number (e.g., `2026-003`).
3.  **Discovery Details**: Type the **Finder's Name** and where they found the turtle.
4.  **Automatic Record Creation**: Click **[SAVE]**. The database will automatically create 1 Mother record, 1 Bin record, and all individual egg records at once.

### 2.2 Multiple Bins for one Mother
If a mother turtle lays more eggs than will fit in one bin:
1.  Complete the first intake for **Bin 1**.
2.  Use the **ADD** function in the sidebar to link a second bin to the same Mother ID.

### 3.1 Choosing the Intake Path
Not every turtle arrives in the same way. Use the flowchart below to decide which path to take before you touch the screen.

![Intake Logic Flowchart](../../assets/manual/intake_logic_flowchart.png)

### 3.2 Standard Clinical Intake Workflow
Follow these steps to register a healthy discovery:

1.  **Species Identification**: Click the **Species** box. Choose the correct turtle type (e.g., *Blanding’s* or *Wood Turtle*). The system uses this to set the "Optimal Incubation Temp" alerts later.
2.  **Assign WINC Case #**: Type the year and the sequence number (e.g., `2026-003`). This is the "Master ID" for the mother.
3.  **Discovery Details**: Type the **Finder's Name** and where they found the turtle.
4.  **Maternal Metrics**: Type the **Mother's Weight (g)** and **Carapace Length (mm)** if required by the Lead Biologist.
5.  **Establishing Case**: Double-check your numbers. Then, click the big **[SAVE]** button.

> 📘 **NOTE**: When you click **[SAVE]**, the "Audit Robot" creates 1 Mother record, 1 Bin record, and up to 30 individual Egg records all at once. This is called an **Atomic Transaction**.

### 3.3 The DOA Salvage Protocol
If a turtle is found deceased (Dead on Arrival) but the eggs are still viable, follow this path:
1.  Set the **Condition** to **Dead (Salvage)**.
2.  Complete the same steps as above, but add a 📘 **NOTE** in the **Intake Notes** field about the location of the recovery.
3.  The system will flag this case as a **Salvage Recovery** in the final reports.

![New Intake Form Mockup](../../assets/manual/intake_form_mockup.png)

### 3.4 Multiple Bins for one Mother
Sometimes a mother turtle lays so many eggs that they won't fit in one plastic bin. 
1.  Complete the first intake for **Bin 1**.
2.  Go to the **Supplemental Intake** tools in the sidebar.
3.  Choose the same **Mother ID** and click **[ADD]** to create **Bin 2**.

> 🛑 **IMPORTANT: MOTHER ID VERIFICATION**: Before clicking **[SAVE]**, look at the physical tag on the mother turtle. Ensure it matches the **Mother ID** you selected in the app. Choosing the wrong ID will link your 30 eggs to the wrong biological parent in the permanent cloud records.

---

---

## 3. DAILY CHECKS: RECORDING EGG HEALTH

This screen is used for the daily monitoring of bin environment and individual egg growth. Every bin must be weighed before individual eggs are handled.

### 3.1 The Weighing Protocol (Clinical Unlock)
1.  **Mass Verification**: Take the physical bin to the scale. Type the weight in the **Current Total Mass (g)** box.
2.  **Compare to Target**: Look at the **Target Weight** listed on the screen.
3.  **Remediation Action**:
    -   **Weight is Low**: Add water (ml) to match the Target. Enter the amount in **Water Added**.
    -   **Weight is High (>5g Over)**: Do not add water. Open the bin lid for 2 hours for passive evaporation.
    -   **Weight is Very High (>15g Over)**: Immediately notify the Lead Biologist for a substrate swap.
4.  **Clinical Unlock**: Click **[SAVE]** to unlock the individual egg grid.

### 3.2 Biological Mandate: NEVER ROTATE
🛑 **IMPORTANT**: When you pick up an egg to check it, **NEVER TURN IT OVER.** Flip-risk: If you flip the egg, the embryo may drown in its own yolk.

### 3.3 Recording Health (The 0-3 Scale)
1.  **Select Eggs**: Select individual eggs or use the **[START]** button to select all pending.
2.  **Assign Stage**: Pick the current growth stage (e.g., S3M).
3.  **Set Health Scores**: Rate health markers from 0 (Normal) to 3 (Critical).
4.  **Save**: Click **[SAVE]** at the bottom to sign and record your work.

![Daily Checks Dashboard](../../assets/manual/daily_checks_dashboard.png)

### 3.4 Species-Specific Alert Thresholds
The database automatically flags bins that fall outside these safe ranges. Use this table to double-check system alerts:

| Species | Optimal Temp | Critical Temp | Humidity Target |
| :--- | :--- | :--- | :--- |
| **Blanding's** | 29.5°C | < 26°C / > 33°C | 85% |
| **Wood Turtle** | 28.0°C | < 25°C / > 32°C | 90% |
| **Painted** | 29.0°C | < 26°C / > 33°C | 80% |

---

---

## 4. LIFECYCLE: EGG DEVELOPMENT STAGES (S0 TO S6)

![Turtle Lifecycle Infographic](../../assets/manual/turtle_lifecycle_infographic.png)

Turtle eggs move through seven development stages from "Just Laid" (S0) to "Hatched" (S6).

### 4.1 Understanding Stage Codes
*   **The Number (0-6)**: The lifecycle stage.
*   **The Letter (S, M, J)**: The progress level (Small, Medium, or Major).

### 4.2 Recording Hatching Vitality (Stage S6)
When an egg reaches S6, you must record a Vitality Score (0-5) to determine the next action:
-   **Score 5 (Strong)**: Baby is fully active. **Action**: Ready for transfer to release bin.
-   **Score 3 (Guarded)**: Slow movement or large yolk sac. **Action**: Move to Medical Observation.
-   **Score 0 (Failed)**: Baby died during hatching. **Action**: Notify Senior Biologist immediately.

---

---

## 5. ADMIN: FIXING ERRORS AND SETTINGS

### 5.1 Correction Mode
To keep records accurate, the system never fully deletes an entry. It marks it as **"Voided"** and saves a copy of the original for the background audit system.

1.  Toggle **Correction Mode** to ON at the top of the screen.
2.  Find the record and click **[VOID]**.
3.  Type a reason for the change (Mandatory).

### 5.2 Deleted Records Folder
If a bin was accidentally deleted while still containing active eggs, it is moved to the **Deleted Records Folder**. Contact an Administrator to restore these records.

---

---

## 📈 6. REPORTS: READING THE CLINICAL DATA (ANALYTICS)

The WINC Vault doesn't just store data; it translates it into biological stories. These reports help us understand which clutches are healthy and which ones need more help.

### 6.1 The Mortality Heatmap
This is the most important report for the Science team. It shows a grid of "Danger Zones."
*   **Green Squares**: Normal development for that time of year.
*   **Red Squares**: A "Critical Window" where many eggs are failing. If you see a cluster of Red, check the incubator temperature immediately!

> [Figure 6.1: Report Placeholder - Mortality Heatmap View]

### 6.2 WormD Exports (Sharing for Science)
WINC is part of a global network. We share our data with other turtle scientists using a format called **WormD**.
1.  Go to the **Download Data** screen.
2.  Select **WormD Export**.
3.  The system will create a "Clean" file that removes sensitive location data but keeps the biological health scores.

---

---

## 🆘 7. CRISIS: WHEN THE INTERNET FAILS (CONTINUITY)

Field tablets rely on Wi-Fi or Cellular data. If the connection drops in the middle of a check, follow this **Resilience Protocol**.

### 7.1 The Resilience Protocol
1.  ⚠️ **DO NOT REFRESH**: If you refresh the browser while the internet is "Red," you will lose the data currently in your tablet's local memory.
2.  **Switch to Paper**: Immediately pull out your **Physical Field Sheets** (v2026). Record all weights and health scores by hand.
3.  **The Double-Witness Rule**: Once the internet is restored, you must type the paper logs into the software. **A second person** (the "Witness") must sit next to you and check your typing against the paper to ensure there are no Subject ID typos.

![Crisis Offline Indicator](../../assets/manual/crisis_offline_indicator.png)

---

---

## 8. GLOSSARY

*   **Automatic Record Creation**: The background system that creates egg records immediately after a Mother Intake is saved.
*   **Chalking**: The white calcium patches on the shell indicating embryo development.
*   **Correction Mode**: A secure state that allows observers to void incorrect entries.
*   **Local Data Storage**: The fact that our data lives in our local database, not a third-party commercial cloud.
*   **Egg**: An individual developing turtle subject.
*   **Sign-In**: The process of identifying yourself to the database to start a shift.
*   **Voiding**: Marking an entry as incorrect without deleting it from the audit log.
*   **WormD**: The standard scientific format for exporting turtle health data.

---

---

**WINC Clinical Documentation © 2026**  
*Platinum Rated. Clinical Excellence. Failure-Proof.*
