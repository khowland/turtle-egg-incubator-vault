---
title: QA & Troubleshooting Methodology
tags:
  - qa
  - methodology
  - standards
---
# 🧪 QA & Troubleshooting Methodology

To ensure system stability and audit-readiness for the 2026 season, all QA activities must adhere to the following Knowledge Base (KB) integrated workflow.

## 1. The KB-First Rule
Before investigating any test failure or reporting a new bug:
1.  **Search the Hub**: Query `00_CENTRAL_HUB.md` and related resolution files for similar error strings (e.g., `AttributeError`, `StopIteration`).
2.  **Leverage Lessons**: Apply existing patterns (e.g., using `getattr` instead of `at.session_state.get()`) to resolve known infrastructure quirks.

## 2. Mandatory Reporting
Any time a bug is identified OR resolved:
1.  **Log the Resolution**: Create a new `.md` file in `tests/resolved_bugs/` following the `Bug-ID_resolution` format.
2.  **Update the Hub**: Link the new resolution in `00_CENTRAL_HUB.md`.
3.  **Contextual Data**: Include specific file paths, line numbers, and the forensic rationale for the fix.

## 3. Standard Remediation Patterns
- **Session State**: Always use `getattr(st.session_state, "key", default)` in AppTests to avoid version-specific `AttributeError`.
- **UI Selectors**: Use `in` for label matching (e.g., `"1" in cb.label`) to remain resilient against markdown formatting (e.g., `**1**`).
- **Mocking**: Use the recursive `build_table_aware_mock` from `tests/mock_utils.py` for deep clinical ledger queries.

---
*Standard established April 2026.*
