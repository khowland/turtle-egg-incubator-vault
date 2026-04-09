-- =============================================================================
-- Migration: 20260408_CHANGE_2002.sql
-- Project:   Incubator Vault v7.2.0 — WINC
-- Purpose:   Implementing Species IntakeCount tracker.
-- =============================================================================

-- 1. Species Counter Implementation
-- Tracks the sequential intake events per Wisconsin species for Bin Code generation.
ALTER TABLE species ADD COLUMN IF NOT EXISTS intake_count INTEGER DEFAULT 0;

-- Optionally initialize existing records to 0 if null
UPDATE species SET intake_count = 0 WHERE intake_count IS NULL;
