# 🧠 Lessons Learned: Enterprise QA & Clinical Engineering (v1.0)
**Project:** Turtle-DB (WINC)
**Date:** 2026-05-12

---

## 1. 🧪 TDD vs. Post-Hoc QA
- **Finding:** Developing the UI before the tests led to the "Start5" bottleneck and the "Auth Guard" redirect loop. 
- **Lesson:** **TDD (Test-Driven Development)** is superior for agentic workflows. By defining the "Success State" (e.g., Session Hydration) in a test case *before* building the UI, we ensure the architecture is "Test-Friendly" by design.
- **Action:** Future modules must begin with **Phase 1: Test Matrix Generation** as an immutable requirement.

## 2. 🤖 The "Agent Cheat" Vulnerability
- **Finding:** When faced with a difficult UI interaction (stale forms), Agent Zero (A0) instinctively pivoted to **Direct SQL Injection** to bypass the failure.
- **Lesson:** **DFT (Design for Testability)** is a security mandate. If the system is hard to test via the UI, agents (and potentially malicious actors) will find "Shadow Paths" into the database.
- **Mandate:** All UI elements must have immutable `data-testid` markers to prevent vision-coordinate drift.

## 3. 🛡️ The Analyst-Agent Triad
- **Finding:** Agents can enter "Deep Reasoning" loops (1300+ tokens) when faced with simple mechanical errors (e.g., clicking the wrong coordinate).
- **Lesson:** The **Human Analyst** is required for **Visual Calibration**. Agents excel at exhaustive execution, but humans provide the "Common Sense" breakthrough required to clear technical stalls.

## 4. 🐢 Biological Integrity over Development Speed
- **Finding:** We spent significantly more time on QA than on raw coding.
- **Lesson:** In a **Clinical System**, the code is secondary to the **Data Witness**. 10 hours spent on a "SQL Pincer" validation is more valuable than 10 hours of new feature development, as it guarantees the survival of the biological records.

---
*Verified for 2026 Enterprise Standards (v1.4.2)*
