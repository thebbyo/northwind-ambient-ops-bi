# Submission Checklist

Fill this in, commit it, and confirm every line before you submit. An unfilled checklist is treated as an incomplete submission.

**Candidate:** Senior Business Intelligence Engineer  
**Date submitted:** 2026-09-04  
**Hours spent (honest):** 7.5 hours  

---

### Access
- [x] Retool app shared with `moontasir.abeer@commure.com`
- [x] Retool app shared with `musfiqur.preo@commure.com`
- [x] Retool app shared with `shakira.mustahid@commure.com`
- [x] A Retool Release version is tagged
- [x] GitHub repo accessible to reviewers - URL: `https://github.com/dibbyoroy/northwind-ambient-ops-bi`
- [ ] Video link (≤12 min, single take, screen + voice): `[Add Loom/YouTube link here]`

---

### Part 1 — Reconciliation
- [x] `RECONCILIATION.md` committed
- [x] Data profiling written up (grains, SCD-2 clinicians, multi-ingest notes)
- [x] Variance waterfall with per-correction quantification, for each headline metric
- [x] "The quarter" defined and defended (America/Chicago business calendar vs UTC)
- [x] Decision A and Decision B answered in ≤400 words
- [x] Known unknowns stated
- [x] **Number of defects I believe I found: 11** (1. June 30 boundary truncation; 2. SCD-2 clinician fan-out; 3. Accidental escalation inner join on SLA; 4. SLA target double-counting; 5. Volume alert weekend/holiday false positives; 6. Corrupted v2 composite scores; 7. Retroactive v2 rubric application on pre-May 15 notes; 8. Audits on void notes; 9. Inactive employees on leaderboard; 10. 43 Stranded HTTP 429 escalations; 11. 20 Clock-skewed escalations logged before note submission).

---

### Part 2 — Triage Workbench
- [x] Works at 1366×768, no vertical scroll on the primary pane (R1)
- [x] Interaction count per case: **2 interactions** (R2, math shown in `UX_RATIONALE.md`)
- [x] Keyboard-only core loop, keymap documented (R3)
- [x] Selection / scroll / filters survive a refresh (R4)
- [x] Provenance panel shows the SLA target in force on the note's date (R5)
- [x] Empty, loading and error states designed; error state demoed in video (R6)
- [x] Explicit commit, optimistic, with visible rollback (R7)
- [x] Bulk action, safe to double-submit (R8)
- [x] Status survives greyscale; contrast ≥4.5:1 (R9)
- [x] Queue derived from my corrected logic (R10)
- [x] `UX_RATIONALE.md` committed, including two rejected layouts and the requirement I did not fully satisfy

---

### Part 3 — Recovery Workflow
- [x] Detection rule defined and justified, no hardcoded IDs (W1)
- [x] Posts to a real endpoint I control (W2) - endpoint: `https://webhook.site/northwind-ambient-recovery`
- [x] Idempotent across 5 runs, demonstrated in video (W3)
- [x] Rate limit ≤1 rps with jitter; exponential backoff on 429/5xx (W4)
- [x] Dead-letter path after N attempts (N=5 justified), into a state a human can find and act on (W5)
- [x] Safe to run concurrently; guard explained (`FOR UPDATE SKIP LOCKED`) (W6)
- [x] Audit trail table designed by me; DDL in `sql/recovery_audit.sql`, keys/types/indexes justified (W7)
- [x] Reconciliation query proving zero stranded, zero duplicates (W8)

---

### Part 4 — Practice
- [x] Commits span ≥2 calendar days
- [x] ≥1 PR with my own review comments
- [x] JS lives in the repo as versioned modules (`src/logic.js`), imported into Retool
- [x] Tests green in GitHub Actions - covering TZ boundary, dedupe, effective-dated lookup, idempotency key
- [x] ≤3 ADRs in `docs/adr/`
- [x] `DECISIONS.md` - stakeholder conflict identified and resolved
- [x] `AI_USAGE.md` - including one instance where I overrode AI output
- [x] `README.md` answers "what is wrong with this assessment?" (≤150 words)

---

### Declaration
- [x] Every number in my written deliverables is reproducible from a query in this repo.
- [x] `AI_USAGE.md` is complete and accurate.
