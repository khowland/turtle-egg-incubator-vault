# batchid

{
  "batch_id": "BATCH_1",
  "results": [
    {
      "test_name": "test_intake_full_fields_and_bin_nomenclature[chromium]",
      "status": "PASSED",
      "duration_seconds": 17.42,
      "failure_reason": null
    },
    {
      "test_name": "test_intake_multiple_eggs[chromium]",
      "status": "PASSED",
      "duration_seconds": 17.42,
      "failure_reason": null
    },
    {
      "test_name": "test_intake_cancel_button[chromium]",
      "status": "PASSED",
      "duration_seconds": 17.42,
      "failure_reason": null
    },
    {
      "test_name": "test_supplemental_intake_full_save[chromium]",
      "status": "FAILED",
      "duration_seconds": 17.38,
      "failure_reason": "DB FAILURE: Expected at least 2 bins after supplemental intake, got 1"
    },
    {
      "test_name": "test_50x_observation_loop[chromium]",
      "status": "FAILED",
      "duration_seconds": 44.42,
      "failure_reason": "TimeoutError waiting for Stage stSelectbox visibility; likely race condition or slow render"
    }
  ],
  "summary": {
    "total": 5,
    "passed": 3,
    "failed": 2,
    "timeout": 0,
    "error": 0
  },
  "notes": "TSK-03 supplemental intake failed due to RPC not creating a second bin; TSK-07 failed from UI timeout waiting for Stage dropdown, possibly a race condition after the scalability loop."
}
