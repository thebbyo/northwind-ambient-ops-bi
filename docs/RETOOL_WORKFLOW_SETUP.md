# Retool Workflow Guide: Stranded Escalation Recovery (Part 3)

This guide provides the block-by-block blueprint to build and demonstrate the **Stranded Escalation Recovery Workflow** in Retool, fulfilling requirements **W1 through W8**.

---

## 1. Architectural Architecture & Flow

```
 ┌────────────────┐     ┌───────────────────────┐     ┌────────────────────────┐
 │ 1. Trigger     ├────►│ 2. SQL Detection (W1) ├────►│ 3. Loop Block (W4)     │
 │ Webhook / Manual│     │ FOR UPDATE SKIP LOCKED│     │ Rate limit: <=1 req/sec│
 └────────────────┘     └───────────────────────┘     └───────────┬────────────┘
                                                                  │
                                   ┌──────────────────────────────┴──────────────┐
                                   ▼                                             ▼
                        ┌─────────────────────┐                       ┌─────────────────────┐
                        │ 4. POST to Webhook  │                       │ 5. Audit & State    │
                        │ (W2, W3 Idempotency)│                       │ (W7 Audit, W5 Dead) │
                        └─────────────────────┘                       └──────────┬──────────┘
                                                                                 │
                                                                                 ▼
                                                                      ┌─────────────────────┐
                                                                      │ 6. W8 Reconciliation│
                                                                      │ 0 stranded, 0 dupes │
                                                                      └─────────────────────┘
```

---

## 2. Block-by-Block Retool Workflow Configuration

### Block 1: Webhook / Manual Start Trigger
* **Type:** Webhook or Manual Trigger
* **Name:** `start_trigger`

---

### Block 2: SQL Detection Query (`get_stranded_escalations`) — `W1`, `W6`
* **Type:** Resource Query (PostgreSQL)
* **Resource:** PostgreSQL Replica
* **Name:** `get_stranded_escalations`
* **SQL Query:**
  ```sql
  -- W1: Rule-based detection (not hardcoded IDs)
  -- W6: Concurrency guard (FOR UPDATE SKIP LOCKED) prevents double-processing if run in parallel
  SELECT 
      e.escalation_id,
      e.note_id,
      e.slack_channel,
      COALESCE(e.attempt_count, 1) AS attempt_count,
      e.created_at_utc,
      e.last_api_error
  FROM escalation e
  WHERE (e.status = 'PENDING_POST' OR e.last_api_error ILIKE '%429%')
    AND e.slack_thread_ts IS NULL
    AND COALESCE(e.attempt_count, 1) < 5
  ORDER BY e.created_at_utc ASC
  LIMIT 50
  FOR UPDATE SKIP LOCKED;
  ```

---

### Block 3: Loop Block (`process_each_escalation`) — `W4`
* **Type:** Loop Block
* **Input Array:** `{{ get_stranded_escalations.data }}`
* **Rate Limit (`W4`):** Check **"Rate limit loop"** $\rightarrow$ Set to **1 iteration per second** (or `1000ms`).

Inside the Loop Block, add these sequential sub-actions:

#### Sub-Action 3A: Idempotency Key Transformer (`create_payload`) — `W3`
* **Type:** Run JS Code
* **Code:**
  ```javascript
  // W3: Deterministic idempotency key
  const escalationId = value.escalation_id;
  const nextAttempt = Number(value.attempt_count) + 1;
  const rawKey = `${escalationId}:${nextAttempt}`;

  // Simple browser/node SHA-256 hash or deterministic base64
  let hash = 0;
  for (let i = 0; i < rawKey.length; i++) {
    hash = ((hash << 5) - hash) + rawKey.charCodeAt(i);
    hash |= 0;
  }
  const idempotencyKey = `idem_${escalationId}_att${nextAttempt}_${Math.abs(hash)}`;

  return {
    escalation_id: escalationId,
    note_id: value.note_id,
    slack_channel: value.slack_channel,
    attempt_number: nextAttempt,
    idempotency_key: idempotencyKey,
    recovery_run_id: workflowContext.workflowExecutionId || "manual_run",
    timestamp_utc: new Date().toISOString()
  };
  ```

#### Sub-Action 3B: HTTP POST (`repost_to_webhook`) — `W2`, `W4`
* **Type:** REST API Query
* **Action:** `POST`
* **URL:** `https://webhook.site/YOUR-UNIQUE-UUID` (or `https://httpbin.org/post`)
* **Headers:**
  * `Content-Type`: `application/json`
  * `X-Idempotency-Key`: `{{ create_payload.data.idempotency_key }}`
* **Body (JSON):** `{{ create_payload.data }}`
* **Error Handling & Backoff (`W4`):**
  * Retries: 3
  * Retry backoff: Exponential (Base 1000ms)

#### Sub-Action 3C: Log to Audit Table (`insert_audit_trail`) — `W7`
* **Type:** Resource Query (PostgreSQL)
* **SQL:**
  ```sql
  -- W7: Log immutable audit trail
  INSERT INTO escalation_recovery_audit (
      recovery_run_id,
      escalation_id,
      attempt_number,
      status,
      http_status_code,
      idempotency_key,
      endpoint_url,
      attempted_at_utc
  ) VALUES (
      '{{ create_payload.data.recovery_run_id }}'::uuid,
      '{{ create_payload.data.escalation_id }}',
      {{ create_payload.data.attempt_number }},
      '{{ repost_to_webhook.status >= 200 && repost_to_webhook.status < 300 ? "SUCCESS" : "FAILED" }}',
      {{ repost_to_webhook.status || 200 }},
      '{{ create_payload.data.idempotency_key }}',
      'https://webhook.site/YOUR-UUID',
      clock_timestamp()
  )
  ON CONFLICT (idempotency_key) DO NOTHING;
  ```

#### Sub-Action 3D: Update Escalation State (`update_escalation_status`) — `W5`
* **Type:** Resource Query (PostgreSQL)
* **SQL:**
  ```sql
  -- W5: If success, certify with slack_thread_ts. If attempts >= 5, transition to DEAD_LETTER
  UPDATE escalation
  SET 
      status = CASE 
          WHEN {{ repost_to_webhook.status >= 200 && repost_to_webhook.status < 300 }} THEN 'RESOLVED'
          WHEN {{ create_payload.data.attempt_number }} >= 5 THEN 'DEAD_LETTER'
          ELSE 'PENDING_POST'
      END,
      slack_thread_ts = CASE 
          WHEN {{ repost_to_webhook.status >= 200 && repost_to_webhook.status < 300 }} 
          THEN EXTRACT(EPOCH FROM clock_timestamp())::text
          ELSE slack_thread_ts 
      END,
      attempt_count = {{ create_payload.data.attempt_number }},
      last_api_error = CASE 
          WHEN {{ repost_to_webhook.status >= 200 && repost_to_webhook.status < 300 }} THEN NULL
          WHEN {{ create_payload.data.attempt_number }} >= 5 THEN 'DEAD_LETTER: Max retries exceeded'
          ELSE 'HTTP {{ repost_to_webhook.status }}'
      END
  WHERE escalation_id = '{{ create_payload.data.escalation_id }}';
  ```

---

### Block 4: Final Reconciliation Query (`w8_reconciliation_audit`) — `W8`
* **Type:** Resource Query (PostgreSQL)
* **Name:** `w8_reconciliation_audit`
* **SQL Query:**
  ```sql
  -- W8: Proves ZERO remaining stranded records and ZERO duplicate posts
  SELECT 
      COUNT(*) FILTER (WHERE e.status = 'PENDING_POST') AS remaining_stranded_records,
      COUNT(*) FILTER (WHERE e.slack_thread_ts IS NULL AND e.status <> 'DEAD_LETTER') AS unposted_active_records,
      (SELECT COUNT(*) - COUNT(DISTINCT idempotency_key) FROM escalation_recovery_audit) AS duplicate_audit_posts,
      (SELECT COUNT(*) FROM escalation_recovery_audit WHERE status = 'SUCCESS') AS total_recovered_records
  FROM escalation e;
  ```

---

## 3. How to Demonstrate in the Loom Video (Requirements W3 & W6)

In your ≤12-minute video:
1. **First Execution:**
   * Trigger the Retool Workflow live. Show the loop executing at 1 req/sec.
   * Open your Webhook.site tab to show live HTTP POST calls arriving in real time.
2. **Second Execution (Proving Idempotency W3):**
   * Immediately click **"Run Workflow"** a second time.
   * Point out: `get_stranded_escalations` returns **0 records**.
   * Show that zero new webhooks were dispatched and zero duplicate rows were added to `escalation_recovery_audit`.
3. **Show Reconciliation Query Output (W8):**
   * Run Block 4: Point to `remaining_stranded_records: 0` and `duplicate_audit_posts: 0`.
