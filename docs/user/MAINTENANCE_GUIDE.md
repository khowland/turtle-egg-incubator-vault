# 🐢 WINC Incubator System v8.1.3 - Maintenance Guide
**2026 Production Season Edition**

## 🚀 Launch Instructions
1. Activate your Python environment.
2. Run:
   ```powershell
   streamlit run app.py
   ```
   *(Port 9000 is default to avoid local conflicts)*

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
