-- ============================================================
-- MIGRATION: v9.8.2 — Rename session_log.user_name → observer_name
-- ============================================================
-- Purpose: Align session_log column name with observer table
--          (observer.observer_name) for schema consistency.
-- Breaks:  Login.tsx:80 and identity.ts:42 until frontend is
--          updated to write to observer_name instead of user_name.
-- ============================================================

BEGIN;

-- 1. Check pre-migration state
DO $$
DECLARE
  col_exists boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'session_log'
      AND column_name = 'user_name'
  ) INTO col_exists;

  IF NOT col_exists THEN
    RAISE EXCEPTION 'Column user_name does not exist — migration already applied?';
  END IF;
END $$;

-- 2. Rename column
ALTER TABLE public.session_log
  RENAME COLUMN user_name TO observer_name;

-- 3. Post-migration verification
DO $$
DECLARE
  new_col_exists boolean;
  old_col_exists boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'session_log'
      AND column_name = 'observer_name'
  ) INTO new_col_exists;

  SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'session_log'
      AND column_name = 'user_name'
  ) INTO old_col_exists;

  IF NOT new_col_exists THEN
    RAISE EXCEPTION 'Migration failed: observer_name column not found';
  END IF;

  IF old_col_exists THEN
    RAISE EXCEPTION 'Migration failed: user_name column still exists';
  END IF;

  RAISE NOTICE 'Migration v9.8.2 applied successfully: session_log.user_name → observer_name';
END $$;

COMMIT;
