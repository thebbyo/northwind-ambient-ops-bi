"""
Generate the Ultimate Master Video Walkthrough & Presentation Guide PDF for Northwind Ambient Ops.
Follows the approved workflow plan with complete problem statement, forensic CSV & SQL findings,
exact code fixes with file paths, Retool app & workflow demonstration guides, and a timed teleprompter script.
"""
import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Northwind Ambient Ops — Master Video Walkthrough & Preparation Guide</title>
<style>
  @page {
    size: A4;
    margin: 15mm 13mm 15mm 13mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      color: #718096;
    }
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1a202c;
    line-height: 1.45;
    font-size: 9pt;
    margin: 0;
    padding: 0;
  }
  .header {
    border-bottom: 3px solid #2b6cb0;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  .header h1 {
    margin: 0 0 4px 0;
    color: #1a365d;
    font-size: 17pt;
    font-weight: 800;
  }
  .header .meta {
    font-size: 8pt;
    color: #4a5568;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .badge {
    display: inline-block;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 7pt;
    font-weight: 700;
    margin-right: 4px;
    text-transform: uppercase;
  }
  .badge-blue { background: #ebf8ff; color: #2b6cb0; border: 1px solid #bee3f8; }
  .badge-green { background: #f0fff4; color: #276749; border: 1px solid #c6f6d5; }
  .badge-amber { background: #fffaf0; color: #9c4221; border: 1px solid #feebc8; }
  .badge-red { background: #fff5f5; color: #9b2c2c; border: 1px solid #fed7d7; }

  h2 {
    color: #2b6cb0;
    font-size: 11.5pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }
  h3 {
    color: #2d3748;
    font-size: 10pt;
    margin-top: 10px;
    margin-bottom: 3px;
    page-break-after: avoid;
  }
  p { margin: 0 0 5px 0; }
  ul, ol { margin: 0 0 6px 0; padding-left: 16px; }
  li { margin-bottom: 2px; }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 10px 0;
    font-size: 8pt;
  }
  th, td {
    border: 1px solid #cbd5e0;
    padding: 4px 6px;
    text-align: left;
  }
  th {
    background-color: #edf2f7;
    color: #2d3748;
    font-weight: 700;
  }
  tr:nth-child(even) { background-color: #f7fafc; }

  .callout {
    background: #ebf8ff;
    border-left: 4px solid #3182ce;
    padding: 6px 10px;
    margin: 6px 0;
    border-radius: 0 4px 4px 0;
    font-size: 8.5pt;
  }
  .callout-success { background: #f0fff4; border-left-color: #38a169; }
  .callout-danger { background: #fff5f5; border-left-color: #e53e3e; }
  .callout-warning { background: #fffaf0; border-left-color: #dd6b20; }

  .code-box {
    background: #1a202c;
    color: #edf2f7;
    padding: 5px 8px;
    border-radius: 4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 7.5pt;
    line-height: 1.35;
    margin: 4px 0;
    overflow-x: auto;
  }
  .code-title {
    font-size: 7.5pt;
    font-weight: 700;
    color: #a0aec0;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .file-tag {
    font-family: ui-monospace, monospace;
    background: #edf2f7;
    padding: 1px 3px;
    border-radius: 3px;
    font-size: 7.5pt;
    color: #2b6cb0;
    font-weight: 600;
  }
  .teleprompter {
    background: #f7fafc;
    border: 1px solid #cbd5e0;
    border-left: 4px solid #4a5568;
    padding: 6px 10px;
    margin: 5px 0;
    font-style: italic;
    color: #2d3748;
    font-size: 8.5pt;
  }
  .page-break { page-break-before: always; }
</style>
</head>
<body>

<div class="header">
  <h1>Northwind Ambient Ops — Master Walkthrough & Video Script Guide</h1>
  <div class="meta">
    <span><strong>Author:</strong> Diponker Roy | Candidate for Senior BIE</span>
    <span><strong>Target Duration:</strong> ≤ 12 Minutes (Screen + Audio)</span>
    <span><span class="badge badge-green">Production Ready</span> <span class="badge badge-blue">Complete Blueprint</span></span>
  </div>
</div>

<h2>1. The Problem Statement & Real-World Business Context</h2>
<p>
  <strong>Company & Product:</strong> Northwind Ambient Ops builds ambient AI clinical documentation tools for healthcare systems. During patient encounters, ambient microphones capture physician-patient conversations, an AI model generates structured SOAP notes (Subjective, Objective, Assessment, Plan), and <strong>Medical Documentation Specialists (MDS)</strong> perform human-in-the-loop quality audits. If an urgent error occurs, alerts are posted to Slack channels (<code>#ops-note-triage-urgent</code>) before notes are delivered to the hospital Electronic Health Record (EHR).
</p>
<p>
  <strong>The Strategic Crisis:</strong> Prior to our investigation, executive leadership received a quarterly operations review memo (<code>APPENDIX_A_Q2_REVIEW.md</code>) driven by an uncalibrated SQL script (<code>PROVIDED_QUERIES.sql</code>). That memo triggered three catastrophic, high-stakes decisions:
</p>
<ol>
  <li><strong>Decision A ($410,000 Unnecessary Retraining):</strong> Management believed clinical quality was plummeting (reporting a 79.9% pass rate, missing the 80% SLA), and prepared to mandate a $410K retraining program for doctors.</li>
  <li><strong>Decision B (Wrongful Employee PIP):</strong> Management placed former employee Noor Achebe on a Performance Improvement Plan (PIP) while praising departed staff on the leaderboard.</li>
  <li><strong>43 Abandoned Emergencies (Part 3):</strong> On June 11, a traffic surge caused Slack API HTTP 429 rate limits. Northwind's legacy code crashed with zero retry logic, abandoning 43 urgent clinical escalations in <code>PENDING_POST</code>.</li>
</ol>

<div class="callout callout-success">
  <strong>Our Objective:</strong> Conduct a forensic data reconciliation to prove true metrics, overturn the $410K expenditure, build a zero-scroll keyboard-driven Retool Workbench (Part 2), deploy an idempotent Retool recovery workflow (Part 3), and prove complete software engineering rigor.
</div>

<h2>2. Walkthrough Video Agenda & Time Allocations (≤12 Minutes)</h2>
<table>
  <thead>
    <tr>
      <th>Order</th>
      <th>Required Section</th>
      <th>What to Share on Screen</th>
      <th>Target Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>1</strong></td><td><strong>Candidate Introduction</strong></td><td>Camera + Project Overview (<span class="file-tag">README.md</span>)</td><td><strong>1:00 min</strong></td></tr>
    <tr><td><strong>2</strong></td><td><strong>Reconciliation Waterfall & Top Findings</strong></td><td><span class="file-tag">RECONCILIATION.md</span> + Comparison Tables</td><td><strong>3:30 mins</strong></td></tr>
    <tr><td><strong>3</strong></td><td><strong>Retool Operator Loop (Keyboard-Only)</strong></td><td>Retool App: <code>Ambient Ops Triage Workbench</code></td><td><strong>2:30 mins</strong></td></tr>
    <tr><td><strong>4</strong></td><td><strong>Upstream-Error State (Live Trigger)</strong></td><td>Retool App: Search Corrupted Note <code>NT-002899</code></td><td><strong>1:30 mins</strong></td></tr>
    <tr><td><strong>5</strong></td><td><strong>Recovery Workflow Run Twice (Idempotency)</strong></td><td>Retool Workflows: <code>Stranded Escalation Recovery</code></td><td><strong>2:30 mins</strong></td></tr>
    <tr><td><strong>6</strong></td><td><strong>One Thing to Redo & Engineering Rigor</strong></td><td>Terminal (<code>npm test</code>) + GitHub ADRs</td><td><strong>1:00 min</strong></td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>3. Forensic Findings from the Provided SQL and CSVs</h2>
<p>
  A rigorous audit of the replica database and <span class="file-tag">PROVIDED_QUERIES.sql</span> revealed that every reported metric was distorted by SQL syntax bugs, timezone blunders, and data pipeline glitches:
</p>

<h3>Finding 1: The "Lost June 30" Bug (Chicago Timezone Boundary Failure)</h3>
<ul>
  <li><strong>The SQL Mistake:</strong> In Query 1, the analyst wrote: <code>WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30'</code>. In PostgreSQL, <code>TIMESTAMP '2026-06-30'</code> defaults to midnight (<code>00:00:00</code>). It completely dropped the entire 24 hours of June 30!</li>
  <li><strong>The Data Proof:</strong> In <span class="file-tag">data/clinician.csv</span>, 100% of clinicians (all 64 of 64) operate in <strong>`America/Chicago`</strong> time (UTC-5). A note submitted on June 30 at 11:59 PM in Chicago is July 1 at 04:59:59 UTC. The naive query dropped <strong>27 audited notes</strong> submitted on June 30!</li>
  <li><strong>File & Fix:</strong> <span class="file-tag">src/logic.js:7-30</span> & SQL boundary: <code>submitted_at_utc &gt;= '2026-04-01 05:00:00' AND &lt; '2026-07-01 05:00:00'</code>.</li>
</ul>

<h3>Finding 2: The Ghost Duplicates (+132 Phantom Notes)</h3>
<ul>
  <li><strong>The SQL Mistake:</strong> Query 1 joined <code>JOIN clinician c ON c.clinician_id = n.clinician_id</code>.</li>
  <li><strong>The Data Proof:</strong> In <span class="file-tag">data/clinician.csv</span>, table <code>clinician</code> is a <strong>Slowly Changing Dimension Type 2 (SCD-2)</strong> tracking doctor clinic transfers. Clinicians like Dr. Bram Adeyemi (<code>CL-1004</code>) and Dr. Priya Espinoza (<code>CL-1018</code>) have 2 historical rows. The unconstrained join duplicated notes up to 3 times, injecting <strong>132 phantom notes</strong> into audit reports!</li>
  <li><strong>In Note Ingestion:</strong> In <span class="file-tag">data/note.csv</span>, 62 notes were re-ingested with multiple upload IDs due to network retries.</li>
  <li><strong>File & Fix:</strong> <span class="file-tag">src/logic.js:35-44</span> (Hash-map deduplication) and SQL: <code>DISTINCT ON (clinician_id) ... ORDER BY record_effective_from DESC</code> (<span class="file-tag">docs/adr/ADR-001</span>).</li>
</ul>

<h3>Finding 3: The SLA Policy Bug (Row Doubling & Left-Join Massacre)</h3>
<ul>
  <li><strong>The SQL Mistake in Query 2:</strong> The analyst reported a 12.8% SLA delivery breach rate over 296 notes.</li>
  <li><strong>The Two Fatal Bugs:</strong>
    <ol>
      <li><strong>Omitted Date Join on <code>sla_config</code>:</strong> On May 15, Northwind tightened standard SLA targets from 45m to 30m. The query joined on product line and priority without matching effective dates, matching both rules simultaneously and <strong>doubling every row from 148 to 296 notes</strong>!</li>
      <li><strong>The Left-Join Massacre:</strong> The query wrote <code>LEFT JOIN escalation e ... WHERE e.status &lt;&gt; 'RESOLVED'</code>. Filtering a right-side table in `WHERE` turned the `LEFT JOIN` into an <strong>`INNER JOIN`</strong>, measuring delivery breaches <em>only on notes with active escalations</em>, ignoring 5,400+ smoothly delivered notes!</li>
    </ol>
  </li>
  <li><strong>File & Fix:</strong> <span class="file-tag">src/logic.js:49-58</span> (<code>getEffectiveSlaTarget</code>). Across all 5,449 delivered notes, true Q2 breach rate was <strong>10.4% (567 notes; median 18.1 min)</strong>.</li>
</ul>

<h3>Finding 4: The Corrupted $410,000 Scoring Glitch (Decision A Overturned)</h3>
<ul>
  <li><strong>The Data Proof in <span class="file-tag">data/note_audit.csv</span>:</strong> An upstream ETL bug hardcoded fake failing numbers into <code>composite_score</code> for <strong>150 notes</strong> audited under Rubric v2 right after May 15.</li>
  <li><strong>Mathematical Smoking Gun:</strong> Audit <code>AU-10829</code> scored: Accuracy: 0.8906 (x0.35), Completeness: 0.9738 (x0.25), Formatting: 0.9196 (x0.05), Terminology: 0.9476 (x0.10), HPI: 0.8870 (x0.10), ROS: 0.9378 (x0.05), Plan: 0.9311 (x0.10).
  <br>$$\text{True Score} = \mathbf{0.9246} \text{ (CLEAR PASS!)}$$
  Yet the database recorded: <strong>`0.7890` (FAIL)</strong>!</li>
  <li><strong>Verdict:</strong> True Q2 quality was <strong>0.9161 (91.6%)</strong>, beating the 90% target. <strong>Decision A ($410K retraining) is 100% REJECTED!</strong></li>
</ul>

<h3>Finding 5: The Flawed Volume Anomaly Alert ("28 of 91 Days" Debunked)</h3>
<ul>
  <li><strong>The SQL Mistake in Query 3:</strong> Flagged any day where volume dropped >30% below trailing 14-day average.</li>
  <li><strong>The Data Proof:</strong> The query had <strong>zero calendar awareness</strong>. It flagged <strong>26 weekend days</strong> (Saturdays & Sundays when clinics are closed!) + <strong>2 federal holidays</strong> (Memorial Day on May 25, Juneteenth on June 19).</li>
  <li><strong>True Metric:</strong> <strong>Exactly ZERO true volume anomalies. Outpatient demand was completely stable.</strong></li>
</ul>

<h3>Finding 6: Inactive Staff on PIP & Leaderboard Distortion (Decision B Overturned)</h3>
<ul>
  <li><strong>The SQL Mistake in Query 4:</strong> Omitted <code>WHERE status = 'ACTIVE'</code>. Placed Noor Achebe (<code>MD-201</code>) on a PIP even though Noor resigned in October 2023! Ranked departed <code>MD-218</code> in the Top 3.</li>
  <li><strong>True Metric:</strong> True #1 MDS specialist is <strong>Ana Marchetti (<code>MD-228</code>, 88.9% pass rate, 0.9362 quality)</strong>.</li>
</ul>

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Reported in Legacy Memo</th>
      <th>True Reconciled Metric</th>
      <th>Root Cause of Variance</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>Notes Audited</strong></td><td>1,705</td><td><strong>1,566</strong></td><td>-27 dropped on June 30; +132 SCD-2 clinician duplicates</td></tr>
    <tr><td><strong>Audit Pass Rate</strong></td><td>79.9%</td><td><strong>80.1% (Policy v1) / 77.0% (v2)</strong></td><td>150 corrupted ETL scores; retroactive v2 grading on April notes</td></tr>
    <tr><td><strong>Composite Quality</strong></td><td>0.9055</td><td><strong>0.9161 (91.6%)</strong></td><td>Doctors exceeded targets; Decision A $410K retraining rejected</td></tr>
    <tr><td><strong>SLA Breach Rate</strong></td><td>12.8% (296 notes)</td><td><strong>10.4% (567 of 5,449 notes)</strong></td><td>Left-join converted to inner-join; doubled sla_config rows</td></tr>
    <tr><td><strong>Median Delivery Time</strong></td><td>18.5 min</td><td><strong>18.1 min</strong></td><td>Healthy turnaround times across ambient pipeline</td></tr>
    <tr><td><strong>Open Escalations</strong></td><td>149</td><td><strong>108 Active + 43 Stranded</strong></td><td>43 Slack API HTTP 429 dropouts abandoned without retry</td></tr>
    <tr><td><strong>Volume Anomalies</strong></td><td>28 of 91 days</td><td><strong>0 true anomalies</strong></td><td>Zero calendar awareness: flagged 26 weekends + 2 holidays</td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>4. What We Actually Fixed (With File Paths & Code Blocks)</h2>

<h3>1. Chicago Timezone Boundary Alignment</h3>
<p><strong>File Path:</strong> <span class="file-tag">src/logic.js:7-30</span> & <span class="file-tag">docs/RETOOL_APP_SETUP.md</span></p>
<div class="code-box">
  <div class="code-title">PostgreSQL SQL Query</div>
  (n.submitted_at_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago') AS submitted_at_cst,<br>
  WHERE n.submitted_at_utc >= TIMESTAMP '2026-04-01 05:00:00'<br>
  &nbsp;&nbsp;AND n.submitted_at_utc &lt; TIMESTAMP '2026-07-01 05:00:00'
</div>

<h3>2. SCD-2 Clinician Deduplication Engine</h3>
<p><strong>File Path:</strong> <span class="file-tag">docs/adr/ADR-001-scd2-clinician-deduplication.md</span> & <span class="file-tag">src/logic.js:35-44</span></p>
<div class="code-box">
  <div class="code-title">PostgreSQL DISTINCT ON Join</div>
  JOIN (<br>
  &nbsp;&nbsp;SELECT DISTINCT ON (clinician_id) clinician_id, clinician_name, specialty, region<br>
  &nbsp;&nbsp;FROM clinician<br>
  &nbsp;&nbsp;ORDER BY clinician_id, record_effective_from DESC<br>
  ) c ON c.clinician_id = n.clinician_id
</div>

<h3>3. Effective-Dated SLA Target Lookup</h3>
<p><strong>File Path:</strong> <span class="file-tag">src/logic.js:49-58</span> (<code>getEffectiveSlaTarget</code>)</p>
<div class="code-box">
  <div class="code-title">Temporal SQL Join</div>
  JOIN sla_config s<br>
  &nbsp;&nbsp;ON s.product_line = n.product_line AND s.priority = n.priority<br>
  &nbsp;&nbsp;AND n.submitted_at_utc::date &gt;= s.effective_from<br>
  &nbsp;&nbsp;AND (s.effective_to IS NULL OR n.submitted_at_utc::date &lt;= s.effective_to)
</div>

<h3>4. True Rubric Weighted Score Calculation</h3>
<p><strong>File Path:</strong> <span class="file-tag">src/logic.js:63-78</span> & <span class="file-tag">docs/RETOOL_APP_SETUP.md</span></p>
<div class="code-box">
  <div class="code-title">Dynamic Rubric Scoring (Rubric v1 vs. v2)</div>
  CASE <br>
  &nbsp;&nbsp;WHEN a.rubric_version = 'v1' THEN<br>
  &nbsp;&nbsp;&nbsp;&nbsp;ROUND((a.score_accuracy * 0.30 + a.score_completeness * 0.20 + a.score_formatting * 0.10 + ...)::numeric, 4)<br>
  &nbsp;&nbsp;WHEN a.rubric_version = 'v2' THEN<br>
  &nbsp;&nbsp;&nbsp;&nbsp;ROUND((a.score_accuracy * 0.35 + a.score_completeness * 0.25 + a.score_formatting * 0.05 + ...)::numeric, 4)<br>
  &nbsp;&nbsp;ELSE a.composite_score<br>
  END AS true_composite_score
</div>

<h3>5. Automated Unit Tests (CI/CD Rigor)</h3>
<p><strong>File Path:</strong> <span class="file-tag">test/logic.test.js</span> — Run with <code>npm test</code></p>
<div class="code-box">
  <div class="code-title">Terminal Output: npm test</div>
  ✔ Timezone boundary: UTC vs America/Chicago business date (56.1ms)<br>
  ✔ Deduplication: Note re-ingestions resolve to latest ingested_at_utc (0.08ms)<br>
  ✔ Effective-dated SLA lookup: Pre-May 15 vs Post-May 15 targets (0.06ms)<br>
  ✔ Composite score recalculation: Detects discrepancy against rubric weights (0.08ms)<br>
  ✔ Idempotency Key: Deterministic and unique across attempts (5.4ms)<br>
  ℹ tests 5 | pass 5 | fail 0 | duration_ms 127.5ms
</div>

<div class="page-break"></div>

<h2>5. Retool Triage Workbench Demonstration Guide (Part 2)</h2>
<p>
  Built as a standard Classic Retool Application (zero black-box AI generators) optimized for <strong>1366×768 single-screen operations</strong> without vertical scrolling.
</p>

<h3>UI Architecture (55% / 45% Master-Detail Split)</h3>
<ul>
  <li><strong>Left Pane (55%):</strong> Master Queue Table populated by <code>get_triage_queue</code>. Displays <code>note_id</code>, Chicago timestamp, doctor name, specialty, priority, true score, and escalation status.</li>
  <li><strong>Right Pane (45%):</strong> Reviewer & Provenance Container displaying doctor details, 7-dimension rubric scorecard, disposition controls, and the dynamic alert badge.</li>
  <li><strong>Documentation:</strong> <span class="file-tag">docs/RETOOL_APP_SETUP.md</span>, <span class="file-tag">UX_RATIONALE.md</span></li>
</ul>

<h3>The Keyboard Operator Loop (Requirement 3: Interaction Count ≤ 4)</h3>
<ol>
  <li><strong>Interaction 1 (Navigation):</strong> Press <strong>Down Arrow (↓)</strong> on the keyboard. The selected row updates instantly and populates the right pane.</li>
  <li><strong>Interaction 2 (Disposition):</strong> Click <code>APPROVE</code>, <code>REVISE</code>, or <code>ESCALATE</code> (or press hotkeys).</li>
  <li><strong>Interaction 3 (Commit):</strong> Click <strong>Commit Decision (C)</strong>. Instant green notification toast fires: <em>"Triage Decision Recorded: Note NT-005938 marked as APPROVE"</em>.</li>
</ol>
<p><strong>Total Interaction Count: Exactly 2 to 3 actions per note (Well below the requirement limit of 4!).</strong></p>

<h3>Upstream-Error State (Requirement 5: Triggered Live)</h3>
<p>In the video, search for corrupted note <strong>`NT-002899`</strong> (or `NT-005938`):</p>
<ul>
  <li><strong>The Live Demonstration:</strong> Watch the right-hand container: an orange warning card automatically pops up:
    <div class="callout callout-warning">
      <strong>⚠️ ETL Score Discrepancy Detected</strong><br>
      • Legacy Database Score: 0.7890 (FAIL)<br>
      • True Calculated Rubric Score: 0.9246 (PASS)<br>
      • Rubric: v2
    </div>
  </li>
  <li><strong>The Underlying Logic:</strong> Our query calculates <code>is_score_corrupted = ABS(legacy - true) &gt; 0.001</code>. If true, the alert unhides. On clean notes, the alert is completely hidden. This protects operators from falsely penalizing doctors.</li>
</ul>

<h2>6. Retool Recovery Workflow Demonstration Guide (Part 3)</h2>
<p>
  <strong>The Production Incident:</strong> On June 11, Northwind hit a surge of urgent escalations. The legacy backend bombarded Slack without rate limits. Slack returned <code>HTTP 429 (Too Many Requests)</code>. The code crashed, marked 43 escalations as <code>PENDING_POST</code>, and abandoned them without retrying.
</p>

<h3>The Five-Block Recovery Pipeline Architecture</h3>
<ol>
  <li><strong><code>startTrigger</code>:</strong> Webhook, manual, or scheduled cron trigger.</li>
  <li><strong><code>fetch_stranded_escalations</code>:</strong> SQL query filtering: <code>WHERE status = 'PENDING_POST' AND slack_thread_ts IS NULL</code> (returns the 43 records).</li>
  <li><strong><code>process_each_escalation</code> (Sequential Loop):</strong>
    <ul>
      <li><strong>Requirement W4 (Rate-Limiting):</strong> Enforces a strict <strong>1000ms delay</strong> between iterations to comply with Slack Tier 2 rate limits (≤1 req/sec).</li>
      <li><strong>Requirement W3 (Idempotency Key):</strong> Generates deterministic SHA-256 hash: <code>idem_{escalation_id}_att{attempt_number}_{timestamp}</code>.</li>
    </ul>
  </li>
  <li><strong><code>update_recovered_escalations</code>:</strong> Updates database setting <code>status = 'RESOLVED'</code>, <code>slack_thread_ts = 1774540029.893550</code>, and <code>resolved_at_utc = NOW()</code>.</li>
  <li><strong><code>verify_zero_stranded</code> (Requirement W8):</strong> Audit query verifying: <code>stranded_count = 0</code>.</li>
</ol>

<div class="callout callout-success">
  <strong>How to Show Idempotency Live (Back-to-Back Run):</strong><br>
  Open the workflow run history on screen showing all 4 green checkmarks and 1000ms pacing. Then click <strong>Run a second time live</strong>! The query finds 0 records, the loop executes 0 times, and 0 duplicate messages are sent.
</div>

<div class="page-break"></div>

<h2>7. Word-for-Word Video Teleprompter Script (≤12 Minutes)</h2>

<div class="teleprompter">
  <strong>0:00 – 1:00 | Section 1: Candidate Introduction</strong><br>
  "Hello everyone, my name is Diponker Roy, and today I'm presenting my operational data reconciliation, Retool Triage Workbench, and automated recovery workflow for Northwind Ambient Ops. Our objective was to resolve deep data integrity failures in the Q2 FY26 operations review, protect the hospital system from an unjustified $410,000 retraining expenditure, and engineer robust operational tooling in Retool backed by enterprise software engineering practices. Let’s dive straight into the reconciliation findings."
</div>

<div class="teleprompter">
  <strong>1:00 – 4:30 | Section 2: Reconciliation Waterfall & Top Findings</strong><br>
  "Opening RECONCILIATION.md, our forensic audit of PROVIDED_QUERIES.sql revealed that every single metric in the executive memo was mathematically flawed.<br><br>
  Finding #1 is the 'Lost June 30' bug. The legacy query filtered with a naive BETWEEN April 1 and June 30 clause. In SQL, June 30 defaults to midnight 00:00:00, which chopped off the final 24 hours of the quarter. Furthermore, Northwind's operational headquarters and all 64 clinicians operate on America/Chicago business time, which is UTC minus 5. By aligning our boundaries from April 1 05:00 UTC to July 1 05:00 UTC, we recovered all 27 dropped audits.<br><br>
  Finding #2 is the Ghost Duplicates issue. We found two distinct fan-out sources: note re-ingestions from network retries, and doctor transfers in the SCD-2 clinician table. Doctors like Dr. Bram Adeyemi have multiple historical rows. The legacy unconstrained join duplicated notes up to three times, inflating audited note counts by 132 phantom records. We resolved this using an O(N) hash map in src/logic.js and PostgreSQL DISTINCT ON clinician_id in our SQL.<br><br>
  Finding #3 is the SLA Policy bug. The legacy analyst reported a 12.8% SLA delivery breach rate. However, on May 15, Northwind revised SLA delivery targets from 45 minutes to 30 minutes. The legacy query joined sla_config without matching effective dates, which doubled the rows in their report and retroactively penalized April notes! Worse, their WHERE clause converted a LEFT JOIN into an INNER JOIN, only evaluating notes with open escalations. The true Q2 SLA breach rate across all 5,449 notes was actually 10.4%.<br><br>
  Finding #4 is the $410,000 scoring glitch. Management reported a 79.9% pass rate, falling below the 80% SLA, and was about to spend $410,000 on clinician retraining. We discovered that an upstream ETL bug hardcoded fake failing scores for 150 notes audited under Rubric v2. In audit AU-10829, for example, the doctor achieved a 92.5% quality score, yet the database recorded 0.7890 FAIL. When we dynamically recalculate the weighted sum across all seven rubric dimensions, the true Q2 quality average is 0.9161, well above target. Decision A is officially rejected—saving $410,000.<br><br>
  Finally, for Decision B, the MDS leaderboard placed Noor Achebe on a PIP, completely unaware that Noor had resigned months earlier with inactive status."
</div>

<div class="teleprompter">
  <strong>4:30 – 7:00 | Section 3: Retool Operator Loop & Upstream Error State</strong><br>
  "Now switching to our Retool Ambient Ops Triage Workbench. Designed for 1366 by 768 displays with zero vertical scrolling, we have a 55% master queue on the left and a 45% reviewer pane on the right.<br><br>
  Notice our keyboard operator loop. As a triage specialist, I don't touch my mouse. Interaction #1: I press the Down Arrow on my keyboard to select note NT-005938. The reviewer pane instantly populates with the doctor’s details, Chicago timestamp, and the seven clinical rubric dimensions.<br><br>
  Now, let's trigger our upstream-error state live. I search for note NT-002899. Watch the right-hand container: an orange alert dynamically appears: '⚠️ ETL Score Discrepancy Detected'. It shows the legacy database score was 0.7890 FAIL, but the true rubric score is 0.9246 PASS. Clean notes hide this card automatically.<br><br>
  Interaction #2: Because the doctor passed, I select APPROVE. Interaction #3: I hit Commit Decision. A green success notification confirms the update. That is a complete triage decision in three keystrokes—well below our four-interaction limit."
</div>

<div class="teleprompter">
  <strong>7:00 – 9:30 | Section 4: Retool Recovery Workflow & Idempotency Proof</strong><br>
  "Next, let’s look at Retool Workflows: Stranded Escalation Recovery. On June 11, a traffic surge caused Slack API HTTP 429 rate-limiting, stranding 43 escalations in PENDING_POST with zero retry handling.<br><br>
  Our workflow uses fetch_stranded_escalations to dynamically detect these 43 records. It pipes them into a sequential loop with an enforced 1,000 millisecond delay, satisfying Requirement W4 for Slack rate-limiting. Inside the loop, we generate a deterministic SHA-256 idempotency key per attempt.<br><br>
  After processing, update_recovered_escalations marks them RESOLVED, and verify_zero_stranded checks the count. Look at our run history: 43 records processed with 1000ms pacing and zero errors.<br><br>
  Now, to prove Requirement W8—Idempotency: Watch what happens when I click Run a second time back-to-back. The query checks the database, finds zero stranded records, the loop executes zero times, and zero duplicate messages are sent. It is 100% idempotent."
</div>

<div class="teleprompter">
  <strong>9:30 – 11:30 | Section 5: Engineering Rigor & What I Would Redo</strong><br>
  "Finally, our engineering rigor. In our repository, we have documented three Architecture Decision Records in docs/adr/ covering SCD-2 deduplication, rate-limiting backoff, and row-level locking. Running npm test in our terminal executes our Node test suite, passing all five test suites in 127 milliseconds, and is automated in GitHub Actions CI.<br><br>
  If given another week with this codebase, the one thing I would redo is replace polling-based database replica queries with an event-driven architecture using Apache Kafka or Temporal. Rather than polling for stranded records, an asynchronous queue with built-in dead-letter topics and automated exponential backoff would provide sub-second resilience before alerts ever get stranded.<br><br>
  Thank you for your time, and I look forward to our live technical review!"
</div>

</body>
</html>
"""

html_path = "/Users/dibbyoroy/Desktop/homeAssesment/master_walkthrough_guide.html"
pdf_path = "/Users/dibbyoroy/Desktop/homeAssesment/Northwind_Master_Video_Walkthrough_Guide.pdf"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML written to {html_path}")

# Run Chrome headless to generate PDF
chrome_cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

res = subprocess.run(chrome_cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"SUCCESS: Master Guide PDF generated at {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
else:
    print("Chrome stderr:", res.stderr)
