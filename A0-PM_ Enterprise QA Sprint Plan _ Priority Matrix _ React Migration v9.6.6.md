# A0-PM Enterprise QA Sprint Plan & Priority Matrix
**Project**: Turtle-DB React Migration (v9.6.6)  
**Role**: QA Project Manager (A0-PM)  
**Date**: 2026-05-21  
**Mandate**: NO MOCKING · BLIND PINCER · VERSION SOVEREIGNTY · GIT-FLOW TDD

---

## 1. Priority Matrix (Impact × Urgency)

| ID  | Issue | Impact | Urgency | Effort | Priority | Fix Type |
|-----|-------|--------|---------|--------|----------|----------|
| **C1** | SERVICE_ROLE key exposed in `frontend/.env` — bypasses all RLS | **Critical** | **Immediate** | **S** | **P0** | Security — rotate key, replace with anon key |
| **H1** | Observations.tsx batch save not atomic — per-egg queries in `Promise.all`, no RPC wrapper | **High** | **High** | **L** (RPC + refactor) | **P1** | Data Integrity — implement `vault_save_observations` RPC |
| **H3** | Version hardcoded `v9.6.6` in `Sidebar.tsx:11` — not fetched from `system_config` | **High** | **High** | **S** (fetch + cache) | **P1** | Sovereignty — dynamic version singleton |
| **H4** | SHIFT END uses `window.location.reload()` — no session cleanup, no forensic trail | **High** | **High** | **M** (cleanup + audit) | **P1** | Forensic — implement session termination with audit log |
| **H2** | `supabase as any` type bypass in Dashboard, Observations, Intake | **High** | **Medium** | **M** (type refactor) | **P2** | Type Safety — add proper generics |
| **M5** | SessionContext hardcodes `DEFAULT_OBSERVER` with `observer_id:1` — no real auth | **Medium** | **Medium** | **M** (auth flow) | **P2** | Authentication — implement real observer resolution |
| **M9-M13** | Biological property scales (chalking, denting, vascularity) not functional in Observations | **Medium** | **Medium** | **L** (UI + RPC) | **P2** | Clinical Accuracy — implement scale controls and DB write |
| **M1-M4** | Help, SystemCheck, Reports, Settings are "Pending Port" placeholder pages | **Medium** | **Low-Medium** | **L** (feature work) | **P3** | Feature Completeness — implement pages per design |
| **M7** | Dashboard mortality heatmap is placeholder (comment says "Recharts implementation") | **Medium** | **Low** | **M** (chart lib) | **P3** | Visualization — implement Recharts heatmap |
| **M8** | Vault Activity section is static text placeholder | **Medium** | **Low** | **M** (API + UI) | **P3** | Live Data — wire real vault activity feed |
| **M6** | `index.html` title is generic "frontend" → should be "WINC Incubator System" | **Low** | **Low** | **S** (text edit) | **P4** | Branding — update title |

### Priority Legend
- **P0** — Ship-stopper. Fix immediately before any other work.  
- **P1** — Must-fix in current sprint. Blocks production-readiness.  
- **P2** — Should-fix. High technical or clinical debt.  
- **P3** — Feature gap. Scheduled for sprint 2+ or backlog.  
- **P4** — Cosmetic. Pick up when convenient.

---

## 2. Sprint Backlog (2-Week Sprint: 2026-05-21 → 2026-06-04)

### **Sprint Goal**: Achieve production-readiness by eliminating all P0/P1 issues and completing critical P2 items.

### Week 1 (May 21–27)

| Task ID | Description | Size | Dependencies | Assignee | TDD Gate |
|---------|-------------|------|--------------|----------|----------|
| **SP1-C1** | Replace SERVICE_ROLE key with anon key in `.env`; audit all supabase client init calls | **S** | None | A2-DB | Verify JWT role = `anon` via decode test |
| **SP1-H3** | Implement version fetch from `system_config` using singleton pattern; propagate to Sidebar | **S** | None | A1-UI | Test `VersionDisplay` renders DB version, not hardcoded |
| **SP1-H4** | Implement SHIFT END with session cleanup (clear state, log forensic event, navigate to login) | **M** | SP1-C1 (for RLS-valid logout) | A1-UI + A2-DB | E2E test: verify audit log entry after SHIFT END |
| **SP1-H1a** | Design `vault_save_observations` RPC signature; create migration | **M** (design) | None | A2-DB | SQL unit test for atomic insert |
| **SP1-M5a** | Design real observer authentication flow (JWT decode → observer resolution) | **M** (design) | SP1-C1 (anon key) | A1-UI + A2-DB | Design doc approved |
| **SP1-TEST** | Write/fix tests for version sovereignty (H3), SHIFT END audit (H4) | **S** | SP1-H3, SP1-H4 | QA (A0-PM) | Red → Green cycle |

### Week 2 (May 28 – June 3)

| Task ID | Description | Size | Dependencies | Assignee | TDD Gate |
|---------|-------------|------|--------------|----------|----------|
| **SP2-H1b** | Implement `vault_save_observations` RPC + refactor Observations.tsx to call it | **L** | SP1-H1a | A2-DB + A1-UI | Tests: atomicity, rollback, error handling |
| **SP2-H2** | Remove `as any` type assertions; add proper TypeScript generics for Supabase queries | **M** | SP2-H1b (touches same files) | A1-UI | Zero `as any` in supabase calls; tsc passes strict |
| **SP2-M5b** | Implement real observer authentication in SessionContext (replace DEFAULT_OBSERVER) | **M** | SP1-M5a, SP1-C1 | A1-UI | Test: observer_id resolved from JWT, not hardcoded |
| **SP2-M9-13** | Implement biological property scale controls (chalking 0-2, denting 0-3, vascularity 0-2, etc.) with RPC write | **L** | SP2-H1b (same RPC) | A1-UI + A2-DB | E2E: change molding slider → DB reflects value |
| **SP2-M6** | Fix `index.html` title to "WINC Incubator System" | **S** | None | A1-UI | Title tag assertion in smoke test |
| **SP2-REG** | Regression test suite: re-run blocked TSK-04, TSK-06, TSK-07 with vision-driven approach | **M** | SP2-H1b, SP2-M5b | QA (A0-PM) | All 61+ tests green |

### Backlog (Post-Sprint)
- M1-M4: Implement placeholder pages (Help, SystemCheck, Reports, Settings)
- M7: Implement Recharts mortality heatmap
- M8: Wire live Vault Activity feed
- Performance benchmarking (§5: TFMP < 1.0s, hydration < 1.5s)
- Mobile-first visual regression suite (§7)

---

## 3. Test Coverage Gaps (Requirements § vs. Test Evidence)

| Requirements Section | Description | Current Test Coverage | Gap | Recommended Test |
|----------------------|-------------|----------------------|-----|------------------|
| **§1.3** | Atomic Transactions — multi-table clinical writes must use single RPC | TSK-03 partially covers; 2 failures due to RPC bug | RPC isolation test missing | `test_rpc_vault_save_observations_atomicity.py` |
| **§1.4** | Database-Driven Versioning — fetch from `system_config` singleton | **None** | No test verifies dynamic version | `test_version_sovereignty.py` — assert Sidebar text matches `system_config` |
| **§1.5** | Action Button Labels — standardized SAVE, CANCEL, START | Implicit in UI workflow tests | No explicit label enumeration test | `test_button_label_standards.py` — assert exact labels |
| **§2** | Session resumption window (1-hour), bin weight check, unified identity | TSK-06 partially covers (blocked) | Blocked by bridging bug; needs vision-driven alternative | `test_session_resumption_workflow.py` (vision mode) |
| **§3** | S0-S6 lifecycle stages, biological property model | TSK-04 covers stage progression (blocked) | Biological property scales not tested | `test_biological_property_scales.py` — validate molding/chalking/vascularity ranges and DB persistence |
| **§4** | Soft delete (is_deleted) and forensic auditing | Adversarial tests partially cover | SHIFT END forensic trail untested | `test_forensic_shift_end.py` — assert `system_log` entry after session termination |
| **§5** | Performance: TFMP < 1.0s, hydration < 1.5s, UI fluidity < 2.0s | `test_performance.py` exists | No CI threshold enforcement | Integrate performance assertions into CI pipeline |
| **§7** | Mobile-first tight-fit (0.8rem margins) | None | No responsive/visual regression tests | `test_mobile_viewport_regression.py` (Playwright viewport + screenshot diff) |
| **§9** | High-Fidelity QA Standards | Meta-governance | Current blocked tests violate this | Unblock TSK-04/06/07; enforce red-green cycle |
| **M1-M4** | Placeholder pages | None | No smoke tests for placeholder pages | `test_placeholder_page_smoke.py` — assert each page renders non-error content |

### Summary
- **6 untested requirements sections** (out of 10 total sections tracked)
- **3 critical test files to create**: version sovereignty, biological property scales, forensic SHIFT END
- **13 tests blocked** by bridging bug → vision-driven unblock plan in Sprint Week 2

---

## 4. Blind Pincer Task Plan: A1-UI & A2-DB

### A1-UI (Frontend Agent)
**Role**: Verify all 18 frontend source files against Requirements.md. Execute visual and functional validation of UI components with zero mocking.

| Task | Description | Deliverable | TDD Gate |
|------|-------------|-------------|----------|
| **UI-1** | Audit all 18 `.tsx`/`.ts` files for `as any` usage; create hit-list | `frontend_type_safety_audit.md` | Zero `as any` in supabase calls |
| **UI-2** | Implement dynamic version fetch in Sidebar (singleton pattern) | Patched `Sidebar.tsx` + test | `test_version_sovereignty.py` green |
| **UI-3** | Implement SHIFT END session cleanup (clear state → log → navigate to login) | Patched `Dashboard.tsx` or session hook | `test_forensic_shift_end.py` green |
| **UI-4** | Implement biological property scale controls (molding 0-4, chalking 0-2, denting 0-3, vascularity 0-2) in Observations | Patched `Observations.tsx` | Slider values persist on save; DB verification |
| **UI-5** | Create Playwright visual regression tests for all pages (mobile viewport 375×812) | `test_visual_regression_mobile.py` | Screenshot diff < 0.1% threshold |
| **UI-6** | Enumerate all action button labels across pages; enforce SAVE/CANCEL/START standard | `test_button_label_standards.py` | 100% compliance |

### A2-DB (Database/Backend Agent)
**Role**: Verify database schema, RPC signatures, and forensic audit integrity. All validation via real Supabase queries — no mocking.

| Task | Description | Deliverable | TDD Gate |
|------|-------------|-------------|----------|
| **DB-1** | Rotate SERVICE_ROLE key; deploy anon key; verify JWT `role` claim = `anon` | `.env` updated + decode test | `test_jwt_role_is_anon.py` — assertion on decoded JWT |
| **DB-2** | Verify `system_config` table has current version row; create `get_system_version()` wrapper | Migration check + wrapper function | `SELECT value FROM system_config WHERE key='app_version'` returns expected |
| **DB-3** | Design and create `vault_save_observations` RPC (atomic multi-egg save with rollback) | Migration SQL + RPC function | SQL unit test: insert 5 eggs in one call → all or none |
| **DB-4** | Audit `vault_finalize_intake` RPC for observer resolution; verify no hardcoded `observer_id=1` | DB audit report | Observer resolved from session, not hardcoded |
| **DB-5** | Verify forensic audit trail: `system_log` receives entry on SHIFT END with correct `trace_id`, `observer_id`, `action` | Query against test data | `test_forensic_shift_end_db.py` — row exists with action='session_terminated' |
| **DB-6** | Validate soft-delete triggers on all clinical tables (`egg`, `intake`, `hatchling_ledger`); audit `is_deleted` flag usage | Schema audit report | `test_soft_delete_propagation.py` — cascade behavior verified |

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| C1 exploitation before fix | Medium | Catastrophic (data breach) | Rotate key immediately; schedule as first action |
| H1 data corruption under concurrent use | Medium | High (clinical data loss) | Ship atomic RPC in Week 1 design, Week 2 implementation |
| TSK-04/06/07 bridging bug persists | High | Medium (18 tests blocked) | Vision-driven testing as alternative path (Week 2) |
| Effort underestimation for M9-M13 biological properties | Medium | Medium (sprint spill) | Scope to 2 properties in sprint; defer remainder |
| TypeScript strict mode reveals hidden errors after H2 fix | High | Low (build failures) | Incremental `as any` removal with CI gate |

---

## 6. Git-Flow TDD Cycle

**Red → Fix → Green → Push** with semantic commits:

```
fix(security): replace SERVICE_ROLE with anon key [C1]
feat(observations): atomic batch save via vault_save_observations RPC [H1]
fix(sidebar): dynamic version from system_config [H3]
fix(auth): SHIFT END session cleanup with forensic audit [H4]
refactor(types): remove supabase as any assertions [H2]
feat(auth): real observer resolution from JWT [M5]
feat(observations): biological property scale controls [M9-M13]
chore(branding): update index.html title [M6]
test: version sovereignty, forensic SHIFT END, biological properties
```

---

*Report generated by A0-PM (Agent Zero QA Project Manager) under Enterprise QA Blind Pincer Protocol. All findings based on line-by-line audit of 18 frontend source files, Requirements.md §1-§9, and historical QA Triad records.*