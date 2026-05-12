# batchid

{
  "batch_id": "BATCH_2",
  "results": [
    {
      "tsk": "TSK-03",
      "test_name": "test_supplemental_intake_full_save[chromium]",
      "status": "FAILED",
      "duration_seconds": 59.30,
      "error_message": "AssertionError: DB FAILURE: Expected at least 2 bins after supplemental intake, got 1",
      "error_line": "tests/e2e_playwright/test_intake_extended.py:272",
      "root_cause": "The supabase RPC function responsible for creating a supplemental intake (likely 'create_supplemental_intake') is not inserting a new row into the bin_observation table. After a supplemental intake of a second batch of eggs into the same bin, the RPC should create a new bin_observation record with the appropriate stage (e.g., S1), but only one bin exists in the database. This is a backend logic bug in the supabase migration, not a test flake.",
      "remediation": "1. Locate the supabase migration that defines the 'create_supplemental_intake' RPC function (likely in supabase_db/migrations/). 2. Ensure the function logic correctly identifies that the intake is supplemental (bin already exists). 3. Insert a new row into 'bin_observation' with the correct stage (e.g., 'S1') and bin_id referenced from the existing bin. 4. Verify that the bin_observation table permits multiple rows per bin_id (no unique constraint on bin_id alone). 5. If the RPC is correct, add a short sleep or polling in the test after the supplemental intake to account for eventual consistency (but the root issue is backend)."
    },
    {
      "tsk": "TSK-06",
      "test_name": "test_non_sequential_stage_jump_blocked[chromium]",
      "status": "FAILED",
      "duration_seconds": 251.60,
      "error_message": "TimeoutError: Locator.click: Timeout 30000ms exceeded. waiting for locator(\\"[data-testid='stSelectboxVirtualDropdown'] li:has-text('S4')\\
