# 🐢 Incubator Vault v7.2.0 - Maintenance Guide

## 🚀 Launch Instructions
1. Ensure your network is clear.
2. Activate your environment.
3. Run:
   ```powershell
   streamlit run app.py
   ```
   *(The app is pre-configured to launch on Port 9000 to avoid Windows conflicts)*

## 🛠️ Feedback & Bug Reporting (The "Agile Sweep" Method)
To request changes or report bugs, please append them to `CHANGELOG_V7.md` in the following format:
`[TIMESTAMP] [CATEGORY] [DESCRIPTION]`

Categories: `BUG`, `ENHANCEMENT`, `EXPERT_FEEDBACK`, `SECURITY`.

## 🧬 Biological Coordinates (v7.2.0)
- **Primary Migration**: `supabase_db/migrations/20260408_v7_2_0_DEEP_DIVE.sql`
- **Native Species Registry**: 11 Wisconsin Native species (BL, WT, OB, PA, SN, MT, FM, OM, SS, SM, MK).
- **Core Requirements**: Refer to `Requirements.md` for the official v7.2.0 Biologist Workflow specs.

## 🔒 Security & Admin
- **Settings Page**: CRUD is enabled but gated by the **Mid-Season Lock**.
- **Lock Trigger**: `st.session_state.active_eggs_count > 0`.
- **Identity**: Session-based. One observer ID per browser session.
