-- v8.2.2 VERSION BUMP (QA Milestone Release)
-- Date: 2026-04-29
-- Context: Complete E2E Playwright test suite — 34 new test cases across all clinical workflows
-- Tests cover: Wipe/Clean Start, Intake, Supplemental Intake, Bin Management,
--              Observations (S1-S6), Hatching, Surgical Corrections, Settings, Reports,
--              Session Management, and Performance thresholds.

UPDATE public.system_config
SET config_value = 'v8.2.2'
WHERE config_key = 'APP_VERSION';

-- Log the release event
INSERT INTO public.system_log (event_type, event_message, observer_id)
VALUES (
    'RELEASE',
    'QA Milestone v8.2.2: 34 new E2E Playwright tests added covering all clinical workflows. Master test plan at tests/e2e_playwright/MASTER_TEST_PLAN.md.',
    'SYSTEM'
);
