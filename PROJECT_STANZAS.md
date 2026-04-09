# 🧬 WINC Incubator Vault: Project Stanzas (v7.2.1)
*Last Sync: 2026-04-08 22:20*

## 🏁 PROJECT STATUS: "GOLD MASTER"
The system is feature-complete and successfully transitioned from a v6 POC to a v7.2.1 Clinical Standard tool for the Wildlife In Need Center.

## 🧠 SYSTEM DNA
- **Clinical Origin**: Replaced "Mother ID" with a 11-species registry and `finder_turtle_name` provenance.
- **Atomic ID Formula**: `{Species}{IntakeCount}-{Finder}-{BinNumber}`.
- **Hydration Bridge**: Replaced air humidity with precision bin-weight tracking (§1.8).
- **Security Hub**: Mid-Season Lock active when `egg.status = 'Active'`.
- **UI Architecture**: Single-page Intake wizard with dynamic 1:N bin matrix.

## 📂 CORE FILE COORDINATES
- **Logic**: `app.py` (Navigation), `vault_views/` (Workflow pages), `utils/` (Bootstrap/Logic).
- **Master SQL**: `supabase_db/migrations/20260408_v7_2_0_DEEP_DIVE.sql`.
- **Validation**: `scripts/regression_check.py`.

## 📜 BIOLOGICAL RULES (For Reference)
- **Species**: 11 WI Natives (including "Stinkpot" alias for Musk Turtles).
- **Stages**: S0 to S6 (Intake to Hatched).
- **Neonate Pivot**: Hatched eggs move to `Transferred` status; data pushes to `hatchling_ledger`.

---
*Context Locked. Ready for Peer Review.*
