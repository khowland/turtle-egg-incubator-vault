-- v8.2.3 VERSION BUMP (QA Test Suite Execution)
-- Date: 2026-04-29
-- Context: Post-wipe version bump after DB clean start reset.
-- Increments minor version from v8.2.2 → v8.2.3.

UPDATE public.system_config
SET config_value = 'v8.2.3'
WHERE config_key = 'APP_VERSION';

-- Log the release event
INSERT INTO public.system_log (event_type, event_message, observer_id)
VALUES (
    'RELEASE',
    'v8.2.3: Post-wipe version bump. Full pytest suite execution with Playwright DB wipe workflow.',
    'SYSTEM'
);
