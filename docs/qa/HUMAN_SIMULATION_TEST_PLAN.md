# 🧪 R&D Task List: Human-Simulated Testing Requirements
**Objective:** To verify system resilience under realistic clinical conditions through adversarial human-mimicry.

---

## 🏛️ Enterprise QA Simulation Standards
Every "Human-Simulated" test run by Agent Zero (A0) must adhere to these R&D requirements:

### 1. Adversarial Interaction (Ad-hoc)
- **HS-001: The "Double-Click" Stress**: Rapidly click 'SAVE' twice. System must handle the second click gracefully without duplicate records.
- **HS-002: Sloppy Precision**: Click action buttons at their outer 10px boundary (x,y) to ensure hitboxes are robust for mobile/touch users.
- **HS-003: Non-Linear Input**: Fill form fields out of sequence (e.g., enter mass, then Species, then Finder).

### 2. Biological Logic Stress (Expert Persona)
- **HS-004: The S0-S6 Gate**: Attempt to promote an egg from Stage S1 directly to S6 (Hatched). System must block this and demand the intermediate YSA (Yolk Sac Absorbed) milestones.
- **HS-005: Extreme Baseline**: Enter a mass of `0.0` or `1000.0` to verify that the "Doctoral-Level" data constraints trigger appropriate clinical warnings.

### 3. Session & UI Resilience
- **HS-006: The Distraction Wait**: Pause for 120 seconds in the middle of a complex form to ensure the Streamlit session doesn't time out or drop local data.
- **HS-007: Screen Handoff Stress**: Rapidly switch between 'Intake' and 'Observations' while a database write is pending to check for "Workflow Handoff" index errors.

---

## 🛠️ Implementation Guidance for A0
- **Vision Model**: Use **DeepSeek-VL2** for high-precision coordinate detection.
- **SQL Pincer**: After every successful `HS-001` or `HS-005` test, verify the database state via `SELECT` to ensure the logic holds.
- **Expert Ledger**: Log all results to `docs/expert/EXPERT_CR_LEDGER.md`.

---
*Verified for 2026 Enterprise QA Standards (v1.4.2)*
