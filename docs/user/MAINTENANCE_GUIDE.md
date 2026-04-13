## 🚀 Launch Instructions

### 💻 Local Development
1. Activate your Python environment.
2. Ensure your `.env` file contains `SUPABASE_URL` and `SUPABASE_ANON_KEY`.
3. Run the application:
   ```bash
   streamlit run app.py --server.port=9000
   ```

### ☁️ Google Cloud (Cloud Run) Container Deployment
This application is containerized for stateless deployment on GCP.
1. **Build the Docker Image:**
   ```bash
   docker build -t gcr.io/YOUR_GCP_PROJECT_ID/winc-incubator:v8.1.3 .
   ```
2. **Push to Google Container Registry (or Artifact Registry):**
   ```bash
   docker push gcr.io/YOUR_GCP_PROJECT_ID/winc-incubator:v8.1.3
   ```
3. **Deploy to Cloud Run:**
   Deploy the image via the GCP Console or CLI. **Crucial:** You must inject the `SUPABASE_URL` and `SUPABASE_ANON_KEY` as environment variables or via Google Secret Manager during deployment. The container exposes port 8501 by default.

## 🛠️ Change Request Protocol
1. **Creation:** New requests use: `ChangeRequest_MMDD_HHMM.txt`.
2. **Categories:** `BUG`, `ENHANCEMENT`, `SECURITY`.

## 🧬 Technical Standards (v8.1.3)
- **UI Standard**: "5th-Grader" Intuitiveness (Unified Verb-Based Labels).
- **Core Identifiers**: Simplified Bin IDs (No timestamp suffix).
- **Primary Migration**: `supabase_db/v8_1_2_FULL_CONSOLIDATED_SCHEMA.sql`
- **Logic Engine**: Atomic RPC Intake via `vault_finalize_intake`.
- **Temporal Tracking**: `intake_timestamp` (TIMESTAMPTZ) for individual egg history.

## 🧬 Biological Coordinates
- **Registry**: 11 native species (BL, WT, OB, PA, SN, MT, FM, OM, SS, SM, MK).

## 🔒 Security & Admin
- **Correction Mode**: Replaces high-complexity "Surgical Resurrection" terminology for better volunteer understanding.
- **RBAC**: Role-based access managed via `utils/rbac.py`.

---
*Verified for Release v8.1.3.*
