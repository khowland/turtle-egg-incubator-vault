# Engineering & QA Methodology
1. Commit Often
2. Breadcrumbing
3. Obsidian Tracking
4. Objective Alignment
5. Rigorous Testing

## Update 2026-04-20: Intake Enhancements (Medium LOE)
- Patched `RPC_VAULT_FINALIZE_INTAKE.sql` to ingest `mother_weight_g` and `days_in_care`.
- Updated `2_New_Intake.py` UI to collect `Mother's Weight (g)` and `Days in Care`.
- Updated dynamic bin ID string format to `SN1-HOWLAND-1`.

- System documentation (`Requirements.md`, `OPERATOR_MANUAL.md`) successfully updated with new intake constraints.
- Verified `pytest` test suites pass with 100% success rate post-patching.
- Git commit and push initiated for feature rollout.
