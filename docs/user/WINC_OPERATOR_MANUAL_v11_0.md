![Operator Manual Cover Page](../../assets/manual/operators_manual_cover_page.png)

# 🐢 WINC Clinical Operator Manual (v11.0)
**Author:** Kevin Howland | **Target Audience:** Volunteer Clinicians | **Level:** Beginner

Welcome to the **WINC Turtle Incubator Vault**! 

This manual is your complete, step-by-step guide to using the system. It is designed to be simple, clear, and easy to follow. Whether it is your first day or you are a seasoned biologist, this document will show you exactly how to use every screen, menu, and report to save turtle lives.

---

## 📑 Table of Contents
1. [Chapter 1: Getting Started (Login)](#chapter-1-getting-started-login)
2. [Chapter 2: The Dashboard](#chapter-2-the-dashboard)
3. [Chapter 3: New Intake (Establishing a Case)](#chapter-3-new-intake-establishing-a-case)
4. [Chapter 4: Daily Observations & Biology](#chapter-4-daily-observations--biology)
5. [Chapter 5: Reports & Analytics](#chapter-5-reports--analytics)
6. [Chapter 6: Settings & Disaster Recovery](#chapter-6-settings--disaster-recovery)
7. [Chapter 7: Crisis Workflow (Offline Catch-up)](#chapter-7-crisis-workflow-offline-catch-up)

---

## Chapter 1: Getting Started (Login)
*Focus: Signing in securely and understanding shift handovers.*

![Figure 1: Login Screen](../../assets/manual/placeholder_screenshot.png)
*Figure 1: The Secure Login Interface*

### Step-by-Step: How to Sign In
1. Open the application.
2. You will see the **Observer Selector** dropdown.
3. Click the dropdown and select your name.
4. Click the button labeled **"START SESSION"**.

> ⚠️ **The 4-Hour Rule:** For security, the system will automatically log you out after 4 hours of inactivity. If this happens, simply select your name and sign in again!

### The Handover Process
When your shift ends, you must "Handover" the system to the next volunteer. Click **"LOGOUT"** in the sidebar. This ensures your name is not accidentally attached to their work!

---

## Chapter 2: The Dashboard
*Focus: Checking the pulse of the incubator room.*

![Figure 2: The Dashboard](../../assets/manual/report_sample_dashboard.png)
*Figure 2: The Active Dashboard Overview*

When you log in, you will land on the **Dashboard**. This is your home screen.

### What You Will See:
- **Active Bins:** A summary of all incubation bins currently holding eggs.
- **System Alerts:** If an egg needs attention, it will flash here.

**How to use it:** You do not need to enter data here. Just use the Dashboard to see how many eggs are currently in the system.

---

## Chapter 3: New Intake (Establishing a Case)
*Focus: Bringing a new turtle mother and her eggs into the system.*

![Figure 3: Intake Logic](../../assets/manual/intake_logic_flowchart.png)
*Figure 3: The logical flow of a new intake*

When a new turtle arrives, click **New Intake** on the left menu.

### Step-by-Step: Maternal Assessment
1. Find the section for the Mother Turtle.
2. **Carapace Measurement:** Use your calipers to measure the shell length (in mm). Type this into the **"Carapace Length (mm)"** field.
3. **Clinical Mass Gate (Mandatory):** You *must* weigh the eggs/bin. Type the weight into the **"Mass (g)"** field. *The system will not let you proceed if the weight is 0.0!* 
4. Fill out the substrate and temperature fields.
5. When everything is correct, click the **"SAVE"** button at the bottom of the screen.

---

## Chapter 4: Daily Observations & Biology
*Focus: Updating egg stages, vitality, and fixing mistakes.*

Click **Observations** on the left menu. This is where you will spend most of your time.

### 🛑 THE "NEVER ROTATE" MANDATE
> **CRITICAL RULE:** When observing an egg, **NEVER ROTATE IT**. Turtle eggs do not have internal anchors. If you turn the egg upside down, the embryo will drown in its own fluids. Always pick it up exactly as you found it.

### Step-by-Step: Recording an Observation
1. Select your Bin from the dropdown list.
2. You will see a list of eggs. Click on an egg to observe it.
3. Select the new **Stage** from the dropdown menu.
4. Click **"SAVE"**.

### Visual Stage Identification (Milestone-Substages)
Use this visual guide to choose the correct stage in the system:

*   ![Stage 1](../../assets/icons/egg_s1.png) **Stage 1 (S1):** Early Identification (Chalking). The egg is white and fresh.
*   ![Stage 2](../../assets/icons/egg_s2.png) **Stage 2 (S2):** Vascular Development. Veins are visible when shining a light through it.
*   ![Stage 3](../../assets/icons/egg_s3.png) **Stage 3 (S3):** Mid-Incubation. The turtle is growing darker inside.
*   ![Stage 4](../../assets/icons/egg_s4.png) **Stage 4 (S4):** Late-Stage. The egg feels heavy; movement might be seen.
*   ![Stage 5](../../assets/icons/egg_s5.png) **Stage 5 (S5):** Pipping Preparation. The turtle is about to break the shell.
*   **Stage 6 (S6):** Hatched! 

### Hatchling Vitality Scoring
When an egg reaches **S6**, you must give it a Vitality Score (0 to 5):
- **0-1:** Weak movement, large yolk sac remaining.
- **3:** Average strength, partial yolk sac.
- **5:** Excellent movement, fully absorbed yolk sac.

### Fixing a Mistake (LIFO Rollback Gates)
If you accidentally click the wrong stage and hit SAVE, don't panic! 
1. Look for the **"UNDO LAST ENTRY"** or **SHIFT END** button at the top of the sidebar.
2. Click it. The system uses a "Last-In, First-Out" (LIFO) rollback to safely erase your mistake like it never happened.

---

## Chapter 5: Reports & Analytics
*Focus: Exporting data for the Lead Scientists.*

![Figure 4: Analytics Dashboard](../../assets/manual/placeholder_screenshot.png)
*Figure 4: The Analytics and Reporting Dashboard*

Click **Reports** on the left menu.

### The Mortality Heatmap
This chart shows where eggs are failing.
- **Incubator Hotspots:** If many eggs fail in one spot, the incubator might be broken!
- **Genetic Failures:** If only one egg fails, it is likely just natural causes.

### The YA-3 Biosecurity Gate (WormD Export)
The Lead Scientist uses this page to click **"EXPORT WORMD"**. 
> **WARNING:** The system is software-locked. It will *not* let you export or retire a turtle until it reaches **S6-YA3 (Fully Absorbed)**. Releasing a turtle before its yolk sac is absorbed leads to fatal sepsis.

---

## Chapter 6: Settings & Disaster Recovery
*Focus: Advanced tools for Administrators.*

Click **Settings** on the left menu. **(Only Lead Administrators should use this page).**

![Figure 5: Disaster Recovery](../../assets/manual/placeholder_screenshot.png)
*Figure 5: The System Settings and Disaster Recovery tools*

### Bi-Directional JSON Disaster Recovery
If the system needs to be reset or restored from a backup, use the **Database State** tab.

1. You **MUST** click **"EXPORT FULL BACKUP"** first. This downloads a `.json` file to your computer. The system locks all other buttons to protect the data until you do this.
2. Once backed up, you must literally type `OBLITERATE CURRENT DATA` into the text box.
3. You can then safely click **"RESTORE"** and upload your backup file, or click **"WIPE & SET CLEAN START"** to erase everything for a new season.

---

## Chapter 7: Crisis Workflow (Offline Catch-up)
*Focus: What to do when the internet goes down.*

![Figure 6: Paper Logs](../../assets/manual/placeholder_screenshot.png)
*Figure 6: Paper Log transcription protocol*

If the facility loses power or internet, use paper clipboards to record data.

### The Double-Witness Sync
When the internet comes back online:
1. Sit down with the paper logs.
2. Have a partner sit next to you (The Witness).
3. Read the ID out loud. Type it in. The Witness must say "Confirmed" before you hit **"SAVE"**.
4. You can freely change the `Observation Date` field to yesterday's date so the computer knows exactly when the real event happened.

---
*End of Manual. Protocol Authority: WINC Incubator Vault © 2026*
