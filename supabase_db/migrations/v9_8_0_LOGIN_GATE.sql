-- ============================================================
-- MIGRATION: v9.8.0 — Login Gate Authentication
-- Adds AUTH_PIN config and verify_pin RPC for PIN-based auth
-- ============================================================

-- 1. Insert default AUTH_PIN (numeric, 6-digit) if not exists
INSERT INTO public.system_config (config_name, config_value, description)
SELECT 'AUTH_PIN', '123456', '6-digit numeric PIN for user authentication'
WHERE NOT EXISTS (SELECT 1 FROM public.system_config WHERE config_name = 'AUTH_PIN');

-- 2. RPC to verify PIN (never exposes the actual PIN to client)
CREATE OR REPLACE FUNCTION public.verify_pin(input_pin TEXT)
RETURNS BOOLEAN
SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
LANGUAGE plpgsql
AS $$
DECLARE
    stored_pin TEXT;
BEGIN
    SELECT config_value INTO stored_pin
    FROM public.system_config
    WHERE config_name = 'AUTH_PIN';

    RETURN stored_pin = input_pin;
END;
$$;
