---
title: Final Remediation Task List
tags:
  - tasks
  - remediation
component: system
issue_type: backlog
resolved: false
---
# 📝 Final Remediation Task List: Turtle-DB (2026)

Following the senior engineering audit and collaboration with the Turtle Expert, this list defines the critical path for production readiness.

## 🔧 Task 1: Global Sidebar Standardization (B-005)
- **Issue**: Individual views override the global sidebar, burying the "SHIFT END" forensic button.
- **Requirement**: Standardize sidebar ordering to ensure clinical visibility.
- **Status**: Pending Authorization.

## 🔧 Task 2: S6 Rollback Atomic Integrity (ISS-3)
- **Issue**: Rolling back an egg from S6 (Hatched) leaves orphaned rows in hatchling_ledger.
- **Requirement**: Implement atomic voiding of ledger entries during "Surgical Resurrection."
- **Status**: Pending Authorization.

## 🔧 Task 3: Test Suite Modernization (§12.5)
- **Issue**: Label-based testing is fragile to UI/emoji updates.
- **Requirement**: Migrate AppTest lookups from label="..." to key="...".
- **Status**: Pending Authorization.

## 🔧 Task 4: Critical Scope Fix (B-004)
- **Issue**: NameError in session.py crashes recovery logic.
- **Requirement**: Locally initialize supabase_client in show_splash_screen.
- **Status**: Pending Authorization.

## 🔧 Task 5: Clinical Mass Gate (§2)
- **Issue**: Intake lacks physical mass input, bypassing mandatory gate.
- **Requirement**: Insert st.number_input for mass in 2_New_Intake.py.
- **Status**: Pending Authorization.
