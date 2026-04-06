# Agent Zero: Project Handover & Implementation Roadmap

## 1. Can Agent Zero (A0) "Perform the Work"?

**Yes, with specific caveats:**

*   **Supabase (100% Codeable)**: A0 can generate SQL for your schema, functions, and triggers. It can also write the integration code (Node.js/Python) for the "Auto-Unpause" heartbeat logic.
*   **AppSheet (Logic + Schema only)**: AppsSheet is a GUI-based "no-code" platform. A0 cannot "drag-and-drop" the UI for you unless it is given browser automation tools. However, **A0 can "code" the app by**:
    -   Generating the **Database Schema** (in Supabase or Google Sheets) that AppSheet reads.
    -   Writing the **AppSheet Expressions** (formulas for virtual columns, validation, etc.).
    -   Defining the **JSON configuration** for any AppSheet API calls.
    -   Writing a **Deployment Guide** for a human to follow in the AppSheet editor.

---

## 2. Required Access & Permissions
To perform these tasks effectively, ensure A0 has the following in your `.env` or passed via environment variables:

### For Supabase Integration:
- `SUPABASE_URL`: Your project URL.
- `SUPABASE_SERVICE_ROLE_KEY`: **CRITICAL** for A0 to modify the DB schema/functions.
- `SUPABASE_DB_PASSWORD`: If you want A0 to run direct `psql` migrations.
- `SUPABASE_MANAGEMENT_API_TOKEN`: Required for the programmatic "Unpause" (Wake) logic.

### For AppSheet Handover:
- `APPSHEET_APP_ID`: Once you create the empty shell in AppSheet.
- `APPSHEET_ACCESS_KEY`: To allow A0 to trigger data updates or syncs via API.
- **Google Service Account JSON**: If you want A0 to manage the Google Sheets (Version 1 fallback).

---

## 3. The "Missing Pieces" for a Successful POC

Before A0 can build a high-fidelity system, the "Biological Logic" needs more detail:

1.  **Stage Constants**: Define the expected number of days an egg stays in each stage (Intake -> ... -> Hatched) per species. This allows A0 to build "Alerts" for eggs that aren't developing as expected.
2.  **Sample "Clue Chain" Data**: Provide 3 real examples of Mother-Bin-Egg lineage to test the string concatenation logic.
3.  **Permissions Matrix**: Who can "Delete" vs "Soft Delete" records? (Volunteer vs. Staff).
4.  **Species Reference Table**: A curated list of Wisconsin turtle species (Blanding’s, Painted, Snapping, etc.) to prevent data entry errors.

---

## 4. Handover to Wildlife In Need Center (WINC)

Once the POC is successful, moving it to production requires these steps:

### Step 1: Stability Phase
- **PWA Conversion**: If not using AppSheet, wrap the Next.js app in a PWA manifest for offline "Incubator Room" use.
- **Conflict Resolution**: Implement a "Last Write Wins" sync strategy for the offline dead-zones.

### Step 2: WINC Staff Onboarding
- **The "Wet Hand" UI Test**: Have a volunteer test the app with gloves on. A0 can generate "High-Contrast" and "Large-Button" UI variations based on this feedback.
- **One-Click Export**: Implement the "Export to GSheet" button for the WINC board of directors/biologists.

### Step 3: Deployment
- **Sovereign Hosting**: Deploy the Supabase project to a dedicated account (not personal).
- **Hard-Capping Costs**: Set up alerts in Supabase/OpenRouter to ensure the non-profit doesn't exceed its budget.

---

## 5. Immediate Next Steps: The "A0 Command"

To hand this off, run the Agent Zero container and give it this **Mission Directive**:

> "Agent Zero, read `/workspace/Requirements.md`. Your mission is to initialize the **Supabase Backend** for the TurtleEggDB. 
> 1. Create the `schema.sql` with the 'Clue Chain' natural key logic. 
> 2. Ensure all tables have 'Created/Updated/Deleted' audit columns linked to a `SessionLog`. 
> 3. Implement the Postgres triggers for the 'Clue Chain' auto-generation. 
> 4. Generate the AppSheet Expression logic for the 'Quick Edit' toggles mentioned in line 146. 
> 5. Report back when the DB is ready for data ingestion."
