# Architectural & Operational Decision Record: Stakeholder Reconciliation

**Document:** `DECISIONS.md`  
**Author:** Senior Business Intelligence & Database Engineer  
**Reference:** `APPENDIX_B_STAKEHOLDER_REQUESTS.md` & Retool Workbench Specification  

---

## 1. Identified Stakeholder Conflicts

In reviewing stakeholder requirements across Operations, QA, Product, and Compliance, we identified **two irreconcilable conflicts**:

### Conflict 1: "One-Click Instant Row Mutation" vs. "Deliberate Second Confirmation"
* **Stakeholder 1 — Operations Director (`R-01`, `R-05`):**
  > *"When I've decided on a case I want to click the row and have it be done — one click, straight from the table. I don't want to hunt for a Save button... The leads are fast and hate the mouse."*
* **Stakeholder 2 — QA Lead & Compliance (`R-02`, `R-04`):**
  > *"Anything that changes a clinician-facing record needs a deliberate second confirmation. We've had accidental dispositions before and it created a real mess with a physician group."*
* **The Assessment Hard Rule (`R7`):**
  > *"Row-click alone must not mutate anything."*

### Conflict 2: "Display Entire 3,000-Row Queue With Zero Scrolling" vs. "Full Note Text & 7 Sub-Scores Always Visible" at 1366×768 (`R-01`, `R-02`, `R-03`, `R-06`, `R1`)
* **Operations Director (`R-01`):** *"I want to see the whole queue on one screen. No scrolling, no pagination, no 'next 50'."*
* **Head of Product (`R-03`, `R-06`):** *"Monday morning queues run 2,500–3,000 cases... Keep it to one screen please."*
* **QA Lead (`R-02`):** *"The reviewer cannot make a defensible call without the full note text in front of them and all seven sub-scores visible at the same time. Nothing hidden behind a click, nothing in a tooltip."*
* **The Reality at 1366×768 (`R1`):** Rendering 3,000 rows in a table while dedicating screen real estate to full clinical notes (averaging 450+ words) and 7 metric cards on a 768px vertical viewport without a scroll container is physically and visually impossible.

---

## 2. Who I Went Back To and What I Asked

### Question to Operations Director:
> *"We cannot allow a single row-click to mutate production EHR records because accidental clicks have previously corrupted physician relations (and directly violate Compliance R-04 and Platform Constraint R7). If we give your operators a rapid 2-key keyboard sequence (`[D]` for disposition $\rightarrow$ `[Enter]` to commit) with an immediate 5-second undo toast, would that meet your speed benchmark without relying on dangerous single-click row mutation?"*

### Question to QA Lead & Head of Product:
> *"At a 1366×768 viewport, displaying 3,000 simultaneous table rows alongside a 500-word clinical note pane and 7 dimension scorecards causes layout overflow. If we implement a virtualized master-detail view where the left pane holds a virtualized queue and the right pane permanently displays the full note text and provenance breakdown for the active case, will your reviewers have the clinical defensibility they need?"*

---

## 3. What I Chose (The Architecture Decision)

1. **Rejected Single-Click Row Mutation in Favor of Keyboard-Operable Two-Stroke Commits:**
   * Selecting a row (via mouse click or `[J]`/`[K]` navigation) **only highlights and loads the case into the preview pane**. It performs zero database mutations (`R7`).
   * Committing requires an explicit action: `[1]`–`[3]` to select disposition, followed by `[C]` or `[Enter]` to commit.
   * Changes are applied optimistically in the UI with a visible 5-second undo banner and rollback capability on API failure.
2. **Master-Detail Layout with Virtualized Scroll Container for the 3,000-Case Queue:**
   * Split the 1366px screen into two fixed panels:
     * **Left Panel (55% width):** Compact virtualized queue holding up to 3,000 cases with sticky filter pills (`High Priority`, `v2 Rubric`, `Stranded`).
     * **Right Panel (45% width):** The permanent Reviewer Workspace showing the full note transcript, 7 sub-score chips, and the historical SLA/rubric provenance panel (`R5`).
   * Eliminated pagination ("next 50") by using infinite DOM virtualization, fulfilling the Ops Director's desire to avoid paginated navigation while respecting the 768px height limit.

---

## 4. What I Gave Up (The Explicit Trade-Offs)

1. **Gave up the Ops Director's "One-Click Done" requirement:**
   * *Rationale:* Patient safety, compliance auditability (`R-04`), and engineering integrity rule `R7` strictly prohibit accidental row-click mutation. 
   * *Mitigation:* Replaced it with a $\le 3$-keystroke workflow that is faster than mouse hunting and immune to misclicks.
2. **Gave up displaying all 3,000 rows simultaneously without a scrollbar:**
   * *Rationale:* 3,000 table rows require $\approx 105,000\text{px}$ of vertical height. Displaying them on a 768px screen without a virtualized scroll container is physically impossible.
   * *Mitigation:* Used client-side virtualized scrolling where all 3,000 rows reside in memory, preserving scroll position and active filter state across refreshes (`R4`).
