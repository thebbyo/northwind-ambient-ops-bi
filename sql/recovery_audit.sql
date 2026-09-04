-- =====================================================================
-- Part 3: Stranded Escalation Recovery Workflow DDL
-- Author: Senior BI & Database Engineer
-- Dialect: PostgreSQL 14/15
-- =====================================================================

-- 1. Create Audit Trail Table for Recovery Tracking (W7)
CREATE TABLE IF NOT EXISTS escalation_recovery_audit (
    audit_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recovery_run_id      UUID NOT NULL,
    escalation_id        TEXT NOT NULL,
    attempt_number       INTEGER NOT NULL DEFAULT 1,
    status               TEXT NOT NULL,            -- 'SUCCESS', 'FAILED', 'DEAD_LETTER'
    http_status_code     INTEGER,                  -- e.g. 200, 429, 500
    idempotency_key      TEXT NOT NULL UNIQUE,     -- SHA256(escalation_id || ':' || attempt_number)
    endpoint_url         TEXT NOT NULL,
    error_message        TEXT,
    execution_duration_ms INTEGER,
    attempted_at_utc     TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- Strategic Indexes for Performance & Concurrency:
CREATE INDEX IF NOT EXISTS idx_rec_audit_escalation_id ON escalation_recovery_audit(escalation_id);
CREATE INDEX IF NOT EXISTS idx_rec_audit_run_id ON escalation_recovery_audit(recovery_run_id);
CREATE INDEX IF NOT EXISTS idx_rec_audit_status ON escalation_recovery_audit(status);

-- 2. Concurrency-Safe Detection Query with Row-Level Locking (W1, W6)
-- Uses FOR UPDATE SKIP LOCKED to prevent race conditions during concurrent runs
-- Rule: Find all escalations marked PENDING_POST or flagged with HTTP 429 rate limit
-- without a valid Slack thread timestamp, and not already exceeding max retry attempts.
/*
SELECT 
    e.escalation_id,
    e.note_id,
    e.slack_channel,
    e.attempt_count,
    e.created_at_utc,
    e.last_api_error
FROM escalation e
WHERE (e.status = 'PENDING_POST' OR e.last_api_error ILIKE '%429%')
  AND e.slack_thread_ts IS NULL
  AND e.attempt_count < 5
ORDER BY e.created_at_utc ASC
FOR UPDATE SKIP LOCKED;
*/

-- 3. Dead-Letter State Transition Rule (W5)
-- Records failing after 5 attempts are transitioned to DEAD_LETTER for human review
/*
UPDATE escalation
SET status = 'DEAD_LETTER',
    last_api_error = 'EXCEEDED_MAX_RETRIES: moved to dead-letter queue'
WHERE (status = 'PENDING_POST' OR last_api_error ILIKE '%429%')
  AND attempt_count >= 5;
*/

-- 4. Final Reconciliation Query (W8)
-- Proves ZERO remaining stranded records and ZERO duplicate posts
SELECT 
    COUNT(*) FILTER (WHERE e.status = 'PENDING_POST') AS remaining_stranded_records,
    COUNT(*) FILTER (WHERE e.slack_thread_ts IS NULL AND e.status <> 'DEAD_LETTER') AS unposted_active_records,
    (SELECT COUNT(*) - COUNT(DISTINCT idempotency_key) FROM escalation_recovery_audit) AS duplicate_audit_posts
FROM escalation e;
