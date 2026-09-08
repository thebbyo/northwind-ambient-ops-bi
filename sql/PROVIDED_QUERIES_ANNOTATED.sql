-- =====================================================================
--  Northwind Ambient Ops — "production" reporting queries
--  Owner: Ops Analytics (departed).  Last edited: 2026-07-02.
--  These are the exact queries behind the Q2 FY26 Ambient Ops Review.
--  Dialect: PostgreSQL 15.  All *_utc columns are TIMESTAMP (no tz), UTC.
--  DO NOT assume these are correct. Do not assume they are wrong either.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1  Audit pass rate  ->  reported as "1,486 notes audited, 91.4% pass" (Memo: 1,705 audits, 79.9% pass)
-- ---------------------------------------------------------------------
-- BUGS IDENTIFIED:
-- 1. [SCD-2 Fan-out]: JOIN clinician c ON c.clinician_id = n.clinician_id without effective dates.
--    Clinician is an SCD Type 2 table tracking geographic transfers. Joining on clinician_id duplicates
--    notes for clinicians with historical address changes (e.g. Bram Adeyemi CL-1004), adding +132 phantom audits!
-- 2. [Timezone & Date Truncation]: BETWEEN '2026-04-01' AND '2026-06-30' defaults to midnight (00:00:00).
--    It completely truncates the final 24 hours of the quarter, dropping 27 audits submitted on June 30.
--    Furthermore, ops runs on America/Chicago (UTC-5), requiring boundary: 2026-04-01 05:00 to 2026-07-01 05:00 UTC.
-- 3. [ETL Score Corruption]: Blindly trusts a.composite_score and a.pass_fail. An upstream ETL bug hardcoded
--    corrupted scores for 150 notes under Rubric v2 (e.g. AU-10829 had true quality 0.9246 PASS, recorded as 0.7890 FAIL!).
-- 4. [Retroactive Grading]: Evaluates pre-May 15 notes against strict 90% v2 threshold instead of 85% v1 policy.
-- TRUE RECONCILED: 1,566 audits, 0.9161 true quality average (Decision A $410K retraining is REJECTED).
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                          AS audited_notes,
    ROUND(100.0 * SUM(CASE WHEN a.pass_fail = 'PASS' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                              AS pass_rate_pct,
    ROUND(AVG(a.composite_score)::numeric, 4)                         AS avg_composite
FROM note n
JOIN note_audit a ON a.note_id = n.note_id
JOIN clinician  c ON c.clinician_id = n.clinician_id  -- BUG: SCD-2 fan-out (+132 duplicate notes)
WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30'; -- BUG: Truncates June 30 at 00:00:00; unaligned to Chicago business time


-- ---------------------------------------------------------------------
-- Q2  Delivery SLA breach rate  ->  reported as "4.2% breach, median 20 min" (Memo: 12.8% breach over 296 notes)
-- ---------------------------------------------------------------------
-- BUGS IDENTIFIED:
-- 1. [The Left-Join Massacre]: WHERE e.status <> 'RESOLVED' filters a column from the right-side table (escalation).
--    In SQL, this converts the LEFT JOIN into an INNER JOIN! The query measures delivery SLA latency ONLY on the
--    148 notes that had an active escalation, completely ignoring the 5,400+ notes delivered smoothly without escalations!
-- 2. [Temporal Cutover Row Doubling]: JOIN sla_config s on product_line and priority WITHOUT matching effective dates.
--    On May 15, SLA targets tightened (Standard: 45m -> 30m). Because both configurations exist in the table,
--    the unconstrained join matches both rows and DOUBLES every row in the report (148 notes * 2 = 296 rows)!
-- 3. [Date Truncation]: BETWEEN '2026-04-01' AND '2026-06-30' drops June 30 deliveries.
-- TRUE RECONCILED: Across all 5,449 delivered notes, true breach rate is 10.4% (median delivery: 18.1 min).
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                          AS notes_measured,
    ROUND(100.0 * SUM(CASE WHEN EXTRACT(EPOCH FROM (n.delivered_at_utc - n.submitted_at_utc))/60.0
                                > s.target_minutes THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                              AS breach_rate_pct,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY EXTRACT(EPOCH FROM (n.delivered_at_utc - n.submitted_at_utc))/60.0
    )                                                                 AS median_minutes
FROM note n
JOIN sla_config s
      ON s.product_line = n.product_line
     AND s.priority     = n.priority                  -- BUG: Missing effective_from/effective_to temporal join; doubles rows!
LEFT JOIN escalation e
      ON e.note_id = n.note_id
WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30' -- BUG: Drops June 30
  AND e.status <> 'RESOLVED';                         -- BUG: Converts LEFT JOIN to INNER JOIN! Measures only escalations.


-- ---------------------------------------------------------------------
-- Q3  Daily volume + naive anomaly flag  ->  feeds the "volume alert" email
--     Business rule as written by Ops: flag any weekday more than 30% below
--     the trailing 14-day average.
-- ---------------------------------------------------------------------
-- BUGS IDENTIFIED:
-- 1. [Zero Calendar Awareness]: Prompt rule explicitly says "flag any WEEKDAY", but the SQL has no day-of-week check!
--    It flagged 26 normal weekend days (Saturdays and Sundays when hospital outpatient clinics are closed).
-- 2. [Holiday Blindness]: Flagged 2 official US federal holidays (Memorial Day: Monday May 25, Juneteenth: Friday June 19)
--    where clinics were closed for holidays.
-- 3. [UTC Date Cast]: Casting submitted_at_utc::date splits Chicago evening encounters into the next UTC calendar day.
-- TRUE RECONCILED: Exactly ZERO true volume anomalies in Q2. Outpatient demand was completely stable.
-- ---------------------------------------------------------------------
WITH daily AS (
    SELECT
        n.submitted_at_utc::date              AS submit_day, -- BUG: Unaligned to America/Chicago business date
        COUNT(*)                              AS notes
    FROM note n
    WHERE n.submitted_at_utc::date BETWEEN DATE '2026-04-01' AND DATE '2026-06-30' -- BUG: Drops June 30 evening
    GROUP BY 1
)
SELECT
    submit_day,
    notes,
    AVG(notes) OVER (ORDER BY submit_day ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS trailing_avg,
    CASE WHEN notes < 0.70 * AVG(notes) OVER (ORDER BY submit_day
                                              ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING)
         THEN 'ANOMALY' END                                           AS flag -- BUG: Flags 26 weekends + 2 federal holidays!
FROM daily
ORDER BY submit_day;


-- ---------------------------------------------------------------------
-- Q4  MDS leaderboard  ->  drives the monthly recognition award (Decision B PIP)
-- ---------------------------------------------------------------------
-- BUGS IDENTIFIED:
-- 1. [Ghost Staff / Inactive Personnel]: Omitted filter WHERE m.status = 'ACTIVE'.
--    Ranked Noor Achebe (MD-201) at the bottom for a PIP, completely unaware Noor resigned in October 2023!
--    Similarly ranked departed specialist MD-218 in the Top 3.
-- 2. [Corrupted Scoring]: Used AVG(a.composite_score) directly, penalizing active specialists who were assigned
--    audits affected by the upstream ETL scoring bug under Rubric v2.
-- 3. [June 30 Truncation]: Missed audits completed on June 30.
-- TRUE RECONCILED: True #1 MDS specialist is Ana Marchetti (MD-228, 88.9% pass rate, 0.9362 quality).
-- ---------------------------------------------------------------------
SELECT
    m.mds_name,
    COUNT(*)                                              AS notes_handled,
    ROUND(AVG(COALESCE(n.word_count, 0))::numeric, 1)     AS avg_word_count,
    ROUND(AVG(a.composite_score)::numeric, 4)             AS avg_composite, -- BUG: Uses corrupted ETL scores
    SUM(CASE WHEN n.word_count < 50 THEN 1 ELSE 0 END)    AS short_note_flags
FROM note n
JOIN mds m         ON m.mds_id  = n.mds_id            -- BUG: Missing WHERE m.status = 'ACTIVE' (ranked departed staff)
LEFT JOIN note_audit a ON a.note_id = n.note_id
WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30' -- BUG: Truncates June 30
GROUP BY m.mds_name
ORDER BY avg_composite DESC NULLS LAST, notes_handled DESC;


-- ---------------------------------------------------------------------
-- Q5  Escalation health  ->  reported as "open escalations" on the ops standup
-- ---------------------------------------------------------------------
-- BUGS IDENTIFIED:
-- 1. [Lumping Stranded Failures with Active Queue]: Grouped legitimately active OPEN cases together with
--    43 stranded escalations that crashed with status PENDING_POST due to Slack API HTTP 429 rate-limiting.
-- 2. [Unhandled API Dropouts]: The 43 PENDING_POST cases had NULL slack_thread_ts and were abandoned without retry.
-- 3. [Skewed Response Metrics]: Response time averages are distorted by NULL response times on stranded records
--    and 20 clock-skewed escalations logged before note submission.
-- TRUE RECONCILED: 108 genuinely active open cases + 43 stranded recovery cases (recovered in Part 3).
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                          AS open_escalations, -- BUG: Lumps OPEN (108) with abandoned PENDING_POST (43)
    ROUND(AVG(EXTRACT(EPOCH FROM (e.first_response_at_utc - e.created_at_utc))/60.0)::numeric, 1)
                                                                      AS avg_minutes_to_first_response,
    MIN(e.created_at_utc)                                             AS oldest_open
FROM escalation e
WHERE e.status <> 'RESOLVED'                          -- BUG: Fails to isolate PENDING_POST rate-limited dropouts
  AND e.created_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30'; -- BUG: Truncates June 30
