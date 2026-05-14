-- v8.2.0 VERSION BUMP
-- Date: 2026-04-27
-- Context: Red Team Remediation & Recovery Baseline

UPDATE public.system_config 
SET config_value = 'v8.2.0' 
WHERE config_key = 'APP_VERSION';

-- Log the release event
INSERT INTO public.system_log (event_type, event_message, observer_id)
VALUES ('RELEASE', 'System baseline updated to v8.2.0 following Red Team Remediation.', 'SYSTEM');
