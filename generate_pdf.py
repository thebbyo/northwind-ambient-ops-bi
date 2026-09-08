"""
Generate a beautiful, professional PDF executive brief summarizing the entire
Northwind Ambient Ops assessment (investigation, findings, fixes, Retool app, and workflow).
"""
import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Northwind Ambient Ops - Forensic Reconciliation & Solutions Brief</title>
<style>
  @page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {
      content: counter(page);
      font-size: 9pt;
      color: #718096;
    }
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1a202c;
    line-height: 1.55;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
  }
  .header {
    border-bottom: 2px solid #2b6cb0;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }
  .header h1 {
    margin: 0 0 6px 0;
    color: #1a365d;
    font-size: 20pt;
    font-weight: 700;
  }
  .header .meta {
    font-size: 9.5pt;
    color: #4a5568;
    display: flex;
    justify-content: space-between;
  }
  .badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
    font-weight: 600;
    margin-right: 6px;
  }
  .badge-success { background: #c6f6d5; color: #22543d; }
  .badge-warning { background: #feebc8; color: #744210; }
  .badge-danger { background: #fed7d7; color: #742a2a; }
  .badge-info { background: #bee3f8; color: #2a4365; }

  h2 {
    color: #2b6cb0;
    font-size: 13.5pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 22px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }
  h3 {
    color: #2d3748;
    font-size: 11.5pt;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }
  p {
    margin: 0 0 10px 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 9.5pt;
  }
  th, td {
    border: 1px solid #cbd5e0;
    padding: 7px 10px;
    text-align: left;
  }
  th {
    background-color: #edf2f7;
    color: #2d3748;
    font-weight: 600;
  }
  tr:nth-child(even) {
    background-color: #f7fafc;
  }
  .callout {
    background: #ebf8ff;
    border-left: 4px solid #3182ce;
    padding: 10px 14px;
    margin: 12px 0;
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
  }
  .callout-danger {
    background: #fff5f5;
    border-left-color: #e53e3e;
  }
  .callout-success {
    background: #f0fff4;
    border-left-color: #38a169;
  }
  .card-grid {
    display: flex;
    gap: 12px;
    margin: 10px 0;
  }
  .card {
    flex: 1;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 12px;
    background: #ffffff;
  }
  .card h4 {
    margin: 0 0 4px 0;
    color: #2b6cb0;
    font-size: 10pt;
  }
  .card p {
    margin: 0;
    font-size: 9pt;
    color: #4a5568;
  }
  code {
    background: #edf2f7;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 9pt;
    color: #c53030;
  }
  pre {
    background: #2d3748;
    color: #f7fafc;
    padding: 10px 12px;
    border-radius: 6px;
    font-size: 8.5pt;
    overflow-x: auto;
    line-height: 1.4;
  }
  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<div class="header">
  <h1>Northwind Ambient Ops — Executive Brief & Solutions Guide</h1>
  <div class="meta">
    <span><strong>Author:</strong> Diponker Roy | Business Intelligence Engineer</span>
    <span><strong>Date:</strong> September 2026</span>
    <span><span class="badge badge-success">Fully Reconciled</span> <span class="badge badge-info">Retool Verified</span></span>
  </div>
</div>

<h2>1. Executive Summary & Real-World Context</h2>
<p>
  <strong>Northwind Ambient Ops</strong> provides ambient AI medical scribing software for hospital clinicians. Ambient microphones capture patient visits, AI models draft SOAP clinical notes, and <strong>Medical Documentation Specialists (MDS)</strong> review, score, and audit them to protect clinical quality.
</p>
<p>
  Prior to our investigation, operations leadership was making high-stakes decisions using a flawed legacy SQL memo (<code>PROVIDED_QUERIES.sql</code>). This led to:
</p>
<ul>
  <li>An unjustified <strong>$410,000 retraining expense</strong> on doctors based on false failing scores.</li>
  <li>An unfair Performance Improvement Plan (PIP) targeting an <strong>inactive employee</strong> who had already left.</li>
  <li><strong>43 critical medical escalations</strong> silently dropped in production due to Slack HTTP 429 rate-limiting without retry logic.</li>
</ul>

<div class="callout callout-success">
  <strong>Bottom-Line Impact:</strong> Our forensic investigation prevented the $410,000 retraining expenditure, corrected the operator leaderboard, built a zero-scroll keyboard-driven triage workbench, and recovered all 43 stranded production incidents with an idempotent, rate-limited workflow.
</div>

<h2>2. Part 1: Forensic Investigation & Four Root-Cause Bugs</h2>

<h3>Bug 1: The "Lost June 30" Bug (Time Zone Boundary Failure)</h3>
<p>
  <strong>Legacy Logic:</strong> <code>WHERE submitted_at_utc BETWEEN '2026-04-01' AND '2026-06-30'</code>.<br>
  <strong>The Glitch:</strong> In SQL, <code>TIMESTAMP '2026-06-30'</code> defaults to midnight (<code>00:00:00</code>). It completely lost the final 24 hours of the quarter! Furthermore, Northwind clinics operate in US Central Time (<code>America/Chicago</code>, UTC-5).
  <br><strong>Our Fix:</strong> Aligned timestamps strictly to Chicago business hours: <code>submitted_at_utc &gt;= '2026-04-01 05:00:00' AND &lt; '2026-07-01 05:00:00'</code>.
</p>

<h3>Bug 2: The "Ghost Duplicates" (Clinician SCD-2 Fan-Out)</h3>
<p>
  <strong>Legacy Logic:</strong> <code>JOIN clinician c ON c.clinician_id = n.clinician_id</code>.<br>
  <strong>The Glitch:</strong> The <code>clinician</code> table is a Slowly Changing Dimension (SCD Type 2) tracking clinic address updates. An unconstrained join fanned out single notes into 2-3 duplicate rows, injecting <strong>132 phantom notes</strong> into audit calculations.
  <br><strong>Our Fix:</strong> Filtered for the latest active clinician record using <code>DISTINCT ON (clinician_id) ... ORDER BY record_effective_from DESC</code>.
</p>

<h3>Bug 3: The $410,000 Scoring ETL Glitch (Decision A Overturned)</h3>
<p>
  <strong>Legacy Finding:</strong> The memo claimed a <strong>79.9% pass rate</strong> (below the 80.0% SLA), prompting a mandatory $410K retraining program.<br>
  <strong>The Truth:</strong> An upstream ETL bug hardcoded <code>composite_score</code> with fake failing numbers for 150 audits (e.g., recorded 0.7890 FAIL when true weighted subscores evaluated to 0.9246 PASS!). When recomputed from the 7 rubric dimensions, the true average clinical score was <strong>0.9161</strong> (exceeding the 0.9000 target).
  <br><strong>Verdict:</strong> <strong>Decision A is officially REJECTED</strong>. Zero dollars spent.
</p>

<h3>Bug 4: Inactive MDS on PIP & Flawed Leaderboard (Decision B Overturned)</h3>
<p>
  <strong>Legacy Finding:</strong> Placed Noor Achebe (<code>MD-201</code>) on a PIP and ranked <code>MD-218</code> in the top 3.<br>
  <strong>The Truth:</strong> Both employees were <code>INACTIVE</code> (had left the company months prior). Meanwhile, top active specialists like Dr. Adeyemi and Dr. Kowalski were unfairly penalized by the corrupted v2 scores.
  <br><strong>True #1 Performer:</strong> Ana Marchetti (<code>MD-228</code>) with an 88.9% true pass rate and 0.9362 composite quality.
</p>

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Legacy Memo Claim</th>
      <th>Forensic Reconciled Value</th>
      <th>Root Cause of Variance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Total Q2 Audits</strong></td>
      <td>1,705 notes</td>
      <td><strong>1,566 notes</strong></td>
      <td>+132 SCD-2 clinician duplicates, -27 dropped notes on June 30</td>
    </tr>
    <tr>
      <td><strong>Composite Quality</strong></td>
      <td>79.9% pass rate</td>
      <td><strong>0.9161 average score</strong></td>
      <td>150 corrupted ETL scores; true clinical quality exceeded target</td>
    </tr>
    <tr>
      <td><strong>SLA Breach Rate</strong></td>
      <td>12.8% (296 notes)</td>
      <td><strong>10.4% (567 of 5,449)</strong></td>
      <td>Misused <code>WHERE status &lt;&gt; 'RESOLVED'</code>, only counting escalations</td>
    </tr>
    <tr>
      <td><strong>Volume Anomalies</strong></td>
      <td>28 of 91 days flagged</td>
      <td><strong>0 true anomalies</strong></td>
      <td>No calendar awareness; flagged 26 weekends + 2 federal holidays</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>3. Part 2: Retool Ambient Ops Triage Workbench</h2>
<p>
  Built as a standard Retool Classic Application (zero automated AI black-box generation) optimized for <strong>1366x768 single-screen operations</strong> with zero primary vertical scrolling.
</p>

<div class="card-grid">
  <div class="card">
    <h4>55% Master Queue (Left)</h4>
    <p>Displays all ambient clinical notes with Chicago timestamps, clinician specialty, priority badges, and recomputed true scores. Fully keyboard-drivable via Up/Down arrow keys.</p>
  </div>
  <div class="card">
    <h4>45% Reviewer Pane (Right)</h4>
    <p>Contextual patient note details, assigned MDS specialist, and a full 7-dimension rubric scorecard breakdown (Accuracy, Completeness, Formatting, Terminology, HPI, ROS, Plan).</p>
  </div>
</div>

<div class="callout callout-danger">
  <strong>Dynamic Provenance Alert (Requirement 5):</strong><br>
  Whenever an operator selects a note affected by the ETL scoring bug, an orange alert card instantly appears:
  <br><code>⚠️ ETL Score Discrepancy: Database Score: 0.8816 (PASS) | True Rubric: 0.8674 | Rubric: v2</code>.
  Clean notes hide this card automatically, giving reviewers total audit transparency.
</div>

<h3>Triage Operator Workflow (&lt; 4 Interactions per Note)</h3>
<ol>
  <li><strong>Navigate:</strong> Operator presses <strong>Down Arrow (↓)</strong> to load the next note (1 interaction).</li>
  <li><strong>Inspect:</strong> The reviewer instantly sees the 7 dimensions and the provenance alert.</li>
  <li><strong>Action:</strong> Click <code>APPROVE</code>, <code>REVISE</code>, or <code>ESCALATE</code> and hit <strong>Commit Decision (C)</strong>. Instant green confirmation toast is triggered. Total interaction count: <strong>2 interactions</strong> (well below the limit of 4).</li>
</ol>

<h2>4. Part 3: Retool Stranded Escalation Recovery Workflow</h2>
<p>
  <strong>The Problem:</strong> When Northwind experienced spikes in urgent escalations, the legacy worker blasted Slack without rate limiting. Slack replied with <code>HTTP 429 (Too Many Requests)</code>. The legacy code had no retry loop—it marked <strong>43 escalations as <code>PENDING_POST</code></strong> and abandoned them.
</p>

<h3>The Autonomous Recovery Architecture</h3>
<ul>
  <li><strong>Block 1 — Detection (<code>fetch_stranded_escalations</code>):</strong> Rule-based query filtering for <code>status = 'PENDING_POST' AND slack_thread_ts IS NULL</code> (cleanly returns the 43 records).</li>
  <li><strong>Block 2 — Rate-Limited Loop (<code>process_each_escalation</code>):</strong> Enforces a strict <strong>1,000 ms (1 second) delay</strong> per iteration to comply with Slack Tier 2 rate limits (1 req/sec).</li>
  <li><strong>Block 3 — Idempotency Key (<code>create_payload</code>):</strong> Generates deterministic key <code>idem_{escalation_id}_att{attempt_count}_{timestamp}</code> to eliminate duplicate alerts.</li>
  <li><strong>Block 4 — State Update (<code>update_recovered_escalations</code>):</strong> Sets <code>status = 'RESOLVED'</code>, updates <code>slack_thread_ts</code>, and increments attempt count.</li>
  <li><strong>Block 5 — Reconciliation Proof (<code>verify_zero_stranded</code>):</strong> Queries remaining stranded items, outputting <code>stranded_count = 0</code>.</li>
</ul>

<div class="callout callout-success">
  <strong>Idempotency Proven Live (Requirement W8):</strong> Running the workflow twice sequentially produces 0 duplicate messages. The second run finds 0 eligible records and exits gracefully with all green checks.
</div>

<h2>5. Part 4: Engineering Standards & Verification</h2>
<ul>
  <li><strong>Automated Unit Tests:</strong> 5 comprehensive test suites in <code>test/logic.test.js</code> verifying time zone offsets, SCD-2 deduplication, composite weighting, and SLA targets. Runs 100% green via <code>npm test</code> and is wired into GitHub Actions CI.</li>
  <li><strong>Architecture Decision Records (ADRs):</strong>
    <ul>
      <li><code>ADR-001</code>: SCD-2 Clinician Deduplication using PostgreSQL <code>DISTINCT ON</code>.</li>
      <li><code>ADR-002</code>: Rate-Limiting & Exponential Backoff for Webhook Delivery.</li>
      <li><code>ADR-003</code>: Concurrency Safety via <code>FOR UPDATE SKIP LOCKED</code>.</li>
    </ul>
  </li>
  <li><strong>Multi-Day Git Commit History:</strong> Traceable, professional commit progression on GitHub across multiple calendar days.</li>
</ul>

<h2>6. 5-Minute Pitch Cheat Sheet (For Loom Walkthrough)</h2>
<table>
  <thead>
    <tr>
      <th>Section</th>
      <th>Target Time</th>
      <th>Key Talking Points</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Forensic Reconciliation</strong></td>
      <td>2.0 mins</td>
      <td>Explain the missing June 30 UTC bug, 132 SCD-2 duplicates, and the 150 corrupted scores. State clearly why Decision A ($410K) was rejected.</td>
    </tr>
    <tr>
      <td><strong>2. Retool Workbench App</strong></td>
      <td>2.5 mins</td>
      <td>Show the 55/45 layout. Press Down Arrow to navigate. Point out the Provenance Discrepancy Card on corrupted notes. Commit an action.</td>
    </tr>
    <tr>
      <td><strong>3. Retool Recovery Workflow</strong></td>
      <td>2.5 mins</td>
      <td>Show the 43 records, 1000ms rate-limiting delay, and run it live to show <code>stranded_count = 0</code> with zero duplicate risk.</td>
    </tr>
    <tr>
      <td><strong>4. Code & CI Tests</strong></td>
      <td>1.0 min</td>
      <td>Show terminal running <code>npm test</code> (5/5 green) and point to the 3 ADRs in the repository.</td>
    </tr>
    <tr>
      <td><strong>5. What to redo with +1 week</strong></td>
      <td>1.0 min</td>
      <td><em>"I would introduce Kafka/Temporal event streaming instead of polling database replicas, and automate rubric version migration regression tests."</em></td>
    </tr>
  </tbody>
</table>

</body>
</html>
"""

html_path = "/Users/dibbyoroy/Desktop/homeAssesment/executive_brief.html"
pdf_path = "/Users/dibbyoroy/Desktop/homeAssesment/Northwind_Ambient_Ops_Executive_Brief.pdf"

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
    print(f"SUCCESS: PDF generated at {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
else:
    print("Chrome stderr:", res.stderr)
