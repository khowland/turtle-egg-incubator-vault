# 🐢 WINC Incubator Vault: Master Migration & Handover Guide
**Project: Incubator Vault v8.0.0 — Institutional Clinical Edition**

This guide provides the official, step-by-step procedures for transitioning the Incubator Vault from development to a Production-Ready state for the Wildlife In Need Center (WINC).

---

## 🏗️ Phase 1: Database Setup (Supabase)

The Vault uses **Supabase** (PostgreSQL) as its biological ledger. Follow these steps to prepare the production database:

1.  **Create Supabase Project**:
    *   Log in to [database.supabase.com](https://database.supabase.com).
    *   Click **New Project** and name it `WINC-Incubator-Vault`.
    *   Set a strong database password (store this in a secure vault).
2.  **Initialize Schema & Lookup Tables**:
    *   Navigate to the **SQL Editor** in your new project.
    *   Copy and paste the entire content of `scripts/INITIAL_DATABASE_SEED.sql`.
    *   Run the script. This will create all tables (Mothers, Bins, Eggs, Observations) and populate the lookup tables for species (`BLA`, `SNAPP`, etc.) and developmental stages (`S0-S6`).
3.  **Capture API Credentials**:
    *   Go to **Project Settings** -> **API**.
    *   Copy the `Project URL` and the `anon public` key. You will need these for the next phase.

---

## 🚀 Phase 2: Application Hosting (Google Cloud Run)

The Streamlit UI is hosted on **Google Cloud Run**, which provides a free tier for non-profits and scales automatically.

1.  **Prepare the Container**:
    *   Ensure the `Dockerfile` in the project root is present.
    *   Open your terminal and authenticate: `gcloud auth login`.
    *   Build and push the image to Google Artifact Registry:
        ```bash
        gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/winc-vault
        ```
2.  **Deploy to Cloud Run**:
    *   Run the deployment command:
        ```bash
        gcloud run deploy winc-vault \
          --image gcr.io/[YOUR_PROJECT_ID]/winc-vault \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --set-env-vars SUPABASE_URL=[YOUR_URL],SUPABASE_KEY=[YOUR_KEY]
        ```
    *   *Note*: Ensure the `SUPABASE_URL` and `SUPABASE_KEY` match your production credentials.
3.  **Verify Vitality**:
    *   Once deployed, navigate to the URL provided by Google (e.g., `winc-vault-xyz.a.run.app`).
    *   Use the **Diagnostic Screen** (7_Diagnostic.py) within the app to verify DB connectivity.

---

## 🤝 Phase 3: Official Handover to WINC

At the end of the technical setup, the project ownership must be formally transferred to the WINC staff.

1.  **Supabase Ownership**:
    *   In Supabase Settings -> Team, invite the WINC official email (e.g., `tech@wildlifeinneed.org`) as an **Owner**.
2.  **Google Cloud Ownership**:
    *   In the GCP IAM console, add the WINC administrator account as a **Project Owner**.
3.  **GitHub / Code Transfer**:
    *   Deliver the finalized `.zip` bundle or transfer the GitHub repository to the WINC organizational account.
    *   Ensure all **Legacy Files** (found in `docs/archive/`) are deleted before going live to save space and reduce confusion.

---

## 🛠️ Phase 4: System Management & Maintenance

1.  **Staff Management**:
    *   Use the **Registry Screen** (5_Settings.py) to add the official names of staff members who will be performing observations.
2.  **The 7-Day Rule (Availability)**:
    *   If the database is not used for 7 days, Supabase will pause the project to save resources.
    *   **Solution**: The `scripts/heartbeat_ping.py` script is included to automatically "wake up" the database once a day. This should be scheduled as a **GitHub Action** or **Google Cloud Scheduler** job.

---
*For technical emergencies, consult the `docs/design/SYSTEM_DESIGN_SPEC.md` or the `docs/user/MAINTENANCE_GUIDE.md`.*
