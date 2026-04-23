---
description: [Sync User Manual with Code Changes]
---
1. **Analyze Changes**: Review the recent modifications in `vault_views/` or `utils/`.
2. **Update Operator Manual**: Locate the relevant section in `docs/user/OPERATOR_MANUAL.md`.
3. **Cross-Reference API Docs**: Ensure that any changes to docstrings are reflected in the `docs/api/` stubs.
4. **Verify Build**:
    // turbo
    Run `python -m mkdocs build` and check for any broken links or navigation errors.
5. **Commit**: Commit the documentation changes alongside the code changes.
