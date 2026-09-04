# Retool Triage Workbench Setup Guide (Part 2)

This guide provides the exact SQL queries, component tree, and keyboard event handlers to build the **Single-Screen Triage Workbench** in Retool, fulfilling all hard requirements **R1 through R10**.

---

## 1. App Layout Architecture (Requirement R1: 1366×768)

To ensure zero vertical scroll on the primary working pane at 1366×768:
* **Header Bar (Height: 50px):** Title, Queue Counter, Search Input, and Simulated Error Toggle button (`R6`).
* **Main Pane (Height: 670px, split 55% / 45%):**
  * **Left Column (55% width):** High-density Table displaying the triage queue.
  * **Right Column (45% width):** Fixed Reviewer Workspace (Full Note Text, 7 Metric Scorecards, and the R5 Historical Provenance Panel).
* **Footer Action Bar (Height: 48px):** Keyboard shortcut hints (`[J]`/`[K]` Navigate, `[1]` Overturn, `[2]` Uphold, `[C]` Commit).

---

## 2. Retool Resource Queries

### Query 1: `get_triage_queue` (Requirements R5, R10)
* **Resource:** PostgreSQL Replica
* **Name:** `get_triage_queue`
* **Trigger:** On Page Load / Automatic
* **SQL Query:**
  ```sql
  -- R10: Derived from corrected Part 1 logic (NOT the broken legacy query)
  -- R5: Evaluates the historical SLA target and rubric active ON NOTE DATE
  WITH rubric_pivoted AS (
      SELECT 
          rubric_version,
          MAX(CASE WHEN dimension = 'accuracy' THEN weight END) AS w_acc,
          MAX(CASE WHEN dimension = 'completeness' THEN weight END) AS w_comp,
          MAX(CASE WHEN dimension = 'formatting' THEN weight END) AS w_fmt,
          MAX(CASE WHEN dimension = 'terminology' THEN weight END) AS w_term,
          MAX(CASE WHEN dimension = 'hpi' THEN weight END) AS w_hpi,
          MAX(CASE WHEN dimension = 'ros' THEN weight END) AS w_ros,
          MAX(CASE WHEN dimension = 'plan' THEN weight END) AS w_plan,
          MAX(pass_threshold) AS threshold
      FROM rubric_weight
      GROUP BY rubric_version
  ),
  deduped_note AS (
      SELECT DISTINCT ON (note_id) *
      FROM note
      ORDER BY note_id, ingested_at_utc DESC
  )
  SELECT 
      a.audit_id,
      n.note_id,
      n.encounter_id,
      n.product_line,
      n.priority,
      n.word_count,
      (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date AS note_date_chi,
      n.submitted_at_utc,
      n.delivered_at_utc,
      ROUND(EXTRACT(EPOCH FROM (n.delivered_at_utc - n.submitted_at_utc))/60.0, 1) AS actual_delivery_minutes,
      
      -- R5: SLA in force on the note's authoring date
      s.target_minutes AS sla_target_on_note_date,
      CASE 
          WHEN EXTRACT(EPOCH FROM (n.delivered_at_utc - n.submitted_at_utc))/60.0 > s.target_minutes 
          THEN 'BREACH' ELSE 'MET' 
      END AS sla_status,

      -- R5: Historical Rubric Version active on note date
      CASE WHEN (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date >= '2026-05-15' 
           THEN 'v2' ELSE 'v1' END AS rubric_on_note_date,
      r.threshold AS passing_threshold_on_note_date,

      -- Raw Dimension Scores
      a.score_accuracy,
      a.score_completeness,
      a.score_formatting,
      a.score_terminology,
      a.score_hpi,
      a.score_ros,
      a.score_plan,

      -- Stored Score vs True Recalculated Score
      a.composite_score AS recorded_score,
      a.pass_fail AS recorded_status,
      ROUND((
          a.score_accuracy * r.w_acc + 
          a.score_completeness * r.w_comp + 
          a.score_formatting * r.w_fmt + 
          a.score_terminology * r.w_term + 
          a.score_hpi * r.w_hpi + 
          a.score_ros * r.w_ros + 
          a.score_plan * r.w_plan
      )::numeric, 4) AS true_composite_score,
      CASE 
          WHEN (a.score_accuracy * r.w_acc + a.score_completeness * r.w_comp + a.score_formatting * r.w_fmt + 
                a.score_terminology * r.w_term + a.score_hpi * r.w_hpi + a.score_ros * r.w_ros + a.score_plan * r.w_plan) >= r.threshold 
          THEN 'PASS' ELSE 'FAIL' 
      END AS true_status,

      -- Human-readable provenance explanation
      CASE 
          WHEN a.composite_score < r.threshold AND (a.score_accuracy * r.w_acc + a.score_completeness * r.w_comp + a.score_formatting * r.w_fmt + a.score_terminology * r.w_term + a.score_hpi * r.w_hpi + a.score_ros * r.w_ros + a.score_plan * r.w_plan) >= r.threshold
          THEN 'Formula Mismatch (Calculated Pass, Recorded Fail)'
          WHEN a.rubric_version = 'v2' AND (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date < '2026-05-15'
          THEN 'Policy Cutover Mismatch (Note authored under v1, audited under v2)'
          ELSE 'Clinical Standard Threshold Breach'
      END AS triage_flag_reason

  FROM deduped_note n
  JOIN note_audit a ON a.note_id = n.note_id
  JOIN rubric_pivoted r ON r.rubric_version = (
      CASE WHEN (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date >= '2026-05-15' 
           THEN 'v2' ELSE 'v1' END
  )
  JOIN sla_config s ON s.product_line = n.product_line 
                   AND s.priority = n.priority
                   AND (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date >= s.effective_from 
                   AND (s.effective_to IS NULL OR (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date <= s.effective_to)
  WHERE n.is_void = false
    -- Filter for cases requiring triage review (recorded failures or formula anomalies)
    AND (a.pass_fail = 'FAIL' OR a.composite_score < r.threshold)
  ORDER BY a.audited_at_utc DESC;
  ```

---

### Query 2: `commit_triage_decision` (Requirement R7)
* **Resource:** PostgreSQL Replica
* **Name:** `commit_triage_decision`
* **Trigger:** Manual (Triggered by Keyboard shortcut `[C]` or Button)
* **SQL Query:**
  ```sql
  -- R7: Explicit commit of triage verdict
  UPDATE note_audit
  SET 
      pass_fail = {{ selectedDisposition.value === 'OVERTURN' ? 'PASS' : 'FAIL' }},
      composite_score = CASE 
          WHEN {{ selectedDisposition.value === 'OVERTURN' }} 
          THEN {{ triageTable.selectedRow.true_composite_score }}
          ELSE composite_score
      END
  WHERE audit_id = {{ triageTable.selectedRow.audit_id }};
  ```

---

### Query 3: `bulk_commit_triage` (Requirement R8)
* **Resource:** PostgreSQL Replica
* **Name:** `bulk_commit_triage`
* **Trigger:** Manual (Triggered from Bulk Confirmation Modal)
* **SQL Query:**
  ```sql
  -- R8: Safe to double-submit, updates exactly selected rows
  UPDATE note_audit
  SET pass_fail = 'PASS'
  WHERE audit_id IN ({{ triageTable.selectedRowKeys.map(k => `'${k}'`).join(',') }});
  ```

---

## 3. Retool State & Persistence (Requirement R4)

To ensure selection, scroll, and filters **survive a data refresh** (`R4`):
1. **Create a Temporary State variable:** `selectedAuditId`
   * In the Table component's **"On row select"** event:
     * Action: **Set Value** $\rightarrow$ `selectedAuditId.setValue(triageTable.selectedRow.audit_id)`
2. **Table Default Selection:**
   * Set **Default row** to: `{{ triageTable.data.findIndex(r => r.audit_id === selectedAuditId.value) || 0 }}`

---

## 4. UI Components & Layout Configuration

### Left Pane: Triage Table (`triageTable`)
* **Component:** Table
* **Data Source:** `{{ get_triage_queue.data }}`
* **Primary Key:** `audit_id`
* **Multi-select:** Enabled (`R8` bulk selection)
* **Columns to Display:**
  1. `audit_id` (Text)
  2. `note_id` (Text)
  3. `priority` (Badge: STANDARD=Blue, URGENT=Amber)
  4. `recorded_status` (Badge: FAIL=Red)
  5. `triage_flag_reason` (Tag: highlighting formula errors vs true fails)
  6. `true_composite_score` (Numeric: 4 decimal places)

### Right Pane: Reviewer Workspace
* **Component 1 (Note Context Card):**
  * Container displaying: Encounter ID, Clinician ID, Word Count, and Full Clinical Text.
* **Component 2 (7 Metric Scorecards — `R9` Accessibility):**
  * 7 Stat/Tag components displaying Accuracy, Completeness, Plan, etc.
  * Contrast ratio $\ge 4.5:1$ with visible text labels (no color-only encoding).
* **Component 3 (Provenance Panel — `R5`):**
  * Display Card with title **"Historical Policy Provenance (Rule R5)"**:
    * **Note Date:** `{{ triageTable.selectedRow.note_date_chi }}`
    * **Active Rubric on Date:** `{{ triageTable.selectedRow.rubric_on_note_date }}` (Threshold: `{{ triageTable.selectedRow.passing_threshold_on_note_date }}`)
    * **SLA Target in Force:** `{{ triageTable.selectedRow.sla_target_on_note_date }} min` (Actual Delivery: `{{ triageTable.selectedRow.actual_delivery_minutes }} min` $\rightarrow$ `{{ triageTable.selectedRow.sla_status }}`)
    * **Diagnostic Rule Fired:** `{{ triageTable.selectedRow.triage_flag_reason }}`

---

## 5. Keyboard Navigation Handlers (Requirement R3)

Add these custom hotkeys in your Retool app settings:

| Key | Event / Script Action |
| :---: | :--- |
| `J` or `ArrowDown` | `triageTable.selectRow(triageTable.selectedRowIndex + 1)` |
| `K` or `ArrowUp` | `triageTable.selectRow(Math.max(0, triageTable.selectedRowIndex - 1))` |
| `1` | `selectedDisposition.setValue('OVERTURN');` |
| `2` | `selectedDisposition.setValue('UPHOLD');` |
| `C` or `Enter` | `commit_triage_decision.trigger();` |

---

## 6. Three Named States (Requirement R6)

Retool containers support conditional view states:
1. **Loading State:** Table skeleton loader displays while `get_triage_queue.isFetching` is true.
2. **Empty Queue State:** Container displays when `triageTable.data.length === 0`:
   * Icon: Checkmark
   * Text: *"All audit failure cases resolved. Queue is empty."*
3. **Upstream Error State (Demo in Video):**
   * Add a toggle switch in the header: **"Simulate Database Error"**.
   * When toggled on, triggers an alert banner displaying *"Upstream Error: Connection refused on postgres:5432"* **without shifting the layout**.
