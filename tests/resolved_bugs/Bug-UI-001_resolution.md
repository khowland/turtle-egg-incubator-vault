---
component: "vault_views/2_New_Intake.py"
issue_type: "UI Navigation / Syntax Error"
resolved: true
---
# Bug-UI-001: Intake Page Crashed on Navigation Due to Invalid f-string

**Issue**: After login and dashboard render, navigating to **Intake** crashed the application with a Python syntax error instead of rendering the intake workflow. The traceback pointed to `/a0/usr/workdir/vault_views/2_New_Intake.py` at the line building `r["bin_id_preview"]`.

**Root Cause**: The f-string embedded a nested `re.sub(r"...")` expression with conflicting quote characters inside the f-string, producing `SyntaxError: f-string: unmatched '('` during Streamlit page compilation.

**Resolution**:
1. Extracted the sanitized finder token into a separate local variable:
   - `finder_clean_preview = re.sub(r"[^A-Z0-9]", "", finder_name.upper()) if finder_name else ""`
2. Rebuilt the preview string using the precomputed value instead of a nested regex call inside the f-string.
3. Verified the file parses cleanly with:
   - `python3 -m py_compile /a0/usr/workdir/vault_views/2_New_Intake.py`

**Forensic Notes**:
- This defect was a true application bug, not a harness issue.
- It explains why the first adversarial E2E flow appeared to hang after startup/login: the app crashed when the test navigated into the Intake page.
- The crash was reproducible both from user-observed live behavior and the automated Playwright path.

**Files / Locations Referenced**:
- `/a0/usr/workdir/vault_views/2_New_Intake.py`
- `/a0/usr/workdir/tests/e2e_playwright/test_adversarial_forensic.py`
- `/a0/usr/workdir/tests/resolved_bugs/00_CENTRAL_HUB.md`
