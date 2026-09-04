#!/usr/bin/env python3
"""
Northwind Ambient Ops - Visual Data Explorer
Interactive PostgreSQL Visualizer & Anomaly Inspector
"""

import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import psycopg2
from psycopg2.extras import RealDictCursor

PORT = 8080
PG_DB = "postgres"
PG_USER = os.environ.get("USER", "dibbyoroy")

def get_connection():
    return psycopg2.connect(
        dbname=PG_DB,
        user=PG_USER,
        host="localhost",
        port=5432
    )

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Northwind Ambient Ops | Visual Data Explorer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0a0f1d;
      --bg-secondary: #111827;
      --bg-card: rgba(17, 24, 39, 0.7);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-highlight: rgba(99, 102, 241, 0.3);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --accent-blue: #3b82f6;
      --accent-indigo: #6366f1;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #8b5cf6;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
                  radial-gradient(circle at 90% 80%, rgba(244, 63, 94, 0.08) 0%, transparent 40%),
                  var(--bg-primary);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      padding: 1rem 2rem;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      backdrop-filter: blur(12px);
      background: rgba(10, 15, 29, 0.8);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .logo-badge {
      background: linear-gradient(135deg, var(--accent-indigo), var(--accent-blue));
      width: 38px;
      height: 38px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.1rem;
      color: white;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }

    .brand-title h1 {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .brand-title p {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .db-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 0.35rem 0.85rem;
      border-radius: 999px;
      font-size: 0.75rem;
      color: #34d399;
      font-weight: 600;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    main {
      flex: 1;
      padding: 1.5rem 2rem;
      max-width: 1600px;
      width: 100%;
      margin: 0 auto;
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      backdrop-filter: blur(8px);
      transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      border-color: var(--border-highlight);
    }
    .kpi-label {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .kpi-value {
      font-size: 1.6rem;
      font-weight: 800;
      margin-top: 0.35rem;
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
    }
    .kpi-sub {
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--text-muted);
    }

    /* Tabs Bar */
    .nav-tabs {
      display: flex;
      gap: 0.5rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.5rem;
      margin-bottom: 1rem;
      overflow-x: auto;
    }

    .tab-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 0.55rem 1.1rem;
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.15s ease;
      white-space: nowrap;
    }
    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }
    .tab-btn.active {
      background: var(--accent-indigo);
      color: white;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    .tab-badge {
      background: rgba(255, 255, 255, 0.18);
      font-size: 0.7rem;
      padding: 0.15rem 0.45rem;
      border-radius: 999px;
      font-family: 'JetBrains Mono', monospace;
    }
    .tab-btn.anomaly-tab {
      margin-left: auto;
      border-color: rgba(244, 63, 94, 0.3);
      color: #fda4af;
      background: rgba(244, 63, 94, 0.1);
    }
    .tab-btn.anomaly-tab.active {
      background: var(--accent-rose);
      color: white;
    }

    /* Controls Bar */
    .controls-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1rem;
      background: var(--bg-card);
      padding: 0.75rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--border-color);
      flex-wrap: wrap;
    }

    .search-box {
      display: flex;
      align-items: center;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 0.4rem 0.8rem;
      gap: 0.5rem;
      flex: 1;
      max-width: 400px;
    }
    .search-box input {
      background: transparent;
      border: none;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.85rem;
      outline: none;
      width: 100%;
    }
    .search-box input::placeholder { color: #6b7280; }

    .pagination-bar {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .page-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      cursor: pointer;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: 500;
    }
    .page-btn:disabled {
      opacity: 0.3;
      cursor: not-allowed;
    }

    /* Table Container */
    .table-container {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: auto;
      max-height: calc(100vh - 360px);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      text-align: left;
    }

    thead th {
      background: #131d33;
      color: var(--text-muted);
      font-weight: 700;
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 10;
      white-space: nowrap;
      text-transform: uppercase;
      font-size: 0.7rem;
      letter-spacing: 0.05em;
    }

    tbody tr {
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      transition: background 0.1s ease;
    }
    tbody tr:hover {
      background: rgba(99, 102, 241, 0.06);
    }

    tbody td {
      padding: 0.75rem 1rem;
      white-space: nowrap;
      color: #e5e7eb;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
    }

    /* Badges */
    .badge {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
    }
    .badge-pass { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-fail { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-open { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-resolved { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-stranded { background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid #ef4444; font-weight: 700; animation: pulse 2s infinite; }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    /* Anomaly Callout Box */
    .anomaly-banner {
      background: rgba(244, 63, 94, 0.08);
      border: 1px solid rgba(244, 63, 94, 0.3);
      padding: 1rem 1.25rem;
      border-radius: 10px;
      margin-bottom: 1rem;
      display: none;
    }
    .anomaly-banner h3 {
      color: #fb7185;
      font-size: 0.95rem;
      margin-bottom: 0.25rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .anomaly-banner p {
      font-size: 0.8rem;
      color: #fecdd3;
    }

    /* Sub Anomaly Selector */
    .anomaly-selector {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }
    .anomaly-btn {
      background: rgba(0,0,0,0.4);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      font-size: 0.78rem;
      cursor: pointer;
      font-family: inherit;
    }
    .anomaly-btn.active {
      background: rgba(244, 63, 94, 0.2);
      border-color: var(--accent-rose);
      color: white;
      font-weight: 600;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="logo-badge">N</div>
      <div class="brand-title">
        <h1>Northwind Ambient Ops</h1>
        <p>PostgreSQL Replica Explorer & Integrity Inspector</p>
      </div>
    </div>
    <div class="db-status">
      <div class="status-dot"></div>
      PostgreSQL 14 Connected (localhost:5432 / postgres)
    </div>
  </header>

  <main>
    <!-- KPI Summary Grid -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Clinical Notes</div>
        <div class="kpi-value" id="kpi-notes">6,235 <span class="kpi-sub">(62 dupes)</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Audits Performed</div>
        <div class="kpi-value" id="kpi-audits">1,780 <span class="kpi-sub">Q2 Quality</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Escalations</div>
        <div class="kpi-value" id="kpi-escs">533 <span class="kpi-sub">(149 unresolved)</span></div>
      </div>
      <div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.4);">
        <div class="kpi-label" style="color: #f87171;">Stranded (HTTP 429)</div>
        <div class="kpi-value" style="color: #ef4444;" id="kpi-stranded">43 <span class="kpi-sub" style="color: #fca5a5;">Never sent</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">MDS Specialists</div>
        <div class="kpi-value" id="kpi-mds">34 <span class="kpi-sub">29 Active</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Clinicians</div>
        <div class="kpi-value" id="kpi-clinicians">64 <span class="kpi-sub">(4 SCD-2)</span></div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTable('note')">note <span class="tab-badge">6,235</span></button>
      <button class="tab-btn" onclick="switchTable('note_audit')">note_audit <span class="tab-badge">1,780</span></button>
      <button class="tab-btn" onclick="switchTable('escalation')">escalation <span class="tab-badge">533</span></button>
      <button class="tab-btn" onclick="switchTable('mds')">mds <span class="tab-badge">34</span></button>
      <button class="tab-btn" onclick="switchTable('clinician')">clinician <span class="tab-badge">64</span></button>
      <button class="tab-btn" onclick="switchTable('sla_config')">sla_config <span class="tab-badge">8</span></button>
      <button class="tab-btn" onclick="switchTable('rubric_weight')">rubric_weight <span class="tab-badge">14</span></button>
      <button class="tab-btn anomaly-tab" onclick="switchAnomalyMode()">🚨 Integrity Anomaly Views <span class="tab-badge" style="background: rgba(244,63,94,0.4);">5</span></button>
    </div>

    <!-- Anomaly Inspector Banner (shown in anomaly mode) -->
    <div class="anomaly-banner" id="anomaly-banner">
      <h3 id="anomaly-title">🚨 Profiling Anomaly View</h3>
      <p id="anomaly-desc">Viewing defect subset.</p>
    </div>

    <!-- Anomaly Sub-tabs -->
    <div class="anomaly-selector" id="anomaly-selector" style="display: none;">
      <button class="anomaly-btn active" onclick="loadAnomaly('stranded')">1. Stranded Escalations (43)</button>
      <button class="anomaly-btn" onclick="loadAnomaly('score_mismatch')">2. Audit Score Drift (150)</button>
      <button class="anomaly-btn" onclick="loadAnomaly('note_dupes')">3. Re-ingested Notes (62)</button>
      <button class="anomaly-btn" onclick="loadAnomaly('time_paradox')">4. Escalation Before Note (20)</button>
      <button class="anomaly-btn" onclick="loadAnomaly('void_activity')">5. Audits on Void Notes (18)</button>
    </div>

    <!-- Search & Pagination Controls -->
    <div class="controls-bar">
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #6b7280;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" id="search-input" placeholder="Search rows across columns..." oninput="handleSearch()">
      </div>
      <div class="pagination-bar">
        <span id="row-summary">Showing 0 of 0</span>
        <button class="page-btn" id="prev-btn" onclick="changePage(-1)" disabled>← Prev</button>
        <span id="page-indicator">Page 1</span>
        <button class="page-btn" id="next-btn" onclick="changePage(1)">Next →</button>
      </div>
    </div>

    <!-- Main Table -->
    <div class="table-container">
      <table id="data-table">
        <thead id="table-head">
          <tr><th>Loading schema...</th></tr>
        </thead>
        <tbody id="table-body">
          <tr><td style="text-align: center; padding: 2rem;">Connecting to PostgreSQL...</td></tr>
        </tbody>
      </table>
    </div>
  </main>

  <script>
    let currentMode = 'table'; // 'table' or 'anomaly'
    let currentTable = 'note';
    let currentAnomaly = 'stranded';
    let currentPage = 1;
    let pageSize = 50;
    let searchQuery = '';
    let totalRows = 0;

    const anomalyMeta = {
      stranded: {
        title: "Part 3 Defect: 43 Stranded Escalations (HTTP 429 Rate Limited)",
        desc: "These escalations have status 'PENDING_POST', empty slack_thread_ts, and error 'slack_api:ratelimited (HTTP 429)'. They were dropped by the Slack integration and were never seen or triaged by operators."
      },
      score_mismatch: {
        title: "QA Defect: 150 Mismatched Audit Composite Scores (Rubric v2)",
        desc: "Audits where the recorded composite_score contradicts the mathematical weighted sum of the 7 rubric dimensions. Passing scores were recorded as fails, driving the false 79.9% pass rate."
      },
      note_dupes: {
        title: "Grain Defect: 62 Re-ingested Notes with Multiple Ingestion IDs",
        desc: "Notes that have duplicate note_id records due to capture replays. Joining without resolving to the active ingestion_id causes Cartesian row explosion in reporting."
      },
      time_paradox: {
        title: "Chronology Defect: 20 Escalations Created BEFORE Note Submission",
        desc: "Logical impossibility where escalation created_at_utc occurs days or weeks prior to note submitted_at_utc due to batch ingestion clock skew."
      },
      void_activity: {
        title: "Governance Defect: 18 Audits Conducted on Retracted/Voided Notes",
        desc: "QA audits performed on encounters where is_void = true (wrong patient, duplicate encounter), skewing operational compliance totals."
      }
    };

    async function loadData() {
      const tbody = document.getElementById('table-body');
      tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding: 2rem; color: #9ca3af;">Loading data from PostgreSQL...</td></tr>';

      let url = '';
      if (currentMode === 'table') {
        url = `/api/data?table=${encodeURIComponent(currentTable)}&page=${currentPage}&limit=${pageSize}&q=${encodeURIComponent(searchQuery)}`;
      } else {
        url = `/api/anomaly?type=${encodeURIComponent(currentAnomaly)}&page=${currentPage}&limit=${pageSize}&q=${encodeURIComponent(searchQuery)}`;
      }

      try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.error) {
          tbody.innerHTML = `<tr><td colspan="10" style="color: #f43f5e; padding: 2rem;">Error: ${data.error}</td></tr>`;
          return;
        }

        renderTable(data.columns, data.rows);
        totalRows = data.total;
        updatePagination();
      } catch (err) {
        tbody.innerHTML = `<tr><td colspan="10" style="color: #f43f5e; padding: 2rem;">Failed to fetch data: ${err.message}</td></tr>`;
      }
    }

    function renderTable(columns, rows) {
      const thead = document.getElementById('table-head');
      const tbody = document.getElementById('table-body');

      if (!columns || columns.length === 0) {
        thead.innerHTML = '<tr><th>No Columns</th></tr>';
        tbody.innerHTML = '<tr><td style="text-align:center; padding: 2rem;">No matching records found.</td></tr>';
        return;
      }

      thead.innerHTML = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';

      if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${columns.length}" style="text-align:center; padding: 2rem; color: #9ca3af;">No records found.</td></tr>`;
        return;
      }

      tbody.innerHTML = rows.map(r => {
        return '<tr>' + columns.map(c => {
          let val = r[c];
          if (val === null || val === undefined) {
            return '<td style="color: #6b7280; font-style: italic;">NULL</td>';
          }
          let strVal = String(val);

          // Highlight special badges
          if (c === 'status' && strVal === 'PENDING_POST') {
            return `<td><span class="badge badge-stranded">${strVal}</span></td>`;
          }
          if (c === 'status' && strVal === 'OPEN') {
            return `<td><span class="badge badge-open">${strVal}</span></td>`;
          }
          if (c === 'status' && strVal === 'RESOLVED') {
            return `<td><span class="badge badge-resolved">${strVal}</span></td>`;
          }
          if (c === 'pass_fail' && strVal === 'PASS') {
            return `<td><span class="badge badge-pass">${strVal}</span></td>`;
          }
          if (c === 'pass_fail' && strVal === 'FAIL') {
            return `<td><span class="badge badge-fail">${strVal}</span></td>`;
          }
          if (c === 'is_void' && (strVal === 'true' || strVal === 'True')) {
            return `<td><span class="badge badge-fail">VOID</span></td>`;
          }
          if (c === 'last_api_error' && strVal.includes('429')) {
            return `<td style="color: #f87171; font-weight: 600;">${strVal}</td>`;
          }

          return `<td>${escapeHtml(strVal)}</td>`;
        }).join('') + '</tr>';
      }).join('');
    }

    function escapeHtml(text) {
      return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function switchTable(tbl) {
      currentMode = 'table';
      currentTable = tbl;
      currentPage = 1;
      searchQuery = '';
      document.getElementById('search-input').value = '';
      document.getElementById('anomaly-banner').style.display = 'none';
      document.getElementById('anomaly-selector').style.display = 'none';

      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.currentTarget.classList.add('active');
      loadData();
    }

    function switchAnomalyMode() {
      currentMode = 'anomaly';
      currentPage = 1;
      searchQuery = '';
      document.getElementById('search-input').value = '';
      document.getElementById('anomaly-banner').style.display = 'block';
      document.getElementById('anomaly-selector').style.display = 'flex';

      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.currentTarget.classList.add('active');

      loadAnomaly(currentAnomaly);
    }

    function loadAnomaly(type) {
      currentAnomaly = type;
      currentPage = 1;

      document.getElementById('anomaly-title').innerText = '🚨 ' + anomalyMeta[type].title;
      document.getElementById('anomaly-desc').innerText = anomalyMeta[type].desc;

      document.querySelectorAll('.anomaly-btn').forEach(b => b.classList.remove('active'));
      if (event && event.currentTarget && event.currentTarget.classList.contains('anomaly-btn')) {
        event.currentTarget.classList.add('active');
      }

      loadData();
    }

    function updatePagination() {
      const start = totalRows === 0 ? 0 : (currentPage - 1) * pageSize + 1;
      const end = Math.min(currentPage * pageSize, totalRows);
      const totalPages = Math.ceil(totalRows / pageSize) || 1;

      document.getElementById('row-summary').innerText = `Showing ${start}-${end} of ${totalRows.toLocaleString()} rows`;
      document.getElementById('page-indicator').innerText = `Page ${currentPage} of ${totalPages}`;
      document.getElementById('prev-btn').disabled = currentPage <= 1;
      document.getElementById('next-btn').disabled = currentPage >= totalPages;
    }

    function changePage(delta) {
      currentPage += delta;
      loadData();
    }

    let searchTimeout;
    function handleSearch() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        searchQuery = document.getElementById('search-input').value.trim();
        currentPage = 1;
        loadData();
      }, 300);
    }

    // Initial Load
    window.addEventListener('DOMContentLoaded', () => {
      loadData();
    });
  </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        elif path == "/api/data":
            table = params.get("table", ["note"])[0]
            page = int(params.get("page", [1])[0])
            limit = int(params.get("limit", [50])[0])
            q = params.get("q", [""])[0]

            # Allowed tables check
            allowed_tables = ["note", "note_audit", "clinician", "mds", "sla_config", "rubric_weight", "escalation"]
            if table not in allowed_tables:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid table"}).encode("utf-8"))
                return

            offset = (page - 1) * limit
            conn = get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            try:
                # Column check
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;", (table,))
                cols = [r["column_name"] for r in cur.fetchall()]

                where_clause = ""
                params_list = []
                if q:
                    like_clauses = [f"CAST({col} AS TEXT) ILIKE %s" for col in cols]
                    where_clause = f"WHERE {' OR '.join(like_clauses)}"
                    params_list = [f"%{q}%" for _ in cols]

                # Total count
                cur.execute(f"SELECT COUNT(*) FROM {table} {where_clause};", params_list)
                total = cur.fetchone()["count"]

                # Fetch rows
                cur.execute(f"SELECT * FROM {table} {where_clause} LIMIT %s OFFSET %s;", params_list + [limit, offset])
                rows = cur.fetchall()

                # Convert to string serializable
                serializable_rows = []
                for r in rows:
                    row_dict = {}
                    for k, v in r.items():
                        row_dict[k] = str(v) if v is not None else None
                    serializable_rows.append(row_dict)

                res_data = {
                    "total": total,
                    "columns": cols,
                    "rows": serializable_rows
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res_data).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            finally:
                cur.close()
                conn.close()
            return

        elif path == "/api/anomaly":
            anomaly_type = params.get("type", ["stranded"])[0]
            page = int(params.get("page", [1])[0])
            limit = int(params.get("limit", [50])[0])
            q = params.get("q", [""])[0]

            conn = get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            try:
                sql = ""
                count_sql = ""

                if anomaly_type == "stranded":
                    base_sql = "FROM escalation WHERE status = 'PENDING_POST' OR last_api_error ILIKE '%%429%%'"
                    select_cols = "escalation_id, note_id, created_at_utc, status, last_api_error, attempt_count, slack_channel, slack_thread_ts"
                    sql = f"SELECT {select_cols} {base_sql} ORDER BY created_at_utc DESC"
                    count_sql = f"SELECT COUNT(*) {base_sql}"

                elif anomaly_type == "score_mismatch":
                    base_sql = """
                        FROM note_audit a
                        JOIN (
                            SELECT rubric_version,
                                MAX(CASE WHEN dimension = 'accuracy' THEN weight END) AS w_acc,
                                MAX(CASE WHEN dimension = 'completeness' THEN weight END) AS w_comp,
                                MAX(CASE WHEN dimension = 'formatting' THEN weight END) AS w_fmt,
                                MAX(CASE WHEN dimension = 'terminology' THEN weight END) AS w_term,
                                MAX(CASE WHEN dimension = 'hpi' THEN weight END) AS w_hpi,
                                MAX(CASE WHEN dimension = 'ros' THEN weight END) AS w_ros,
                                MAX(CASE WHEN dimension = 'plan' THEN weight END) AS w_plan
                            FROM rubric_weight
                            GROUP BY rubric_version
                        ) r ON a.rubric_version = r.rubric_version
                        WHERE ABS(a.composite_score - ROUND((a.score_accuracy*r.w_acc + a.score_completeness*r.w_comp + a.score_formatting*r.w_fmt + a.score_terminology*r.w_term + a.score_hpi*r.w_hpi + a.score_ros*r.w_ros + a.score_plan*r.w_plan)::numeric, 4)) > 0.005
                    """
                    select_cols = """
                        a.audit_id, a.note_id, a.rubric_version, a.composite_score AS recorded_score,
                        ROUND((a.score_accuracy*r.w_acc + a.score_completeness*r.w_comp + a.score_formatting*r.w_fmt + a.score_terminology*r.w_term + a.score_hpi*r.w_hpi + a.score_ros*r.w_ros + a.score_plan*r.w_plan)::numeric, 4) AS true_calculated_score,
                        ROUND((a.composite_score - (a.score_accuracy*r.w_acc + a.score_completeness*r.w_comp + a.score_formatting*r.w_fmt + a.score_terminology*r.w_term + a.score_hpi*r.w_hpi + a.score_ros*r.w_ros + a.score_plan*r.w_plan))::numeric, 4) AS discrepancy,
                        a.pass_fail AS recorded_status,
                        CASE WHEN (a.score_accuracy*r.w_acc + a.score_completeness*r.w_comp + a.score_formatting*r.w_fmt + a.score_terminology*r.w_term + a.score_hpi*r.w_hpi + a.score_ros*r.w_ros + a.score_plan*r.w_plan) >= 0.90 THEN 'SHOULD_PASS' ELSE 'FAIL' END AS true_status
                    """
                    sql = f"SELECT {select_cols} {base_sql} ORDER BY ABS(a.composite_score - (a.score_accuracy*r.w_acc + a.score_completeness*r.w_comp + a.score_formatting*r.w_fmt + a.score_terminology*r.w_term + a.score_hpi*r.w_hpi + a.score_ros*r.w_ros + a.score_plan*r.w_plan)) DESC"
                    count_sql = f"SELECT COUNT(*) {base_sql}"

                elif anomaly_type == "note_dupes":
                    base_sql = """
                        FROM note n
                        JOIN (
                            SELECT note_id, COUNT(*) AS count
                            FROM note
                            GROUP BY note_id
                            HAVING COUNT(*) > 1
                        ) d ON n.note_id = d.note_id
                    """
                    select_cols = "n.note_id, n.ingestion_id, n.encounter_id, n.clinician_id, n.product_line, n.submitted_at_utc, n.delivered_at_utc, n.ingested_at_utc, d.count AS total_versions"
                    sql = f"SELECT {select_cols} {base_sql} ORDER BY n.note_id, n.ingested_at_utc"
                    count_sql = f"SELECT COUNT(*) {base_sql}"

                elif anomaly_type == "time_paradox":
                    base_sql = """
                        FROM escalation e
                        JOIN note n ON e.note_id = n.note_id
                        WHERE e.created_at_utc < n.submitted_at_utc
                    """
                    select_cols = """
                        e.escalation_id, e.note_id, e.created_at_utc AS escalation_created,
                        n.submitted_at_utc AS note_submitted,
                        ROUND(EXTRACT(EPOCH FROM (n.submitted_at_utc - e.created_at_utc))/86400.0, 1) AS days_before_note_submission,
                        e.status
                    """
                    sql = f"SELECT {select_cols} {base_sql} ORDER BY days_before_note_submission DESC"
                    count_sql = f"SELECT COUNT(*) {base_sql}"

                elif anomaly_type == "void_activity":
                    base_sql = """
                        FROM note_audit a
                        JOIN note n ON a.note_id = n.note_id
                        WHERE n.is_void = true
                    """
                    select_cols = "a.audit_id, a.note_id, a.audited_at_utc, a.composite_score, a.pass_fail, n.is_void, n.void_reason"
                    sql = f"SELECT {select_cols} {base_sql} ORDER BY a.audited_at_utc"
                    count_sql = f"SELECT COUNT(*) {base_sql}"

                # Execute count
                cur.execute(count_sql)
                total = cur.fetchone()["count"]

                # Execute query with limit/offset
                offset = (page - 1) * limit
                cur.execute(f"{sql} LIMIT %s OFFSET %s;", [limit, offset])
                rows = cur.fetchall()

                cols = list(rows[0].keys()) if rows else []
                serializable_rows = []
                for r in rows:
                    row_dict = {}
                    for k, v in r.items():
                        row_dict[k] = str(v) if v is not None else None
                    serializable_rows.append(row_dict)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "total": total,
                    "columns": cols,
                    "rows": serializable_rows
                }).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            finally:
                cur.close()
                conn.close()
            return

        self.send_response(404)
        self.end_headers()

def run():
    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    print(f"Visual Explorer Server running at http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
