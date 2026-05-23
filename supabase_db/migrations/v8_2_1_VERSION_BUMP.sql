-- v8.2.1 VERSION BUMP (Hotfix Release)
-- Date: 2026-04-27
-- Context: Resolve Observations Crashes & Standardize Stage Icons

UPDATE public.system_config 
SET config_value = 'v8.2.1' 
WHERE config_key = 'APP_VERSION';

-- Log the release event
INSERT INTO public.system_log (event_type, event_message, observer_id)
VALUES ('RELEASE', 'System hotfix v8.2.1: Resolved Observations screen crashes and finalized Settings Stage icons.', 'SYSTEM');
