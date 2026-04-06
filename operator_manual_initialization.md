# Operator Manual: Project Initialization (Incubator Vault)

Follow these steps to initialize the **TurtleEggDB v2.0** infrastructure.

---

## 🏗️ 1. Create the Supabase Project
1.  **Log in**: Go to [https://supabase.com/dashboard](https://supabase.com/dashboard).
2.  **New Project**: Click the **"New project"** button (top-right).
3.  **Project Details**:
    *   **Organization**: Select your organization.
    *   **Name**: Type **`Incubator Vault`**.
    *   **Database Password**: Create a strong password (at least 15 characters). 
        *   *Save this immediately as* **`SUPABASE_DB_PASSWORD`**.
    *   **Region**: Select the region closest to you (e.g., East US).
    *   **Pricing Plan**: Select **Free** (you can upgrade to Pro mid-season).
4.  **Wait for Provisioning**: It will take 1–2 minutes for the database to spin up.

---

## 🔑 2. Procure Project-Level API Keys
Once the project is "Ready" (green dot):
1.  **Go to Settings**: Left Sidebar -> **Settings (⚙️)** -> **API**.
2.  **Copy Project URL**: Find the "Project URL" and copy the full `https://...` link.
    *   *Save as*: **`SUPABASE_URL`**.
3.  **Copy Service Role Key**: Under "Project API Keys," find the key named **`service_role` (Secret)**.
    *   *Note*: You must click **"Reveal"** to see the full key.
    *   *Save as*: **`SUPABASE_SERVICE_ROLE_KEY`**.
4.  **Confirm DB Name**: Under **Settings (⚙️) -> Database**, confirm the "DB Name" is `postgres`. In your code, you will refer to the system as **`turtle_egg_db`**.

---

## 🎟️ 3. Procure Management API Token (Account Level)
This is required for Agent Zero to "wake up" the Vault programmatically.
1.  **Account Tokens**: Go to [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens).
2.  **Generate Token**: Click **"Generate new token."**
3.  **Name**: Type `AgentZero_Vault_Manager`.
4.  **Save Copy**: Copy and save this token immediately. **It will only be shown once.**
    *   *Save as*: **`SUPABASE_MANAGEMENT_API_TOKEN`**.

---

## 🛡️ 4. Deploy Keys to the `.env` (Secure Handoff)
Open the file at `C:\dev\projects\turtle-db\.env` and paste these exact lines at the bottom (replace the placeholders):

```bash
# --- [Lo] INFRASTRUCTURE: Incubator Vault (Supabase) -----------------
SUPABASE_URL=https://[YourProjectID].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[YourServiceRoleKey]
SUPABASE_DB_PASSWORD=[YourDatabasePassword]
SUPABASE_MANAGEMENT_API_TOKEN=[YourManagementToken]

# --- [Ac] INTERFACE: AppSheet (Mobile Field UI) ----------------------
# (Optional: If you have an AppSheet ID ready)
APPSHEET_APP_ID=[YourAppID]
APPSHEET_ACCESS_KEY=[YourAppSheetKey]
```

---

## 🏁 5. Handover Mission to Agent Zero (A0)
Once the `.env` is saved, give A0 this command:

> "Agent Zero, the **Incubator Vault** is live. I have updated the `.env` in `/workspace` with the new project keys. 
> 
> **Instructions:** 
> 1. Read `/workspace/Requirements.md`. 
> 2. Build the full relational schema in Supabase. 
> 3. Implement the Postgres triggers for the 'Clue Chain' auto-key generation.
> 4. Verify connectivity and report back when the Vault is ready for its first turtle."
