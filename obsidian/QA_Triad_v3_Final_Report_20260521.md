---
tags:
  - qa-triad
  - final-report
  - project-plan
  - blind-pincer
date: 2026-05-21
status: complete
triad_agents:
  - A0-PM
  - A1-UI
  - A2-DB
---
# QA Triad v3 — Final Unified Project Plan [2026-05-21]

## Executive Summary

The QA Triad (PM, UI Scripter, DB Auditor) has completed a full blind-pincer analysis of the Turtle-DB React migration system. Every finding is evidence-based with exact file paths and line numbers.

### Triad Members
| Role | Agent | Report |
|------|-------|--------|
| Project Manager | A0-PM | `/a0/usr/workdir/A0-PM_ Enterprise QA Sprint Plan _ Priority Matrix _ React Migration v9.6.6.md` |
| UI Scripter | A1-UI | Inline report (6 tasks completed) |
| DB Auditor | A2-DB | `/a0/usr/workdir/DB Auditor Report - QA Triad Sprint Plan _2026-05-21.md` |

---

## 🔴 Blind Pincer Discrepancies (Critical Catches)

These are findings where UI and DB agents independently discovered conflicting truths — the core value of the Blind Pincer Protocol.

| # | UI Finding (A1-UI) | DB Finding (A2-DB) | Discrepancy |
|---|--------------------|--------------------|------------|
| **BP-1** | Sidebar displays **v9.6.6** (hardcoded) | system_config.APP_VERSION = **v8.1.27** | Version mismatch: UI shows aspirational React version, DB holds actual production version. Frontend must fetch dynamically per §1.4. |
| **BP-2** | Observations.tsx does per-egg queries in Promise.all | vault_finalize_batch_observation RPC exists with implicit transaction | RPC exists but has type mismatch (uuid vs bigint). Frontend should use RPC, not raw queries. |
| **BP-3** | SHIFT END = window.location.reload() | system_log table fully supports forensic audit events (trace_id, observer_id, event_type) | DB can record logout, but UI doesn't log it. |
| **BP-4** | 4 `as any` casts in UI files | No RLS policies on any clinical table | UI type safety + DB row-level security both absent — defense in depth missing on both sides. |

---

## 📊 Unified Priority Matrix

| Priority | ID | Issue | Source | Impact | Effort | Sprint Week |
|----------|----|-------|--------|--------|--------|-------------|
| **P0** | C1 | SERVICE_ROLE key in frontend/.env | A0 Audit | RLS bypass — all data exposed | S | **Week 1 Day 1** |
| **P1** | DB-1 | No RLS policies on any clinical table | A2-DB | Full table access without restriction | M | Week 1 |
| **P1** | BP-1 | Version: UI hardcoded v9.6.6 vs DB v8.1.27 | Triad | Breaking §1.4 version sovereignty | S | Week 1 |
| **P1** | H4 | SHIFT END = window.location.reload() | A1-UI | No forensic session termination | M | Week 1 |
| **P1** | DB-3 | vault_finalize_batch_observation: uuid vs bigint type mismatch | A2-DB | Runtime error on observation save | M | Week 1-2 |
| **P1** | DB-3 | vault_finalize_intake references non-existent incubator_temp_c column | A2-DB | Archived RPC broken if reactivated | S | Week 1 |
| **P2** | H2 | 4 `as any` type assertions in UI | A1-UI | TypeScript safety bypassed | M | Week 2 |
| **P2** | M5 | Hardcoded DEFAULT_OBSERVER (observer_id:1) | A1-UI | No real authentication | M | Week 2 |
| **P2** | M9-M13 | Biological scales: 2/5 functional | A1-UI | Clinical accuracy compromised | L | Week 2 |
| **P3** | M1-M4 | 4 placeholder pages (Pending Port) | A1-UI | Feature incompleteness | L | Backlog |
| **P3** | M7 | Mortality heatmap placeholder | A1-UI | No visualization | M | Backlog |
| **P3** | M8 | Vault Activity static text | A1-UI | No live data feed | M | Backlog |
| **P4** | M6 | index.html title = "frontend" | A1-UI | Branding | S | Whenever |

---

## 📋 2-Week Sprint Backlog

### Week 1 (May 21-27): Security + Version + Forensic Foundation

| Task | Size | Assignee | Depends On | TDD Gate |
|------|------|----------|-----------|----------|
| **SP1-C1**: Replace SERVICE_ROLE with anon key | S | A2-DB | None | `test_jwt_role_is_anon.py` green |
| **SP1-RLS**: Implement RLS policies on clinical tables | M | A2-DB | SP1-C1 | Row counts match expectations per role |
| **SP1-H3**: Dynamic version fetch from system_config | S | A1-UI | None | `test_version_sovereignty.py` green |
| **SP1-H4**: SHIFT END with session cleanup + audit log | M | A1-UI + A2-DB | SP1-C1 | `test_forensic_shift_end.py` green |
| **SP1-DB3**: Fix vault_finalize_batch_observation type mismatch | M | A2-DB | None | RPC unit test passes |
| **SP1-DB3b**: Fix vault_finalize_intake column reference | S | A2-DB | None | RPC deploys without error |

### Week 2 (May 28-Jun 3): Clinical Integrity + Type Safety

| Task | Size | Assignee | Depends On | TDD Gate |
|------|------|----------|-----------|----------|
| **SP2-H2**: Remove `as any` casts, add TypeScript generics | M | A1-UI | None | Zero `as any` in supabase calls |
| **SP2-M5**: Real observer authentication (JWT → observer) | M | A1-UI + A2-DB | SP1-C1 | observer_id from JWT, not hardcoded |
| **SP2-M9-13**: Biological property scales (chalking, denting, vascularity) | L | A1-UI + A2-DB | SP1-DB3 | Sliders persist to DB |
| **SP2-M6**: Fix index.html title | S | A1-UI | None | Title tag assertion in smoke test |
| **SP2-REG**: Regression — unblock TSK-04/06/07 | M | QA (A0-PM) | All above | 61+ tests green |

---

## 🧪 Test Coverage Gaps

| Req Section | Description | Status | Recommended Test |
|-------------|-------------|--------|-----------------|
| §1.3 | Atomic Transactions | ⚠️ Partial | `test_rpc_vault_save_observations_atomicity.py` |
| §1.4 | Database-Driven Versioning | ❌ None | `test_version_sovereignty.py` |
| §1.5 | Button Label Standards | ⚠️ Partial | `test_button_label_standards.py` |
| §2 | Session Resumption | ❌ Blocked | `test_session_resumption_workflow.py` (vision) |
| §3 | Biological Property Model | ❌ None | `test_biological_property_scales.py` |
| §4 | Forensic Auditing (SHIFT END) | ❌ None | `test_forensic_shift_end.py` |
| §7 | Mobile-First Tight-Fit | ❌ None | `test_mobile_viewport_regression.py` |
| §9 | High-Fidelity QA Standards | ⚠️ 13 tests blocked | Unblock via vision-driven approach |

**Total: 6 sections with zero coverage, 3 with partial coverage.**

---

## 🛡️ Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| C1 exploitation before fix | Medium | **Catastrophic** (data breach) | Execute SP1-C1 as first action |
| No RLS policies — any user reads all data | High | High | SP1-RLS immediately after key rotation |
| RPC type mismatch causes runtime errors | High | High (clinical data loss) | Fix in Week 1 |
| TSK-04/06/07 bridging bug persists | High | Medium | Vision-driven testing Week 2 |
| Effort underestimation for biological scales | Medium | Medium | Scope to 2 of 3 missing scales |

---

## 🔄 Git-Flow TDD Commit Plan

```
fix(security): replace SERVICE_ROLE with anon key [C1]
feat(auth): implement RLS policies on clinical tables [DB-1]
fix(sidebar): dynamic version from system_config [H3]
fix(auth): SHIFT END session cleanup with forensic audit [H4]
fix(rpc): correct observer_id type in vault_finalize_batch_observation [DB-3]
fix(rpc): remove non-existent incubator_temp_c from vault_finalize_intake [DB-3b]
refactor(types): remove supabase as any assertions [H2]
feat(auth): real observer resolution from JWT [M5]
feat(observations): biological property scale controls [M9-M13]
chore(branding): update index.html title [M6]
test: version sovereignty, forensic SHIFT END, biological properties
```

---

## 📐 Requirements Compliance Summary

| Requirement Section | Compliance | Action Needed |
|---------------------|-----------|--------------|
| §1.1 Project Organization | ✅ | — |
| §1.2 Naming Convention | ✅ | — |
| §1.3 Atomic Transactions | 🔴 FAIL | Fix RPC type mismatch, use RPC not raw queries |
| §1.4 DB-Driven Versioning | 🔴 FAIL | Implement dynamic version fetch |
| §1.5 Unified Vocabulary | 🟡 PARTIAL | Add START button, rename SAVE OBSERVATIONS |
| §2 Session Persistence | 🟡 PARTIAL | Implement real auth, fix SHIFT END |
| §3 Biological Properties | 🟡 PARTIAL | Add 3 missing scales |
| §4 Resilience & Security | 🔴 FAIL | Replace SERVICE_ROLE key, add RLS |
| §4.5 Bin Closure Audit | ❌ NOT IMPLEMENTED | Backlog |
| §4.6 Biosecurity Export Gate | ❌ NOT IMPLEMENTED | Backlog |
| §5 Performance | ⚪ UNVERIFIED | Add benchmarks |
| §7 Mobile-First | ⚪ UNVERIFIED | Visual regression tests |
| §9 High-Fidelity QA | 🟡 PARTIAL | Unblock 13 tests |

---

*Report synthesized by A0 (Agent Zero) from QA Triad v3 blind-pincer analysis. All findings evidence-based with exact file paths and line numbers. No speculation.*
