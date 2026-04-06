# Operator Manual: GitHub & Supabase Sync

Follow these steps to initialize the **Source Code Vault** and link it to your **Supabase Backend** for automated deployments.

---

## 🛠️ 1. Create the GitHub Repository
1.  **Log in**: Go to [https://github.com](https://github.com).
2.  **New Repository**: Click the **"+"** icon (top-right) -> **"New repository."**
3.  **Repository Details**:
    *   **Name**: Type **`turtle-egg-incubator-vault`**.
    *   **Public/Private**: Select **Private** (to keep the biological data and system logic secure).
    *   **Initialize**: Select **"Add a README file."**
    *   **Add .gitignore**: Select **"Node"** (this is a good base for your project).
4.  **Create**: Click **"Create repository."**

---

## 🛡️ 2. The ".gitignore" Safety Net (CRITICAL)
Before you push any code, you **MUST** ensure your API keys (the `.env` file) never reach GitHub.
1.  **Open Local Folder**: Go to `C:\dev\projects\turtle-db\`.
2.  **Create/Edit `.gitignore`**: If you don't have one, create a text file named `.gitignore`.
3.  **Add the Entry**: Ensure this line is at the top of the file:
    ```
    .env
    ```
4.  **Save**: This prevents your **Supabase Secret Keys** from ever being uploaded to GitHub.

---

## 🏗️ 3. Push your Initial Work to GitHub
1.  **Initialize Local Git**: Open a terminal in `C:\dev\projects\turtle-db\` and run:
    ```bash
    git init
    git remote add origin https://github.com/your-username/turtle-egg-incubator-vault.git
    ```
2.  **Stage & Commit**:
    ```bash
    git add .
    git commit -m "chore: initial project initialization for Incubator Vault"
    git branch -M main
    git push -u origin main
    ```

---

## 🔌 4. Connect GitHub to Supabase
This allows Supabase to "see" your SQL migrations automatically.
1.  **Go to Supabase**: Open your **Incubator Vault** project.
2.  **Integrations**: Left sidebar -> **Settings (⚙️)** -> **GitHub**.
3.  **Link Repository**: Click **"Install Supabase on GitHub"** (it will ask you to authorize your GitHub account).
4.  **Select Repository**: Choose **`turtle-egg-incubator-vault`** from the dropdown.
5.  **Branch**: Select **`main`**.

---

## 🏁 5. Handover Mission to Agent Zero (A0)
Once the connection is live, tell A0:

> "Agent Zero, the **GitHub Repository** is linked to the **Incubator Vault in Supabase**. 
> 
> **Instructions:** 
> 1. Read `/workspace/Requirements.md`. 
> 2. Generate the **Supabase SQL Migration** file in `/supabase/migrations/`. 
> 3. Commit the changes and **push to GitHub**. 
> 4. Verify that the migrations are 'Deployed' in the Supabase Dashboard and report back."
