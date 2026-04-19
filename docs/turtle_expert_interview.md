# Clinical Workflow Interview: Turtle Incubator Specialist

**Objective:** To define authoritative clinical behaviors for edge cases in the Turtle-DB system to ensure 100% audit veracity and biological safety.

---

## 🟢 Scenario 1: Non-Viable Egg Lifecycle
In the middle of the season, a biologist identifies an egg that is no longer viable (e.g., severe molding, leaking, or collapsed).

1. **Terminology:** Do we call this "Dead", "Removed", or "Void"?
   A: Non-Viable
2. **State Mutation:** Should the egg status become `Dead` or should it be soft-deleted (`is_deleted=True`)?  
   A: Our standard is soft-delete always preferred to prevent orphans. Handle soft-deletes at UI level for visbility
3. **Audit Trail:** If the egg is removed, does it require a mandatory "Removal Reason" in the system log?
   A: yes request a required reason. Ask Turtle ex[pert for a list of egg removal reasons and provide a drop-down lookup for the user, with ability to write in/add their own reason]
4. **Resurrection:** Is there ever a scenario where a "Removed" egg is reinstated, or is that a permanent terminal state?
   A: Yes, user error, allow rollback or undo operations. But confirm it's not too late in terms of dependencies on that record. we need an entire batch of qa dealing with removals and rollback undos!

## 🟡 Scenario 2: Bin Retirement & Hatchling Ledger
A bin ("BIN-001") reaches the end of its cycle. Some eggs have hatched (S6), and some were non-viable.

1. **Gate Rule:** Should the system explicitly BLOCK the "REMOVE" button for a bin if there is even one egg still in an "Active" status?
   A: Yes, no removal with active eggs. Message user with clear simple reason 
2. **Orphan Handling:** If a bin is accidentally retired while containing active eggs, should those eggs be auto-moved to a "Ghost Bin" or should the retirement fail?
   A: can not retire bin with active eggs
3. **Hatchling Ledger:** Once all eggs in a bin are S6 (Hatched) or Dead, does the bin require a final "Closure Audit" summary before being removed from the dashboard?
   A: Yes, allow final bin closure observations or perhaps a simple note? whatever fits into the schema and functional logic flow the best with least complication and refactoring.

## 🔵 Scenario 3: Mid-Season Intake Additions
A mother ("CASE-2026-001") is still laying, or a new clutch from the same mother arrives after the initial intake was saved.

1. **Existing Bin Addition:** Can we add more eggs to an existing bin that already has eggs from 4 days ago? (Risk: Temperature/Humidity variance for different age eggs).
   A: absolutely yes, it happens with injured but laying mothers as normal workflow..
2. **New Bin to Existing Intake:** If the first bin is full, how should the UI handle adding "BIN-002" to "CASE-2026-001" mid-season? 
   A: require or prompt user to Add new bin. An Add bin button should be on observations screen requiring user to also enter at least 1+ egg(s). Adding eggs to existing bin should also be allowed on observation screen through an easy mechanism. All these mid season adds and removals of eggs and bins, and all permutations each require test cases.
3. **Identifier Collisions:** If we add 5 more eggs to Bin A (already containing eggs 1-10), do they become 11-15? Does the system need to prevent duplicate sequence numbers?
   A: egg numbers are sequential and immutable. the number in that bin is permaently assigned to that egg through its entire life/viability cycle.

## 🔴 Scenario 4: State Transition & Rollback
A user accidentally marks an egg as S6 (Hatched) but it was only S5 (Pipped). 

1. **Rollback Policy:** Which transitions are "Permitted Rollbacks"? (e.g., S2 -> S1? S6 -> S5?)
   A: 1 level at a time, with confirmation and handling of dependent related rows in other tables. User should be messaged with info pertaining to extent of rollback, what info will be lost. Rollbacks must be done in order of last in, first out rollback, always in reverse sequence of inserts..
2. **Forensic Integrity:** When a rollback occurs, should the previous (incorrect) observation be VOIDED or just superceded by a new one?
   A:  Rollback of an egg would obviously roll back all observations, but the user should have to remove observations first one at a time. so message user, can not roll back {entity} because it has observations attached. Remove each observation in reverse order to allow egg removal. same goes for bin. Require rollback of child rows first, one at a time. 
3. **Hatchling Record Deletion:** If S6 is rolled back to S5, must the corresponding entry in the `hatchling_ledger` be automatically soft-deleted?
   A: yes, roll back, BUT CONFIRM first!,  all relevant child rows that may affect later analytics or reporting

## 🌪️ Scenario 5: RBAC & Permission Delegation (Adversarial)
Currently, all biological staff have "Elevated" permissions to perform voids and bin removals.

1. **Role Separation:** Should "Correction Mode" (Voiding/Editing) be restricted to Senior Biologists only, or is it safer to let anyone fix their own mistakes immediately?
   A: no, this version has monolithic universal rights. Only two users will use the system this season.
2. **Double-Sign-Off:** For high-stakes deletions (like bin retirement), does the expert require a second observer's identifier to be entered, or is a simple confirmation toggle sufficient?
   A: nope, simply allow with warning message and consideration for any dependent child rows. QA testing should test all scenarios of higher order soft-deletes and correct representation of related child rows. QA needs to also test that soft-deletes are honored for all objects with soft-delete capability. confirm all relevant tables and related tables have appropriate soft delete capability as well, and that it is honored on every screen and report. Extensive QA test cases here.

## 🕒 Scenario 6: Session Handover & Stale Sessions
A biologist leaves a workstation active in the field without clicking "SHIFT END".

   A: I beleiev the browser times out anyway. When they launch th app again or restart, it should automatically launch user selection screen, and if same user is selected as last session within 4 hours, continue session. Otherwise start new session if new user is selected.
1. **Re-Auth:** When resuming an unattended session, should the system force the user to re-select their name?
   A: any unattended session will probably time out somewhere. But yes, perhaps a system induced timeout after 1 hour or something

## 🛡️ Scenario 7: Bin vs Egg Lifecycle Gates
A user attempts to "REMOVE" a bin from the dashboard.

1. **The Active Egg Gate:** Should the system explicitly forbid removing a bin if it contains eggs with status "Active"? 
   A: YES
2. **Historical Retention:** Once a bin is removed, should it disappear from the dashboard entirely, or move to a "Retired Bins" archive for late-season audit?
   A: users want to still have access to view observations and entries from prior bins or non-viable eggs. So they should be visible but visually greyed out or somehow flagged as "Completed", or "Removed" or for eggs "Non-Viable", or "Hatched" etc..

From Auditor: Note to QA: please ensure all test case notes I made are incorporated as testing scenarios, and ensure all permutations of potential stupid user actions are accounted for with test cases, edge test cases for real morons.
---

**Instruction to Auditor:** Please provide your clinical guidance for each scenario. Your answers will be used to generate the Phase 3.5 adversarial test suite.
