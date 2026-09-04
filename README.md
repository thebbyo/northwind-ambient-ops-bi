# Northwind Ambient Ops — Business Intelligence Practical Assessment

This repository contains the complete forensic audit, reconciliation models, Retool operator workbench architecture, and stranded escalation recovery workflows for Global Operations.

---

## Repository Structure

```
.
├── RECONCILIATION.md       # Forensic data profiling, true values & variance waterfalls (Part 1)
├── UX_RATIONALE.md         # Retool Triage Workbench interaction budget & keymap (Part 2)
├── DECISIONS.md            # Stakeholder conflict reconciliation & trade-offs (Part 4)
├── AI_USAGE.md             # AI disclosure & instance of overriding AI proposal (Part 4)
├── docs/adr/               # 3 Architectural Decision Records (SCD-2, Concurrency, UX commit)
├── sql/
│   ├── schema_postgres.sql # Initial unconstrained replica DDL
│   └── recovery_audit.sql  # Part 3 audit trail DDL, locking query & reconciliation query
├── src/
│   └── logic.js            # Pure modular JavaScript functions imported into Retool
├── test/
│   └── logic.test.js       # Unit tests covering TZ boundary, dedupe, SLA, idempotency
├── app.py                  # Local Visual Data Explorer & Anomaly Inspector (http://localhost:8080)
└── .github/workflows/      # Automated CI test runner
```

---

## Quickstart & Verification

### 1. Database & Visual Explorer
The operational replica is loaded in local PostgreSQL (`postgres:5432`). Launch the visual explorer:
```bash
python3 app.py
# Open http://localhost:8080 to inspect all 7 tables and 5 diagnostic anomaly views
```

### 2. Run Automated Unit Tests
```bash
npm test
```

---

## What is Wrong With This Assessment? (≤150 Words)

> This assessment tests an exceptional range of forensic SQL, edge-case debugging, and Retool mechanics, but it measures a **forensic data platform investigator** rather than an operational **Business Intelligence Engineer**.
>
> In production, a BIE's highest leverage is **not** reverse-engineering corrupted ETL math or rescuing webhook rate limits; it is **translating clinical strategy into operational alignment**, partnering with clinical directors, establishing metric consensus across ambiguous business domains, and designing data products that proactively change human behavior.
>
> To measure true BI engineering excellence, I would have tested:
> 1. **Live Stakeholder Alignment:** Facilitating an ambiguous metric discovery session with a clinical pod lead to define "preventable documentation failure."
> 2. **Proactive Dimensional Modeling:** Designing a star-schema marts layer (`fact_encounter_turnaround`) with automated dbt tests to prevent bad data from ever entering the reporting layer.
