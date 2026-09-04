# Operational Data Reconciliation & Architectural Risk Briefing

**Document:** `RECONCILIATION.md`  
**Author:** Senior Business Intelligence & Database Engineer  
**Date:** September 4, 2026  
**Audience:** VP Global Operations, Head of Product (LT), QA Lead, HR Business Partner  
**Subject:** Forensic Audit of Q2 FY26 Ambient Operations Review & Remediation Plan  

---

## 1. Executive Summary

A forensic review of the operational replica and the legacy reporting script (`PROVIDED_QUERIES.sql`) reveals that **every single metric reported in the Q2 FY26 Ambient Ops Review (`APPENDIX_A_Q2_REVIEW.md`) is mathematically or methodologically invalid**.

The reported "quality collapse" (79.9% pass rate) and "SLA degradation" (12.8% breach rate) are artifacts of **SQL syntax errors, Cartesian fan-outs from unconstrained schema, unhandled API rate limits, and zero calendar awareness**.

| Metric | Reported in Q2 Review | True Reconciled Value | Core Root Cause of Discrepancy |
| :--- | :---: | :---: | :--- |
| **Notes Audited in Quarter** | 1,705 | **1,566** | Cartesian fan-out on SCD-2 clinician table (+132 rows) minus June 30 boundary truncation (-27 rows). |
| **Audit Pass Rate** | 79.9% | **77.0% (True v2)** / **80.1% (Policy v1)** | 150 corrupted composite score calculations in ETL + applying v2 rubric retroactively to v1 notes. |
| **Average Composite Score** | 0.9055 | **0.9161** | ETL calculation error depressed actual clinical quality scores. |
| **Delivery SLA Breach Rate** | 12.8% | **10.4%** | Analyst filtered only for notes with *open escalations* (selection bias) & double-counted SLA rows. |
| **Median Delivery Latency** | 18.5 min | **18.1 min** | 18.5 min was standard priority only; whole-population median is 18.1 min. |
| **Genuinely Open Escalations** | 149 | **110** | 43 cases are stranded HTTP 429 errors never posted to Slack; 1 open case is on a voided encounter. |
| **Volume Anomaly Days** | 28 of 91 days | **0 genuine anomalies** | Script flagged 26 weekends and 2 federal holidays due to lack of a business calendar. |

### Immediate Leadership Guidance:
* **Decision A ($410K Remediation Program & QA Headcount): REJECT / HALT.** Clinician documentation has not collapsed. True composite scores average 0.9161 (above target). The gap was caused by ETL calculation errors and premature enforcement of the tightened 90% pass threshold on notes authored before the May 15 policy cutover.
* **Decision B (MDS Leaderboard Award & Disciplinary Coaching Plan): DO NOT EXECUTE.** The leaderboard includes **inactive employees** (placing departed employee **MD-201** on a PIP and awarding departed employee **MD-218**). Furthermore, active specialists (**MD-204**, **MD-210**) were unfairly pushed into the bottom tier by corrupted scoring calculations.

---

## 2. Table-by-Table Grain & Uniqueness Profiling

Before altering queries, we characterized all 7 tables in PostgreSQL 14/15 to uncover where the physical data contradicts the data dictionary:

### 2.1 Table: `clinician`
* **Assumed Grain:** One row per clinician (`clinician_id` as primary key).
* **Actual Grain:** One row per clinician *per licensing/effective date range* (**Slowly Changing Dimension Type 2**).
* **Data Conflict:** Exactly **4 clinicians** (`CL-1004`, `CL-1018`, `CL-1029`, `CL-1045`) have 2 rows representing historical geographic transfers (e.g., Bram Adeyemi moving from `SOUTH` to `WEST`).
* **Operational Impact:** Naive joins on `clinician_id` duplicate **433 notes**. In `PROVIDED_QUERIES.sql` (Q1), table `clinician` was joined despite zero clinician attributes being selected, artificially inflating audited note counts by 132 rows.
* **True Unique Key:** `(clinician_id, record_effective_from)`.

### 2.2 Table: `note`
* **Assumed Grain:** One row per clinical documentation encounter (`note_id` as primary key).
* **Actual Grain:** One row per *ingestion payload* (`ingestion_id` as primary key).
* **Data Conflict:** When the capture pipeline retries or a client resubmits, a new ingestion row is appended. Exactly **62 notes have multiple ingestion records** (e.g., `NT-000651` has `IG-000651-1` and `IG-000651-2`).
* **Operational Impact:** Joining downstream tables on `note_id` causes fan-out. 17 audits and 4 escalations match duplicate note rows. Furthermore, **90 notes are flagged `is_void = true`**, yet downstream operational systems continued processing them.
* **True Unique Key:** `ingestion_id`.

### 2.3 Table: `note_audit`
* **Assumed Grain:** One row per audit event (`audit_id` as primary key).
* **Actual Grain:** Confirmed 1:1 with `audit_id`.
* **Data Conflict:** 
  1. **Scoring Formula Corruption:** Exactly **150 audits under rubric `v2` have corrupted composite scores** where the stored `composite_score` contradicts the weighted sum of the 7 dimension scores. High-performing notes were hardcoded with failing scores (e.g., `AU-10829` evaluated to 0.9246, but was stored as 0.7890 FAIL).
  2. **Void Processing:** Exactly **18 audits were performed on voided notes**.
  3. **Temporal Policy Mismatch:** Exactly **39 notes authored before May 15 (under rubric v1)** were audited after May 15 and improperly evaluated against rubric `v2` (tightened 90% threshold).

### 2.4 Table: `escalation`
* **Assumed Grain:** One row per workflow escalation (`escalation_id` as primary key).
* **Actual Grain:** Confirmed 1:1 with `escalation_id`.
* **Data Conflict:** 
  1. **The 43 Stranded Cases:** Exactly **43 escalations have status `PENDING_POST` and `last_api_error = 'slack_api:ratelimited (HTTP 429)'`** with `slack_thread_ts IS NULL`. They were dropped by the Slack integration and were never delivered to triage leads.
  2. **Chronological Violations:** Exactly **20 escalations have `created_at_utc` occurring up to 40 days BEFORE `note.submitted_at_utc`**, indicating synthetic batch clock skew.
  3. **Void Processing:** Exactly 7 escalations were raised on voided notes (1 currently open).

### 2.5 Table: `mds`
* **Assumed Grain:** One row per Medical Documentation Specialist (`mds_id` as primary key).
* **Actual Grain:** Confirmed 1:1 with `mds_id` (34 specialists).
* **Data Conflict:** 5 of the 34 specialists have `status = 'INACTIVE'`. The reporting queries did not filter for active staff.

### 2.6 Table: `sla_config` & `rubric_weight`
* **Assumed Grain:** Static configuration parameters.
* **Actual Grain:** **Time-versioned policy rules**.
  * `sla_config`: Targets tightened on **2026-05-15** (e.g., Ambient Assist Standard dropped from 45 min to 30 min).
  * `rubric_weight`: Rubric cutover on **2026-05-15** (threshold raised from 0.85 to 0.90, accuracy weight raised from 0.30 to 0.35).
* **Data Conflict:** Legacy reporting queries joined configuration tables without date validity checks, applying current rules retroactively.

---

## 3. Defining & Defending "The Quarter"

* **Operational Reality:** Northwind Ambient Ops contracts, clinician commitments, and operational shifts run on the **America/Chicago business day**.
* **Database Storage:** All database columns are stored as naive UTC timestamps (`TIMESTAMP WITHOUT TIME ZONE`).
* **The Reconciliation Boundary:**
  * **Quarter Definition:** Q2 FY26 spans **2026-04-01 00:00:00 CDT to 2026-06-30 23:59:59 CDT**.
  * **In UTC terms:** **2026-04-01 05:00:00 UTC to 2026-07-01 05:00:00 UTC**.
  * **The Analyst's Query Bug:** `PROVIDED_QUERIES.sql` used:
    ```sql
    WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30'
    ```
    In SQL, `TIMESTAMP '2026-06-30'` evaluates to `2026-06-30 00:00:00`. The analyst **completely truncated the final 24 hours of the quarter**, dropping 83 encounters submitted on June 30.

---

## 4. Metric Variance Waterfalls

### 4.1 Documentation Quality: Notes Audited & Audit Pass Rate

The prompt notes: *"Two of the corrections you will find move the pass rate in opposite directions, so a partial fix can land you further from the truth."*

* **Opposing Vector 1 (Recalculating True Composite Scores):** Moves pass rate **DOWN (-2.94%)** because under rubric `v2` (90% threshold), several recorded passes actually failed the stricter standard.
* **Opposing Vector 2 (Aligning Rubric to Note Date):** Moves pass rate **UP (+0.25%)** because pre-May 15 notes are restored to the 85% passing threshold.

```
                  AUDIT PASS RATE VARIANCE WATERFALL
 82% ───────────────────────────────────────────────────────────
      79.94%   79.91%   79.75%                             80.05% (Policy v1)
 80% ───██───────██───────██─────────────────────────██───────██
        │        │        │                 77.06%   │        │
 78% ───│────────│────────│────────76.81%─────██─────│────────│
        │        │        │          ██       │      │        │
 76% ───┴────────┴────────┴──────────┴────────┴──────┴────────┴────
       Step 0   Step 1   Step 2    Step 3   Step 4  Step 5-7 Final
```

| Step | Correction Applied | Population (Audits) | Pass Rate (%) | Avg Composite | $\Delta$ Audits | $\Delta$ Pass Rate | Description / Attribution |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **Reported Figure (Q1)** | **1,705** | **79.94%** | **0.9055** | — | — | Legacy query with June 30 truncation & clinician fan-out. |
| **1** | Fix June 30 Date Truncation | 1,732 | 79.91% | 0.9049 | +27 | -0.03% | Expands `BETWEEN` to include all 24 hours of June 30. |
| **2** | Remove Clinician SCD-2 Fan-out | 1,600 | 79.75% | 0.9047 | -132 | -0.16% | Drops unneeded join on `clinician` that duplicated notes. |
| **3** | Recalculate Composite Scores | 1,600 | 76.81% | 0.9165 | 0 | **-2.94%** | Fixes 150 corrupted scores against rubric dimensions (**Vector 1**). |
| **4** | Rubric Version by Note Date | 1,600 | 77.06% | 0.9165 | 0 | **+0.25%** | Restores 39 pre-May 15 notes to v1 (85% threshold) (**Vector 2**). |
| **5** | Exclude Voided Encounters | 1,584 | 76.96% | 0.9163 | -16 | -0.10% | Removes audits conducted on retracted encounters. |
| **6** | Deduplicate Re-ingested Notes | 1,567 | 77.03% | 0.9162 | -17 | +0.07% | Resolves duplicate `note_id`s to the active ingestion version. |
| **7** | Localize to America/Chicago | **1,566** | **77.01%** | **0.9161** | -1 | -0.02% | Final reconciled Q2 business quarter in local operational time. |

* **Note on Policy Interpretation:** If leadership chooses to evaluate all notes authored prior to May 15 under the v1 standard (as contracted), the pass rate is **80.1%**. If evaluated strictly under post-migration rules, it is **77.0%**. In neither case was the pass rate 79.94% over 1,705 notes.

---

### 4.2 Delivery SLA Breach Rate & Measured Population

The legacy query reported a **12.8% breach rate** across **296 measured notes**.

* **The Catastrophic Bug:** The analyst wrote:
  ```sql
  LEFT JOIN escalation e ON e.note_id = n.note_id
  WHERE ... AND e.status <> 'RESOLVED';
  ```
  In SQL, filtering on a left-joined table in `WHERE` converts the join to an **`INNER JOIN`**. The analyst measured delivery latency **only for encounters with unresolved operational escalations**, ignoring the 5,000+ smoothly delivered notes.
* **The Double-Counting Bug:** Joining `sla_config` without effective dates matched both old and new targets, doubling row counts from 148 notes to 296 rows.

| Step | Correction Applied | Measured Notes | Breach Rate (%) | Median Latency | $\Delta$ Notes | $\Delta$ Breach Rate | Description / Attribution |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **Reported Figure (Q2)** | **296** | **12.84%** | **18.45 min** | — | — | Measured open escalations only; doubled SLA rows. |
| **1** | Remove Escalation Filter | 11,012 | 10.17% | 18.12 min | +10,716 | -2.67% | Restores full note delivery population (still doubled). |
| **2** | Effective-Dated SLA Matching | 5,506 | 10.15% | 18.12 min | -5,506 | -0.02% | Matches target active on note submission date. |
| **3** | Fix June 30 Truncation | 5,589 | 10.29% | 18.12 min | +83 | +0.14% | Adds missing June 30 deliveries. |
| **4** | Exclude Void Encounters | 5,509 | 10.35% | 18.10 min | -80 | +0.06% | Removes retracted notes from SLA measurement. |
| **5** | Deduplicate Active Notes | 5,448 | 10.43% | 18.12 min | -61 | +0.08% | Resolves multi-ingestion notes to latest version. |
| **6** | Localize to America/Chicago | **5,449** | **10.41%** | **18.12 min** | +1 | -0.02% | True Q2 delivery population performance. |

---

### 4.3 Escalation Health & Genuinely Open Escalations

The legacy query reported **149 open escalations** with an average response time of **49.5 minutes**.

* **Root Cause:** In Q2 (UTC), exactly 151 escalations were unresolved:
  * **108 were status `OPEN`** (legitimately active triage cases).
  * **43 were status `PENDING_POST`** (stranded cases dropped by Slack HTTP 429 errors).
  * $106 \text{ (truncated Q2)} + 43 = 149$.
* **The Reality:** 43 of the 149 reported escalations were never posted to Slack. They were never seen by an operator, received no human response, and sat abandoned in the database.

| Step | Correction Applied | Open Cases | Avg Response Time | $\Delta$ Cases | Description / Attribution |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **0** | **Reported Figure (Q5)** | **149** | **49.5 min** | — | Truncated June 30; combines OPEN and PENDING_POST. |
| **1** | Fix June 30 Boundary | 151 | 49.0 min | +2 | Captures full calendar quarter. |
| **2** | Segregate Stranded HTTP 429 Cases | 108 | 49.0 min | -43 | Isolates 43 unworked, unposted Slack dropouts. |
| **3** | Exclude Void Encounters | 109 | 49.1 min | +1 | Removes 1 open escalation attached to a voided encounter. |
| **4** | Exclude Pre-Submission Paradoxes | 109 | 49.1 min | 0 | Flags 20 clock-skewed escalations logged before notes. |
| **5** | Localize to America/Chicago | **110** | **49.0 min** | +1 | **True genuinely open, operator-actionable queue.** |

---

### 4.4 Volume Anomaly Alert: The "28 of 91 Days" Debunked

The review memo stated: *"The daily volume alert flagged 28 of 91 days as anomalous (>30% below trailing 14-day average). This is a sharp deterioration in demand stability."*

* **The Reality:** The query compared daily volume against a 14-day trailing average without a weekday mask.
* **The Calendar Math:**
  * Total Calendar Days in Q2 FY26 (Apr 1 – Jun 30): **91 days**
  * Saturdays and Sundays in Q2: **26 days**
  * Federal Holidays (Outpatient Clinics Closed): **2 days**
    * *Memorial Day:* Monday, May 25, 2026
    * *Juneteenth:* Friday, June 19, 2026
  * Total Non-Operational Days: $26 + 2 =$ **28 days**!
* **Conclusion:** There was **zero genuine volume anomaly**. Outpatient clinics close on weekends and holidays, causing note intake to naturally drop from ~80/day to ~25/day. The anomaly alert is an artifact of an amateur SQL query lacking business calendar awareness.

---

## 5. Executive Decisions Evaluation (≤400 Words)

### Is Decision A Justified?
**No. Decision A ($410K for mandatory pod retraining, increased audit coverage, and +1 QA headcount) is unjustified and should be halted immediately.**

The reported 79.9% pass rate does not reflect a clinical documentation collapse. It was driven by three technical defects:
1. **ETL Formula Corruption:** 150 audits had corrupted composite scores; true scores evaluated to a **0.9161 average** (above the 0.90 quality target).
2. **Policy Back-Dating:** 39 notes authored before May 15 were improperly judged against the stricter v2 rubric (90% threshold vs. active 85% threshold).
3. **Cartesian Inflation:** Joining the SCD-2 `clinician` table duplicated 132 audit rows.

Clinician documentation is meeting clinical standards. Investing $410K would burn budget attempting to fix an operational problem that exists purely as a SQL calculation bug.

### Is Decision B Safe to Execute?
**No. Decision B (awarding the top MDS and placing the bottom five on HR coaching plans) is dangerous, legally risky, and operationally unfair.**

1. **Inactive Employees Punished and Rewarded:**
   * **MD-201 (Noor Achebe)** has status `INACTIVE` (terminated/departed). Placing an ex-employee on a 60-day HR coaching plan is a severe governance embarrassment.
   * **MD-218 (Emeka Petronella)** has status `INACTIVE`, yet ranked #2 for the recognition award.
2. **Unfair Relegation of Active Specialists:**
   * **MD-204 (Beatriz Kowalski)** and **MD-210 (Bram Castellanos)** were relegated to the bottom tier solely because corrupted `v2` scoring math artificially depressed their composite scores. Under corrected scoring, both achieve passing rates above 78% and belong in the middle tiers.
3. **True Top Performer:**
   * **MD-228 (Ana Marchetti)** legitimately earns #1 with an active **88.9% pass rate** and **0.9362 average score**.

```sql
-- PROOF QUERY: Inactive employees and true ranks in Decision B
SELECT 
    m.mds_id,
    m.mds_name,
    m.status,
    COUNT(DISTINCT n.note_id) AS true_notes_handled,
    ROUND(AVG(a.composite_score)::numeric, 4) AS corrupted_score,
    ROUND(AVG(
        a.score_accuracy * r.w_acc + a.score_completeness * r.w_comp + 
        a.score_formatting * r.w_fmt + a.score_terminology * r.w_term + 
        a.score_hpi * r.w_hpi + a.score_ros * r.w_ros + a.score_plan * r.w_plan
    )::numeric, 4) AS true_score
FROM mds m
JOIN note n ON m.mds_id = n.mds_id
JOIN note_audit a ON n.note_id = a.note_id
JOIN (
    SELECT rubric_version,
           MAX(CASE WHEN dimension = 'accuracy' THEN weight END) AS w_acc,
           MAX(CASE WHEN dimension = 'completeness' THEN weight END) AS w_comp,
           MAX(CASE WHEN dimension = 'formatting' THEN weight END) AS w_fmt,
           MAX(CASE WHEN dimension = 'terminology' THEN weight END) AS w_term,
           MAX(CASE WHEN dimension = 'hpi' THEN weight END) AS w_hpi,
           MAX(CASE WHEN dimension = 'ros' THEN weight END) AS w_ros,
           MAX(CASE WHEN dimension = 'plan' THEN weight END) AS w_plan
    FROM rubric_weight GROUP BY rubric_version
) r ON a.rubric_version = r.rubric_version
WHERE n.submitted_at_utc >= '2026-04-01' AND n.submitted_at_utc < '2026-07-01'
GROUP BY m.mds_id, m.mds_name, m.status
ORDER BY true_score DESC;
```

---

## 6. Known Unknowns (What Was Not Checked)

1. **Root Cause of the 150 Corrupted Scores:** We identified that `composite_score` does not match the dimension weights in 150 cases, but we do not have access to the upstream ETL code that generated these records. We need the ETL pipeline commit history around the May 15 cutover.
2. **Clinical Intent on Voided Notes:** 18 voided notes were audited and 7 were escalated. We cannot determine whether clinicians voided the encounters *before* or *after* operational processing occurred without access to EHR audit logs.
3. **Slack Webhook Infrastructure:** We confirmed 43 escalations failed with HTTP 429, but do not know whether the rate limit was caused by webhook token throttling or a concurrency spike across multiple pods.
4. **Retroactive Clinician Transfers:** For the 4 clinicians with SCD-2 records, historical encounter reassignment was based on `submitted_at_utc`. If a clinician's transfer date was back-dated in HR systems, some encounters may belong to previous cost centers.

---

## 7. Architectural Risk Briefing: Why Operating Without Constraints is Fatal

Operating an operational replica without **Primary Keys (PKs)**, **Foreign Keys (FKs)**, and **Indexes** creates severe architectural hazards:

1. **Silent Cartesian Inflation:** Without PKs, analysts assume keys are 1:1. The SCD-2 clinician structure and multi-ingestion notes silently multiplied rows, distorting board-level financial and SLA metrics.
2. **Acceptance of Corrupted States:** Without domain and foreign key constraints, the database happily ingested escalations created 40 days before encounter submissions and audits conducted on voided encounters.
3. **Catastrophic Latency:** Every join and filter forces unindexed sequential table scans. At production scale (millions of notes), reporting dashboards will suffer query timeouts and connection starvation.
4. **Remediation:** Raw data must land in a dedicated `stg_*` schema, transform through deduplication pipelines, and load into a constrained `core_*` serving schema enforcing strict composite primary keys, foreign keys, and B-tree indexes.
