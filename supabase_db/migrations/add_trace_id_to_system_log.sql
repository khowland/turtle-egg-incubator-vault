-- Migration: Add trace_id column to system_log for frontend-backend correlation
-- Part of Phase 3 Logging Remediation (P4)
ALTER TABLE system_log ADD COLUMN IF NOT EXISTS trace_id TEXT;
CREATE INDEX IF NOT EXISTS idx_system_log_trace_id ON system_log(trace_id);
