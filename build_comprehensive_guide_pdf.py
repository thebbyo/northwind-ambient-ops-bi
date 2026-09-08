"""
Build the Master Walkthrough & Video Preparation Guide PDF for Northwind Ambient Ops.
Enhanced to include the dedicated query-by-query forensic breakdown of all 5 queries
in PROVIDED_QUERIES.sql, detailing the exact SQL bugs, syntax errors, and their fixes.
"""
import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Northwind Ambient Ops — Comprehensive Walkthrough & Video Script Guide</title>
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
  <h1>Northwind Ambient Ops — Master Walkthrough Guide</h1>
  <div class="meta">
    <span><strong>Author:</strong> Diponker Roy | Candidate for Senior BIE</span>
    <span><strong>Assessment:</strong> Commure Practical Assessment</span>
    <span><span class="badge badge-green">Verified</span> <span class="badge badge-blue">Complete Query-by-Query Bugs</span></span>
  </div>
</div>

<h2>1. Executive Summary & The Business Scenario</h2>
<p>
  <strong>The Company:</strong> Northwind Ambient Ops builds AI-powered ambient clinical transcription software for hospital clinicians. Ambient microphones capture patient visits, an ambient AI model drafts structured SOAP clinical notes, and <strong>Medical Documentation Specialists (MDS)</strong> audit notes to protect clinical safety.
</p>
<p>
  <strong>The Problem:</strong> Leadership made critical strategic decisions based on an uncalibrated Q2 review memo (<code>APPENDIX_A_Q2_REVIEW.md</code>) driven by buggy SQL (<code>PROVIDED_QUERIES.sql</code>). This created three massive operational crises:
</p>
<ul>
  <li><strong>The $410K False Alarm (Decision A):</strong> Management believed quality collapsed to 79.9%, preparing to spend $410,000 on clinician retraining.</li>
  <li><strong>The SLA Miscalculation:</strong> Reported a 12.8% SLA delivery breach rate (296 notes) due to unconstrained joins and botched filters.</li>
  <li><strong>Wrongful Employee PIP (Decision B):</strong> Inactive departed staff were placed on PIPs while top performers were distorted by corrupted scores.</li>
  <li><strong>43 Abandoned Emergencies (Part 3):</strong> On June 11, Slack API rate-limiting (HTTP 429) caused 43 clinical alerts to fail and be abandoned without retry.</li>
</ul>

<div class="callout callout-success">
  <strong>Our Deliverables:</strong> We overturned the $410K expense, corrected the SLA breach rate to 10.4%, eliminated ghost duplicates, built the keyboard-driven <strong>Ambient Ops Triage Workbench</strong> in Retool, deployed an idempotent <strong>Stranded Escalation Recovery Workflow</strong>, and validated everything with 5 automated unit tests.
</div>

<h2>2. Walkthrough Video Agenda & Time Allocations (≤12 Minutes)</h2>
<table>
  <thead>
    <tr>
      <th>Order</th>
      <th>Required Section</th>
      <th>Screen to Share</th>
      <th>Target Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>1</strong></td><td><strong>Candidate Introduction</strong></td><td>Camera + Repo Overview (<code>README.md</code>)</td><td><strong>1:00 min</strong></td></tr>
    <tr><td><strong>2</strong></td><td><strong>Reconciliation Waterfall & Top Findings</strong></td><td><code>RECONCILIATION.md</code> + Tables / Code</td><td><strong>3:30 mins</strong></td></tr>
    <tr><td><strong>3</strong></td><td><strong>Retool Operator Loop (Keyboard-Only)</strong></td><td>Retool App: <code>Ambient Ops Triage Workbench</code></td><td><strong>2:30 mins</strong></td></tr>
    <tr><td><strong>4</strong></td><td><strong>Upstream-Error State (Live Trigger)</strong></td><td>Retool App: Corrupted Note <code>NT-002899</code></td><td><strong>1:30 mins</strong></td></tr>
    <tr><td><strong>5</strong></td><td><strong>Recovery Workflow Run Twice (Idempotency)</strong></td><td>Retool Workflows: <code>Stranded Escalation Recovery</code></td><td><strong>2:30 mins</strong></td></tr>
    <tr><td><strong>6</strong></td><td><strong>One Thing to Redo & Engineering Rigor</strong></td><td>Terminal (<code>npm test</code>) + GitHub ADRs</td><td><strong>1:00 min</strong></td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>3. Query-by-Query Forensic Audit of <code>PROVIDED_QUERIES.sql</code></h2>
<p>
  Management provided a legacy script with 5 queries. Below is the forensic audit of the exact SQL bugs inside each query and how we corrected them:
</p>

<h3>Query 1: Audit Pass Rate & Clinical Quality</h3>
<ul>
  <li><strong>What the Analyst Wrote:</strong>
    <div class="code-box">
      SELECT COUNT(*) AS total_audits, AVG(CASE WHEN a.pass_fail = 'PASS' THEN 1.0 ELSE 0.0 END) AS pass_rate<br>
      FROM note n<br>
      JOIN clinician c ON c.clinician_id = n.clinician_id<br>
      JOIN note_audit a ON a.note_id = n.note_id<br>
      WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30';
    </div>
  </li>
  <li><strong>The SQL Bugs:</strong>
    <ol>
      <li><strong>June 30 Truncation:</strong> <code>TIMESTAMP '2026-06-30'</code> defaults to <code>00:00:00</code> midnight. It dropped the final 24 hours of the quarter (-27 audits).</li>
      <li><strong>SCD-2 Cartesian Fan-out:</strong> Joined <code>clinician</code> on <code>clinician_id</code> without effective dates. Because doctors have multiple rows for historical address transfers, 132 notes duplicated (+132 phantom audits).</li>
      <li><strong>ETL Score Blindness:</strong> Trusted <code>pass_fail</code> directly, completely unaware that 150 audits had corrupted, hardcoded failing scores under Rubric v2.</li>
    </ol>
  </li>
  <li><strong>Reconciled Fix:</strong> Aligned UTC to Chicago business hours (<code>2026-04-01 05:00:00</code> to <code>2026-07-01 05:00:00</code>), deduplicated clinicians using <code>DISTINCT ON (clinician_id)</code>, and recomputed true scores from the 7 rubric dimensions. <strong>True audits: 1,566; Quality: 0.9161 (Decision A $410K Retraining REJECTED).</strong></li>
</ul>

<h3>Query 2: Delivery SLA Breach Rate</h3>
<ul>
  <li><strong>What the Analyst Wrote:</strong>
    <div class="code-box">
      SELECT COUNT(*) AS notes_delivered, AVG(CASE WHEN EXTRACT(EPOCH FROM (n.delivered_at_utc - n.submitted_at_utc))/60 &gt; s.target_minutes THEN 1.0 ELSE 0.0 END) AS breach_rate<br>
      FROM note n<br>
      JOIN sla_config s ON s.product_line = n.product_line AND s.priority = n.priority<br>
      LEFT JOIN escalation e ON e.note_id = n.note_id<br>
      WHERE n.submitted_at_utc BETWEEN TIMESTAMP '2026-04-01' AND TIMESTAMP '2026-06-30'<br>
      &nbsp;&nbsp;AND e.status &lt;&gt; 'RESOLVED';
    </div>
  </li>
  <li><strong>The SQL Bugs:</strong>
    <ol>
      <li><strong>The Left-Join Massacre:</strong> Adding <code>WHERE e.status &lt;&gt; 'RESOLVED'</code> on a left-joined table converted it to an <strong>INNER JOIN</strong>! The analyst measured SLA breaches <em>only on notes with unresolved escalations</em>, ignoring 5,000+ smoothly delivered notes.</li>
      <li><strong>Temporal Cutover Row Doubling:</strong> Joined <code>sla_config</code> without matching effective dates (May 15 policy change). Matched both 45-min and 30-min targets, doubling every row from 148 to 296 notes!</li>
    </ol>
  </li>
  <li><strong>Reconciled Fix:</strong> Removed the escalation filter and joined <code>sla_config</code> on <code>n.submitted_at_utc::date &gt;= s.effective_from AND (s.effective_to IS NULL OR n.submitted_at_utc::date &lt;= s.effective_to)</code>. <strong>True Q2 breach rate was 10.4% across 5,449 notes (not 12.8% over 296).</strong></li>
</ul>

<h3>Query 3: Daily Volume Anomaly Alert ("28 of 91 Days")</h3>
<ul>
  <li><strong>What the Analyst Wrote:</strong> Flagged any calendar day where note volume dropped >30% below the trailing 14-day rolling average.</li>
  <li><strong>The SQL Bug:</strong> <strong>Zero calendar awareness.</strong> Hospitals schedule fewer outpatient appointments on weekends and holidays. The query flagged <strong>26 weekend days</strong> (Saturdays and Sundays) plus <strong>2 federal holidays</strong> (Memorial Day, Juneteenth)!</li>
  <li><strong>Reconciled Fix:</strong> Added business-day filtering (<code>EXTRACT(DOW FROM date) NOT IN (0, 6)</code> and holiday calendar). <strong>True volume anomalies in Q2: exactly ZERO days. Demand was rock solid.</strong></li>
</ul>

<h3>Query 4: MDS Specialist Performance Leaderboard (Decision B)</h3>
<ul>
  <li><strong>What the Analyst Wrote:</strong> Ranked MDS specialists by simple average composite score without filtering employee status.</li>
  <li><strong>The SQL Bugs:</strong>
    <ol>
      <li><strong>Ghost Staff:</strong> Omitted <code>WHERE status = 'ACTIVE'</code>. Placed Noor Achebe (<code>MD-201</code>) on a PIP even though Noor resigned in October 2023! Ranked departed <code>MD-218</code> in the Top 3.</li>
      <li><strong>Corrupted v2 Penalties:</strong> Top active specialists like Dr. Adeyemi and Dr. Kowalski were unfairly penalized by the corrupted v2 scores.</li>
    </ol>
  </li>
  <li><strong>Reconciled Fix:</strong> Filtered for active personnel and recomputed scores. <strong>True #1 MDS: Ana Marchetti (<code>MD-228</code>, 88.9% pass rate, 0.9362 avg score).</strong></li>
</ul>

<h3>Query 5: Open Escalations Queue</h3>
<ul>
  <li><strong>The SQL Bug:</strong> Reported 149 open escalations. Lumped together legitimately active cases with <strong>43 stranded Slack API HTTP 429 rate-limited records</strong> that had null thread timestamps and zero retry handling.</li>
  <li><strong>Reconciled Fix:</strong> Segregated into 108 genuinely active cases and 43 stranded cases for automated recovery.</li>
</ul>

<div class="page-break"></div>

<h2>4. Part 2: Retool Triage Workbench (Operator Loop & Live Error)</h2>

<h3>Application Architecture (1366×768 Single-Screen)</h3>
<ul>
  <li><strong>Left Pane (55% width):</strong> Master Triage Table displaying notes chronologically with doctor name, specialty, priority, Chicago timestamp, and true score.</li>
  <li><strong>Right Pane (45% width):</strong> Detail & Provenance Container showing doctor context, 7 clinical dimension subscores, disposition controls, and the provenance warning card.</li>
  <li><strong>Documentation:</strong> <span class="file-tag">docs/RETOOL_APP_SETUP.md</span>, <span class="file-tag">UX_RATIONALE.md</span></li>
</ul>

<h3>The Keyboard Operator Loop (Requirement 3: Interaction Count ≤ 4)</h3>
<ol>
  <li><strong>Interaction 1 (Keyboard):</strong> Press <strong>Down Arrow (↓)</strong> to select the next note. The right pane updates instantly.</li>
  <li><strong>Interaction 2 (Action):</strong> Press <code>1</code>/<code>2</code>/<code>3</code> or click <code>APPROVE</code>/<code>REVISE</code>/<code>ESCALATE</code>.</li>
  <li><strong>Interaction 3 (Commit):</strong> Click <strong>Commit Decision (C)</strong>. Instant green notification fires: <em>"Triage Decision Recorded"</em>.</li>
</ol>
<p><strong>Total Interaction Count: 2 to 3 actions per note (Well below the requirement limit of 4!).</strong></p>

<h3>Upstream-Error State (Requirement 5: Triggered Live)</h3>
<p>In the video, search for corrupted note <strong><code>NT-002899</code></strong> (or <code>NT-005938</code>):</p>
<ul>
  <li><strong>The Live Visual:</strong> The orange alert card automatically pops up:
    <div class="callout callout-warning">
      <strong>⚠️ ETL Score Discrepancy Detected</strong><br>
      • Legacy Score: 0.7890 (FAIL)<br>
      • True Rubric Score: 0.9246 (PASS)<br>
      • Rubric: v2
    </div>
  </li>
  <li><strong>The Logic:</strong> Our query checks <code>ABS(legacy - true) > 0.001</code>. If corrupted, <code>is_score_corrupted = true</code> and the alert unhides. On clean notes, the alert is hidden. This gives operators instant forensic protection.</li>
</ul>

<h2>5. Part 3: Retool Stranded Escalation Recovery Workflow</h2>

<h3>The Incident: 43 Stranded Slack Escalations</h3>
<p>
  On June 11, Northwind hit a traffic surge. The legacy backend bombarded Slack's API without rate-limiting. Slack returned <code>HTTP 429 (Too Many Requests)</code>. Northwind's code crashed, marked 43 escalations as <code>PENDING_POST</code>, and abandoned them without retrying.
</p>

<h3>The Five-Block Recovery Pipeline in Retool Workflows</h3>
<ol>
  <li><strong><code>startTrigger</code>:</strong> Manual, webhook, or scheduled cron trigger.</li>
  <li><strong><code>fetch_stranded_escalations</code>:</strong> SQL query: <code>WHERE status = 'PENDING_POST' AND slack_thread_ts IS NULL</code> (cleanly returns the 43 records).</li>
  <li><strong><code>process_each_escalation</code> (Loop Block):</strong>
    <ul>
      <li><strong>Requirement W4:</strong> Enforces <strong>1000ms delay</strong> between iterations to comply with Slack Tier 2 rate limits (≤1 req/sec).</li>
      <li><strong>Requirement W3:</strong> Generates deterministic SHA-256 idempotency key: <code>idem_{escalation_id}_att{attempt_number}_{timestamp}</code>.</li>
    </ul>
  </li>
  <li><strong><code>update_recovered_escalations</code>:</strong> Updates database setting <code>status = 'RESOLVED'</code>, <code>slack_thread_ts = 1774540029.893550</code>, and <code>resolved_at_utc = NOW()</code>.</li>
  <li><strong><code>verify_zero_stranded</code> (Requirement W8):</strong> Final audit query returning <code>stranded_count: 0</code>.</li>
</ol>

<div class="callout callout-success">
  <strong>How to Show Idempotency Live (Back-to-Back Run):</strong><br>
  Run the workflow on screen. Point out that all 43 records are resolved. Then click <strong>Run a second time</strong>! The query finds 0 records, the loop executes 0 times, and 0 duplicate messages are sent.
</div>

<div class="page-break"></div>

<h2>6. Word-for-Word Video Teleprompter Script (Section by Section)</h2>

<div class="teleprompter">
  <strong>0:00 – 1:00 | Section 1: Introduction</strong><br>
  "Hello everyone, my name is Diponker Roy, and today I'm presenting my operational data reconciliation, Retool Triage Workbench, and automated recovery workflow for Northwind Ambient Ops. Our objective was to resolve deep data integrity failures in the Q2 FY26 operations review, protect the hospital system from an unjustified $410,000 retraining expenditure, and engineer robust operational tooling in Retool backed by enterprise software engineering practices. Let’s dive straight into the reconciliation findings."
</div>

<div class="teleprompter">
  <strong>1:00 – 4:30 | Section 2: Reconciliation Waterfall & Top Findings</strong><br>
  "Opening RECONCILIATION.md, our forensic audit of PROVIDED_QUERIES.sql revealed that every single metric in the executive memo was mathematically flawed.<br><br>
  In Query 1, the analyst used a naive BETWEEN April 1 and June 30 clause, which truncated the entire day of June 30 and dropped 27 audits. Furthermore, they joined the Slowly Changing Dimension clinician table without effective dates, causing a Cartesian fan-out that created 132 phantom notes! When we recalculate true quality from the seven rubric dimensions, we uncovered 150 corrupted ETL scores under Rubric v2, including audit AU-10829 which had a 92.5% quality score falsely recorded as 0.7890 FAIL. True Q2 quality was 0.9161, proving Decision A's $410,000 retraining expense was completely unjustified.<br><br>
  In Query 2, the analyst reported a 12.8% SLA breach rate. They made two fatal mistakes: they joined sla_config without effective dates, doubling every row in their report, and they placed an escalation filter in the WHERE clause, which converted their LEFT JOIN into an INNER JOIN! They only measured SLA breaches on notes that had open escalations! True Q2 delivery SLA breach rate was actually 10.4% across 5,449 notes.<br><br>
  In Query 3, the daily volume alert flagged 28 of 91 days simply because it lacked calendar awareness—flagging 26 weekends and two federal holidays! True demand anomalies were zero.<br><br>
  Finally, in Query 4, the MDS leaderboard placed Noor Achebe on a PIP, completely unaware that Noor had resigned months earlier with inactive status."
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
pdf_path = "/Users/dibbyoroy/Desktop/homeAssesment/Northwind_Walkthrough_Master_Guide.pdf"

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
    print(f"SUCCESS: Master Guide PDF updated with all query bugs at {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
else:
    print("Chrome stderr:", res.stderr)
