# 📖 Incubator Vault: Operator's Manual (v8.0.0)
**Clinical Sovereignty Edition**

## 1. Getting Started: The Login Splash
When you first open the Vault, you must select your name from the **Observer Identity** list.
*   **Persistent Login**: The system will remember your name for the rest of your shift.
*   **Global Shift Continuity**: If you or a colleague were active in the last 4 hours, the Vault will automatically resume the current "Shift Session." This ensures all your research notes for the morning are grouped together.
*   **Session Handshake**: Your entry into the Command Center is logged for research integrity.

## 2. New Intake: Bringing Eggs into the Vault
Use this screen when a new clutch arrives.
1.  **Select Species**: Choose from the list of 11 protected species.
2.  **Case #**: This matches your internal WINC or DNR case number.
3.  **Unique Bin Generation**: The system automatically appends a timestamp to each `bin_id` to ensure globallly unique clinical tracking.
4.  **Finalize**: Clicking "Commit" will establish the Bins and Eggs in the primary ledger using an atomic transaction.

## 3. Daily Observations: The Workbench
This is your primary tool for clinical monitoring.
1.  **The Hydration Gate**: You MUST record the bin's weight before you can see the eggs. This ensures our hydration protocols are never skipped.
2.  **The 4-Column Grid**: Large icons show the status of every egg.
3.  **Biological Icons**: 
    *   **Equator Band**: Chalking (0, 1, or 2). [0: None, 1: Partial, 2: Full]
    *   **Red Pulse**: Vascularity detected.
    *   **Star-Crack**: Stage S5 (Pipping).
4.  **Property Matrix**: Select multiple eggs to update their Stage and Health markers in bulk.

## 4. 🔄 Lifecycle: Retirement & Resurrection
Data is never truly lost in the Vault; it simply moves between **Active** and **Archive**.

### 4.1 The Resilience Flow
Archiving a bin "Soft Deletes" it. Dashboard KPI metrics explicitly filter out eggs from archived bins.

### 4.2 ✨ Surgical Resurrection
If clinical data surgery is required (e.g., accidental retirement or correction of a past stage):
1.  Enable the **Surgical Resurrection** toggle in the Observations workbench (**Admin, Staff, or Biologist** only).
2.  This mode **voids** individual observation rows (soft delete with audit reason); the egg's displayed stage rolls back to the latest non-void observation. Voided rows remain visible under the audit expander.
3.  Alternatively, use the **Resurrection Vault** in Settings (same roles) to restore entire retired Bins or Cases.

## 5. What if an Egg Hatches?
When an egg reaches **Stage S6 (Hatched)**:
1.  Set the stage to S6 via the Property Matrix. The egg status becomes **Transferred** and a **Hatchling Ledger** row is created or updated for that egg (incubation duration from egg intake date to hatch date when available).
2.  Use **Reports → WormD / Intake Export** (trusted roles) to download **flattened CSV** and **JSON** bundles for agency handoff; confirm import against your current WormD or DNR workflow.
3.  Physical subject is moved to juvenile enclosures per WINC SOP.

## 6. Accountability & Logs
At the bottom of the Observation screen, use the **Live Session Audit** to review your actions. 

**Note on Resumed Shifts**: If you see a banner stating **"📍 Resuming active shift started by..."**, it means your work is being added to the existing shift folder for clinical continuity. You still get full personal credit for your actions via your Observer ID.
