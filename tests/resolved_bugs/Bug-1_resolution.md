---
component: "7_Diagnostic.py"
issue_type: "Vocabulary Compliance"
resolved: true
---
# Bug-1: Non-Standard Button Labels
**Issue**: The `7_Diagnostic.py` view instantiated buttons labeled `RUN`. This violates Rule §1, which strictly enforces the vocabulary map of `SAVE`, `CANCEL`, `ADD`, `REMOVE`, or `START`.
**Resolution**: The `RUN` labels were patched to `START`. Additionally, `test_adversarial_persistence.py` and `test_adversarial_ui_vocabulary.py` were written to deterministically prevent regression on adversarial conditions. Tests passed under AppTest simulating the DOM properly.
