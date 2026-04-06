# Operator Manual: AppSheet Interface Setup

Follow these steps to initialize the **AppSheet Mobile UI** and connect it to your **Supabase "Vault"**.

---

## 🏗️ 1. Signup & Login
1.  **Go to AppSheet**: [https://www.appsheet.com](https://www.appsheet.com).
2.  **Login**: Select **"Login with Google."** 
    *   *Note*: Use the same Google account that will manage the Wildlife In Need Center's Drive/Sheets for the best integration.
3.  **Permissions**: Grant AppSheet permission to access your Google Drive (required for offline syncing and file storage).

---

## 🔑 2. Enable AppSheet API & Generate Key
This is required for **Agent Zero** to automate data syncs and advanced logic.
1.  **Account Settings**: Click your user icon (top-right) -> **"My Account"** -> **"Settings."**
2.  **Integrations Tab**: Click the **"Integrations"** tab at the top.
3.  **Enable API**: Scroll down to the **AppSheet API** section. Ensure the toggle is **ON**.
4.  **Show Access Key**: Click **"Show Access Key."** 
    *   *Save as*: **`APPSHEET_ACCESS_KEY`**.
5.  **Copy to `.env`**: Paste this value into your `C:\dev\projects\turtle-db\.env` exactly like this:
    `APPSHEET_ACCESS_KEY=[Your_Long_Key]`

---

## 🆔 3. Identify your App ID
If you have already created a "Blank" app or a shell:
1.  **Open Editor**: Open your app in the AppSheet editor.
2.  **Settings**: Left sidebar -> **Settings (⚙️)** -> **Information**.
3.  **App Properties**: Look for the **App ID**. It will be a string like `888-222-333e-444-555...`.
    *   *Save as*: **`APPSHEET_APP_ID`**.
4.  **Copy to `.env`**: Paste this value into your `.env` file.

---

## 🔌 4. Connect AppSheet to Supabase (Database Connector)
To make your "Incubator Vault" work, you must link the two systems.
1.  **Add Data**: In the AppSheet editor, click **"Data" (📊) -> "Add New Data."**
2.  **Select Source**: Click **"Cloud Database."**
3.  **Connection Settings**:
    *   **Type**: Select **PostgreSQL**.
    *   **Server**: Use your **`SUPABASE_URL`** (remove the `https://` and `.supabase.co` parts; use the Hostname if prompted, otherwise paste the full URL).
    *   **Database**: `postgres` (unless you renamed it).
    *   **User**: `postgres`.
    *   **Password**: Your **`SUPABASE_DB_PASSWORD`**.
    *   **SSL**: Ensure it is enabled.
4.  **Authorize**: Click **"Test"** and then **"Authorize."**

---

## 🏁 5. Handover Mission to Agent Zero (A0)
Once the connection is live, tell A0:

> "Agent Zero, the **AppSheet UI shell** is connected to the **Incubator Vault**. The `APPSHEET_ACCESS_KEY` and `APPSHEET_APP_ID` are now in the `.env`. 
> 
> **Instructions:** 
> 1. Design the **AppSheet UX Expressions** for 'Quick Edit' on Vascularity and Stage. 
> 2. Create the **Automation Bots** for 'New Intake' notifications. 
> 3. Verify the sync logic and report back."
