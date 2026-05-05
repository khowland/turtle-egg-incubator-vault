# 🧪 Test Matrix: Settings Workflow
**Component:** `vault_views/5_Settings.py`
**Phase:** Phase 1 (Documentation & Matrix Generation)
**Status:** READY FOR VALIDATION

## 🎯 Overview
This matrix maps the UI elements and logic of the Settings page to specific Happy Path and Adversarial test cases, enforcing the **DB Pincer** validation mandate (UI Action → SQL Assertion).

---

## 🚦 Registry Protection (The Administrative Lock)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-LCK-01** | `st.toggle` ("Engage Mid-Season Lock") | Toggle ON: UI displays "LOCKED" error; all `st.data_editor` components become read-only (`num_rows="fixed"`). | Attempt to force a `supabase.upsert` via script while lock is ON. | N/A (UI State) |
| **SET-LCK-02** | `st.toggle` ("Engage Mid-Season Lock") | Toggle OFF: UI displays "EDITING ENABLED" success; `st.data_editor` allows dynamic row addition. | Rapidly toggle state; verify session persistence. | N/A (UI State) |

---

## 👥 User Registry (Tab 0)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-USR-01** | `st.data_editor` (Observer Registry) | Edit an existing `display_name` and click **SAVE**. | Enter an empty name (UI should block via `required=True`); enter SQL injection payload. | `SELECT display_name FROM observer WHERE observer_id = '{id}';` |
| **SET-USR-02** | `st.data_editor` (Login Allowed) | Uncheck `is_active` for a user and click **SAVE**. | Attempt to login with the deactivated user (should fail at Auth gate). | `SELECT is_active FROM observer WHERE observer_id = '{id}';` -- verify `false` |
| **SET-USR-03** | Dynamic Row (Add User) | Add a new row to the data editor, enter name, and click **SAVE**. | Add row with duplicate name; add row and click away without saving. | `SELECT COUNT(*) FROM observer WHERE display_name = '{new_name}';` |

---

## 🐢 Species Management (Tab 1)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-SPC-01** | `st.data_editor` (Species Config) | Modify a Scientific Name or Vulnerability Status and click **SAVE**. | Attempt to modify `species_id` (should be disabled/hidden); enter 3-char code (UI `max_chars=2`). | `SELECT scientific_name FROM species WHERE species_code = '{code}';` |
| **SET-SPC-02** | Dynamic Row (Add Species) | Add a new species (e.g., Code: `XX`, Name: `Test Turtle`) and click **SAVE**. | Add duplicate code; enter numeric code. | `SELECT * FROM species WHERE species_code = 'XX';` |

---

## 📦 Resurrection Vault (Tab 3)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-RES-01** | Bin Restore (`➕` Button) | Click restore on a retired bin. UI should show success and bin should disappear from Vault. | Restore a bin that has "GHOST DATA" warnings (active eggs). | `SELECT is_deleted FROM bin WHERE bin_id = '{id}';` -- verify `false` |
| **SET-RES-02** | Intake Restore (`➕` Button) | Click restore on a retired Case Intake. | Restore an intake where the associated bins are still deleted. | `SELECT is_deleted FROM intake WHERE intake_id = '{id}';` -- verify `false` |

---

## 📜 Activity Log (Tab 4)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-LOG-01** | Date Inputs & Table | Select a date range containing known audit events; verify events appear in table. | Select "From" date after "To" date; select date with 10k+ logs (performance check). | `SELECT COUNT(*) FROM system_log WHERE timestamp BETWEEN '{start}' AND '{end}';` |
| **SET-LOG-02** | `st.download_button` | Click "Download Activity Log (CSV)" and verify file content matches UI table. | N/A | N/A |

---

## ☢️ Backup & Restore (Tab 5 - Red Team)

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-BKP-01** | `GENERATE FULL BACKUP` | Click button; verify JSON payload generation and success message. | Click button on a massive DB (26GB) - check for timeout resilience. | N/A (UI State) |
| **SET-BKP-02** | `st.download_button` | Download the backup. UI should now unlock "Destructive Operations". | Attempt to access destructive buttons via URL/state injection before download. | N/A |
| **SET-WPE-01** | `st.text_input` (Obliterate) | Type `OBLITERATE CURRENT DATA`. Verify "WIPE" buttons become enabled. | Type incorrect string; type partial string. | N/A |
| **SET-WPE-02** | `WIPE & SET CLEAN START` | Click button. Verify DB is wiped and initialized to Day 1 state. | Click button then immediately refresh/close tab. | `SELECT COUNT(*) FROM intake WHERE is_deleted=false;` -- verify `0` |
| **SET-WPE-03** | `WIPE & SEED MID-SEASON` | Click button. Verify DB is wiped and seeded with synthetic data. | N/A | `SELECT COUNT(*) FROM species;` -- verify `> 0` |
| **SET-DRR-01** | `st.file_uploader` (Restore) | Upload a valid backup JSON and click **RESTORE**. | Upload malformed JSON; upload JSON from different schema version. | `SELECT COUNT(*) FROM intake;` -- verify matches backup count. |

---

## 👓 Accessibility & Sidebar

| Test ID | UI Element | Happy Path Description | Adversarial Scenario | DB Validation (SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **SET-ACC-01** | `st.sidebar.slider` (Text Size) | Move slider to 32px; verify UI re-renders with large text. | N/A | N/A |
| **SET-ACC-02** | `st.sidebar.toggle` (High-Contrast) | Toggle ON; verify CSS classes for high-contrast are applied. | N/A | N/A |
