# ADR-002: Concurrency Guards and Idempotency in Stranded Escalation Recovery

## Status
Accepted

## Context
Exactly 43 escalations failed due to Slack API rate limiting (`HTTP 429`) and remain stranded in `PENDING_POST`. When re-dispatching alerts to webhooks, running concurrent recovery workflows risks double-posting the same alert to Slack and spamming triage channels.

## Options Considered
1. **Option 1: In-memory application lock (mutex/semaphore):** Does not scale across distributed Retool workflow instances or worker containers.
2. **Option 2: Pessimistic Table Lock (`LOCK TABLE escalation`):** Stops all operational triage processing during recovery runs.
3. **Option 3: PostgreSQL Row-Level Locking (`FOR UPDATE SKIP LOCKED`) + SHA-256 Idempotency Key:** Concurrency-safe queue pattern where workers lock only the rows they process, skipping locked rows if another worker is in-flight, combined with a unique `idempotency_key` constraint on the audit table.

## Decision
We chose **Option 3**. Recovery workers select stranded records using `SELECT ... FOR UPDATE SKIP LOCKED` and log each attempt with a deterministic idempotency key (`SHA256(escalation_id || ':' || attempt_count)`).

## Consequences
* **Positive:** Guaranteed zero duplicate posts even if multiple recovery workflows fire simultaneously (`W6`).
* **Positive:** Zero blocking overhead on normal operational triage queries.
* **Negative:** Requires PostgreSQL transaction management support in the database connector.
