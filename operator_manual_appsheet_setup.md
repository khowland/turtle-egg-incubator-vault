# Operator Manual: AppSheet Interface Setup (v2.0 Revision)

Follow these steps to initialize the **AppSheet Mobile UI** from scratch and connect it to your **Supabase "Vault"**.

---

## 🏗️ 1. Signup & Account-Level API Key
*You can do this safely before creating any apps.*

1.  **Go to AppSheet**: [https://www.appsheet.com](https://www.appsheet.com).
2.  **Login**: Select **"Login with Google."** 
    *   *Note*: Use a dedicated Google account if possible for long-term non-profit handover.
3.  **Enable API**: Click your user icon (top-right) -> **"My Account"** -> **"Settings."**
4.  **Integrations Tab**: Click the **"Integrations"** tab at the top.
5.  **Generate Access Key**: Scroll to **AppSheet API**. Toggle it **ON**, then click **"Show Access Key."**
    *   *Save as*: **`APPSHEET_ACCESS_KEY`**.
    *   *Paste into `.env`*: (Line 62).

---

## 🏗️ 2. Create the "Incubator Vault" App (From Scratch)
*Since you have no app yet, we will use Gemini to "build the shell" for us.*

1.  **AppSheet Home**: Go to the AppSheet dashboard.
2.  **Create App**: Click **"Create" (+) -> "App" -> "Start with AI."**
3.  **The Prompt**: Paste this exact sentence into the Gemini box:
    > "Create a mobile app for a turtle egg incubator called 'Incubator Vault'. It needs tables for Mothers, Bins, Eggs, and Observations with photos."
4.  **Wait for Build**: Gemini will create the initial data structure and some basic mobile views. Click **"Customize my app"** when it's done.

---

## 🆔 3. Identify your App ID
*Now that your app exists, you can get its unique ID.*

1.  **Open Editor**: Open the "Incubator Vault" app you just created.
2.  **Settings**: Left sidebar -> **Settings (⚙️)** -> **Information**.
3.  **App Properties**: Look for the **App ID**. It looks like `bb9911-3344-555...`.
    *   *Save as*: **`APPSHEET_APP_ID`**.
    *   *Paste into `.env`*: (Line 61).

---

## 🔌 4. Connect AppSheet to Supabase (The Cloud Pivot)
*Currently, your app is likely linked to a Google Sheet. We want it linked to your Supabase Vault.*

1.  **Add Data**: In the AppSheet editor, click **"Data" (📊) -> "Add New Data."**
2.  **Select Source**: Click **"Cloud Database."**
3.  **Connection Settings**:
    *   **Type**: Select **PostgreSQL**.
    *   **Server**: Your Supabase URL (`kxfkfeuhkdopgmkpdimo.supabase.co`).
    *   **Database**: `postgres`.
    *   **User**: `postgres`.
    *   **Password**: Your **`SUPABASE_DB_PASSWORD`** from the `.env`.
4.  **Authorize**: Click **"Test"** and then **"Authorize."** 
    *   *Note*: Agent Zero will now be able to sync data directly to your mobile phone!

---

## 🏁 5. Handover Mission to Agent Zero (A0)
Once the connection is live, tell A0:

> "Agent Zero, the **AppSheet UI shell** is connected to the **Incubator Vault**. All keys for both systems are now in the `.env`. 
> 
> **Build Instructions:** 
> 1. Harmonize the **AppSheet UX** with the **Supabase schema** you just built. 
> 2. Implement the **Mobile Field Logic** for vascularity and chalking from the `expert.md` skill. 
> 3. Verify the sync engine and report back."
