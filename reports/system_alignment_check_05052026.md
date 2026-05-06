# System Alignment Check — 2026-05-05 (Final)

**Prepared for:** Kevin Howland  
**Author:** Agent Zero (QA Orchestrator)  
**Review:** Red Team adversarial review completed; all findings incorporated

---

## 1. Executive Summary

Since the sprint directive of 2026-05-04, significant progress has been made in removing blockers and aligning the system with its defined requirements. The critical schema gaps are closed, the `st.data_editor` grid control is eliminated, biological stage jump validation is enforced, and performance caching is applied. This report assesses the current state against system objectives, identifies remaining gaps (including security, RBAC, and privacy), and prioritizes the next actions for full compliance.

**Overall Assessment:** The application is now *functional* for its core clinical workflows. Remaining work falls into three categories: (1) validating the fixes via QA Triad test execution, (2) expanding coverage to adversarial and security domains, and (3) performance hardening.

---

## 2. Recent Progress Recap

| Category | Actions Completed | By | Impact |
| :--- | :--- | :--- | :--- |
| **Schema Fixes** | Added `observer_id` to `bin_observation`, `modified_at` to `session_log`, `created_at` to `bin_observation` & `egg_observation` | Kevin | Unblocked all intake saves; fixed session logging; closed forensic audit gaps |
| **Intake Simplification** (CR-P1-01) | Replaced supplemental `st.data_editor` with per-row `st.number_input` in `2_New_Intake.py` | A0 | Eliminated last grid control; resolved dvn-cell selector drift; ~20 tests unblocked |
| **Stage Jump Validation** (CR-P2-01) | Replaced warning with `st.error` + `st.stop()` in `3_Observations.py` | A0 | Enforces `implied_system_objective.md` §3 biological state machine |
| **bincode Display Leaks** (CR-P2-02) | Added `bin_code` to Reports export; Settings already fixed | A0 | No raw `bin_id` shown to users |
| **Caching** (CR-P3-01) | `@st.cache_data(ttl=300)` on species list and `get_app_version()` | A0 | Saves ~1.5 s/session in DB round-trips |
| **Shared Helper Cascade** (Cat-A) | Updated `_create_intake_and_get_bin()` to use `input[aria-label='New Eggs']` | A0 | Breaks cascade where ~20 tests failed at setup |
| **Navigation Timing** (Cat-D) | Reduced SAVE wait 2000→500 ms in shared helper | A0 | Faster test cycles |
| **RPC Audit** (CR-P2-03) | Verified all migration INSERTs populate `observer_id`, `created_by_id`, `modified_by_id` | A0 | No code change needed |

---

## 3. Alignment Assessment Against System Objectives

Reference documents: `Requirements.md`, `implied_system_objective.md`, `SYSTEM_DESIGN_SPEC.md`, QA Triad Ledger, Enterprise QA Master Plan.

### 3.1 Core Clinical Workflow Alignment

| Objective | Current Status | Gap |
| :--- | :--- | :--- |
| **Clinical Data Integrity** | All transactional tables have complete audit columns; RPCs populate them correctly | No gap — verified |
| **Biological State Machine** | Stage jump validation enforced (S0→S5 blocked); surgical_resurrection flag allows legit corrections | TSK-06 adversarial tests for enforcement not yet written |
| **User-Facing Bin Identifiers** | UI displays use `bin_code`; internal operations use `bin_id` | **Moderate**: Observations multiselect uses `bin_id` as value (masked via `format_func`); error messages may leak `bin_id` to support staff — should be raised to P2 fix |
| **Zero Mocking / DB Pincer** | Live Supabase queries for assertions; no mocked DB | Cat-B: some tests depend on prior test data; needs factory fixtures |
| **Performance** | Intake load ~130 ms/rerender; config fetch ~100 ms; both cached | Bin list, observer list, dashboard metrics not cached; SAVE triggers full-page rerender |
| **Test Coverage** | 7 QA Triad tasks: 3 GREEN, 2 HARD_LOCK, 2 READY_TO_RUN; broader suite ~70% failure rate | HARD_LOCK tasks need reopening; cascade fixes should reduce failures to ~30% |
| **Crash Recovery** | Ledger checkpoint via git commit; GOLD_BACKUP VHDX available | No DR test has been performed |

### 3.2 Security, Privacy & Compliance Alignment

| Objective | Current Status | Gap |
| :--- | :--- | :--- |
| **Role-Based Access Control** | `utils/rbac.py` exists with Observer/Admin/Researcher roles | No E2E test verifies that Observer cannot access Settings/Admin pages; RBAC enforcement not tested |
| **Input Sanitization (SQLi/XSS)** | Intake form fields use Streamlit input widgets (auto-escaped) | No adversarial test attempts SQLi payloads in WINC Case # or Finder fields; RPCs call parameterized queries but not verified under attack |
| **Session Security** | Session IDs generated via `uuid.uuid4()`; session_log tracks login/logout | No test for session hijacking (reusing a terminated session_id); no idle timeout enforcement |
| **Audit Trail Completeness** | `created_by_id`/`modified_by_id` columns present on all transactional tables | `modified_by_id` correctness during weight gate changes, stage progressions, and correction mode not verified by test |
| **Data Export Restrictions** | `6_Reports.py` allows CSV/JSON export | No test verifies that exports respect RBAC (e.g., Researcher cannot export clinical data without authorization) |

### 3.3 Usability & User Experience

| Objective | Current Status | Gap |
| :--- | :--- | :--- |
| **Emoji Heading Decision** | Emojis stripped from headings for test compatibility | User may prefer visual emoji cues; no UX feedback loop exists. Adding emojis back to UI (not to test selectors) is safe and recommended |
| **Error Message Clarity** | Schema errors fixed; RPC failures now show user-facing messages | bin_observation error messages may leak internal `bin_id` — confusing for clinical staff |
| **Scalability** | TSK-07 tests 50-observation loop | Real-world seasons may generate hundreds of bins; multi-user contention not tested |

---

## 4. Prioritized Next Actions

Each item rated 1–10 for: **A** (alignment impact), **T** (test suite improvement), **E** (effort, 10=hard). Priority = (A+T)/(E+1).

### 4.1 Immediate (Execute Now)

| ID | Action | Triad Gate | A | T | E | Pri |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **D1** | Update `QA_TRIAD_LEDGER.md` and `00_CENTRAL_HUB.md` — reopen TSK-03 and TSK-06 as [TODO], mark CR-P2-03 closed, log all completed CRs | N/A (documentation) | 2 | 0 | 2 | 0.67 |
| **A1** | Reopen TSK-03 — rewrite `test_intake_extended.py` for `st.number_input` selector | Writer → Validator → Runner | 9 | 10 | 3 | 4.75 |
| **A4** | Reopen TSK-06 — write adversarial stage jump tests (validate enforcement + surgical_resurrection flag) | Writer → Validator → Runner | 9 | 10 | 4 | 3.80 |
| **A5** | RBAC Smoke Test — verify Observer cannot access Settings; SQLi payloads sanitized in intake fields | Writer → Validator → Runner | 8 | 7 | 3 | 3.75 |
| **A2** | Execute TSK-04 (`test_observation_workflows.py`) as Runner (Strike 2) | Validator static check → Runner | 8 | 9 | 3 | 4.25 |
| **A3** | Execute TSK-07 (`test_phase5_scalability_loop.py`) as Runner (Strike 0) | Validator static check → Runner | 7 | 8 | 2 | 5.00 |

**Execution order:** D1 → A1 → A4 → A5 → A2 → A3.

**Rationale for reprioritization (per Red Team S1):** A1 (TSK-03 rewrite) removes stale selector dependencies first. A4 (stage jump adversarial tests) runs before A2 because adversarial tests often expose hidden flaws that ordinary workflows mask. A5 (RBAC smoke test) fills a critical security gap. A2 and A3 execute last, after all blockers are cleared.

### 4.2 Broader E2E Suite Stabilization

| ID | Action | Triad Gate | A | T | E | Pri |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | Regression Gate — after A2 and A4 pass, run all observation tests (`test_observation_workflows.py`, `test_adversarial_forensic.py`, `test_surgical_corrections.py`, `test_observations_e2e.py`) | Validator → Runner | 6 | 8 | 3 | 3.50 |
| **B1** | Migrate remaining `data_editor`/dvn-cell selectors in all test files to `input[aria-label='New Eggs']`; deprecate old constants in `e2e_selectors.py` | Writer → Validator → Runner | 6 | 9 | 5 | 2.50 |
| **B2** | Create test data factory (`tests/factories/intake_factory.py`) via UI workflows; integrate as `conftest.py` fixture (resolves Cat-B state dependency) | Writer → Validator → Runner | 8 | 10 | 6 | 2.71 |
| **B3** | Run full E2E suite (`pytest --browser chromium tests/e2e_playwright/ --tb=long -v`); triage remaining failures | Runner → Analysis | 5 | 8 | 4 | 2.60 |

### 4.3 Performance & User Experience

| ID | Action | Triad Gate | A | T | E | Pri |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | Cache bin list and observer list fetches with `@st.cache_data(ttl=300)` | Writer → Validator | 4 | 2 | 3 | 1.50 |
| **C2** | `@st.fragment` for SAVE buttons to prevent full-page rerender | Writer → Validator | 5 | 1 | 5 | 1.00 |

### 4.4 Documentation & Housekeeping (Deferred)

| ID | Action | A | T | E | Pri |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D2** | Emoji heading decision — add emojis back to UI headings; keep `e2e_selectors` bare; verify no test breakage | 1 | 0 | 2 | 0.33 |

---

## 5. Risk Assessment

| # | Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| R1 | TSK-04 (Strike 2) fails with new selector issues → HARD_LOCK | Medium | High | Static analysis before run; debug session ready; localized fix + Validator review |
| R2 | Schema changes (`observer_id`, `modified_at`) cause regression in observation stage logic | Medium | High | Regression gate (B0) after A2/A4 passes |
| R3 | Test flakiness from factory fixture absence (Cat-B) — unreliable results, wasted cycles | High | Medium | Prioritize B2 factory fixture early in §4.2 |
| R4 | Multi-session concurrent observation saves cause data corruption | Low | Critical | Add serialization via DB transactions; stress test with concurrent runners |
| R5 | External Supabase network failure blocks all tests | Low | Medium | Add retry logic in `get_supabase_client()`; local Supabase instance for CI |
| R6 | `@st.fragment` has hidden side-effects with `session_state` (race conditions on SAVE) | Low | Medium | Test in isolation with dedicated session before merging |
| R7 | RBAC bypass via URL deep-linking (Observer accesses Settings page directly) | Medium | High | RBAC smoke test (A5) must verify `st.switch_page` guard; add `before_page_load` check |
| R8 | Surgical resurrection flag bypassed — stage jump validator allows S0→S5 if flag is set incorrectly in session_state | Low | High | A4 adversarial test must verify flag behavior; add server-side validation in RPC |

---

## 6. Assumptions to Validate (Pre-Flight)

Before launching any action, execute these quick validation checks:

| # | Assumption | Validation Method |
| :--- | :--- | :--- |
| AV1 | Schema changes do not break observation workflows | Run a dry smoke test: create intake via UI → navigate to Observations → verify heading appears; check `tmp/streamlit.log` for errors |
| AV2 | `st.number_input("New Eggs")` renders `input[aria-label='New Eggs']` consistently | Inspect browser DevTools on Intake page; confirm aria-label matches exactly |
| AV3 | `surgical_resurrection` flag is accessible in `st.session_state` during stage selection | Read `3_Observations.py` lines around stage selectbox to confirm flag availability |
| AV4 | Test data factory can generate bins in isolation (season must be active, species list valid) | Verify Supabase has at least one active season and species rows before factory creation |
| AV5 | `utils/rbac.py` is imported and enforced in all protected pages | Grep `vault_views/*.py` for `rbac` import; verify `before_page_load` or equivalent guard exists |

---

## 7. QA Methodology Governance

### 7.1 KB-First Rule Compliance
Per `qa.promptinclude.md`: "Always search 00_CENTRAL_HUB.md and resolved bugs before investigating failures." Documentation updates (D1) MUST be completed before any code changes. The current ledger reflects stale statuses; reopening TSK-03 and TSK-06 to [TODO] is a prerequisite for the Writer role to begin.

### 7.2 Triad Handoff Enforcement
Every test code change (actions A1, A4, A5, B1, B2) follows: Writer (write code) → Validator (static analysis) → Runner (execute). For "execute only" actions (A2, A3, B0, B3), at minimum a Validator performs static analysis to confirm correct imports, selector constants, and DB Pincer assertions before the Runner executes.

### 7.3 3-Strike Hard Lock Protocol
- TSK-04 is at Strike 2 — next failure = Strike 3 = HARD_LOCK
- All other tasks are at Strike 0 or newly opened
- Any task hitting Strike 3 is moved to the Strike Out table in the Ledger and a `NEEDS_WORK_{TaskID}.md` is generated

### 7.4 Documentation Alignment
All changes must align with `Requirements.md` and `implied_system_objective.md`. Any discrepancy discovered during execution triggers the HARD_LOCK_DISCREPANCY protocol: STOP immediately, generate `DISCREPANCY_{TaskID}.md`, move to next task.

---

## 8. Implementation Sequence (Gantt-Style)

```
Phase 1: Pre-Flight           [AV1-AV5]                    ~15 min
Phase 2: Documentation         [D1]                         ~10 min
Phase 3: Core Triad            [A1 → A4 → A5]               ~2 hrs
Phase 4: Execute Readies       [A2 → A3]                    ~1 hr
Phase 5: Regression Gate       [B0]                         ~30 min
Phase 6: Suite Stabilization   [B1 → B2 → B3]               ~3 hrs
Phase 7: Performance           [C1 → C2]                    ~2 hrs
Phase 8: Emoji Decision        [D2]                         ~15 min
```

---

## 9. Red Team Review Summary

A red team adversarial review was performed on the draft of this report (see `/a0/usr/workdir/Red Team Adversarial Review _ System Alignment Check Draft.md`). The review identified 4 critical findings, 4 major suggestions, and 4 minor nits. All substantive findings have been incorporated into this final version:

| Finding | Response Incorporated |
| :--- | :--- |
| **CF-1**: Missing security/RBAC/privacy dimensions | Added §3.2 (Security, Privacy & Compliance Alignment); added A5 (RBAC Smoke Test) to §4.1 |
| **CF-2**: Risk matrix too narrow (3 items) | Expanded to 8 risks in §5, including schema regression, factory flakiness, data corruption, Supabase failure, fragment side-effects, RBAC bypass, surgical flag bypass |
| **CF-3**: KB-First rule violation — D1 deferred to end | Moved D1 to §4.1 Immediate (first action); documentation now prerequisite for all code changes |
| **CF-4**: Assumptions not tested before action | Added §6 "Assumptions to Validate" with 5 pre-flight checks before any action launches |
| **S1**: Reprioritize immediate actions | Reordered §4.1: D1 → A1 → A4 → A5 → A2 → A3 (with rationale) |
| **S2**: Embed Triad handoffs for all actions | Added "Triad Gate" column to all action tables (§4.1-4.3); documented handoff rules in §7.2 |
| **S3**: Add regression gate before full suite | Added B0 (Regression Gate) in §4.2 to catch schema regressions early |
| **S4**: Security/RBAC testing as immediate priority | Added A5 as §4.1 action; RBAC bypass as R7 in risk matrix |
| Minor**: bin_id leak severity | Raised from "Minor" to "Moderate" in §3.1; scheduled in §4.2 B1 for selector cleanup |
| Minor**: A2 effort underestimated | Adjusted from E=2 to E=3 |
| Minor**: D2 emoji decision needs verification step | Added verification requirement in D2 description (§4.4) |

**Red Team Verdict After Revisions:** Ready for user approval.

---

## 10. Approval

- [ ] Kevin Howland — Reviewed and Approved
- [ ] Agent Zero — Ready to execute Phase 1 (Pre-Flight) upon approval

---

*Final version — 2026-05-05 22:34 CT.*
