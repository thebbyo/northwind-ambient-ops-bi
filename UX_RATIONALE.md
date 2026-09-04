# UX Rationale: The Triage Workbench

**Document:** `UX_RATIONALE.md`  
**Author:** Senior Business Intelligence & Database Engineer  
**Reference:** Retool Triage Workbench (`Part 2`)  

---

## 1. Operator Time-on-Task Budget

For an Audit Triage Lead managing a queue of 2,500–3,000 cases after a weekend backlog (`R-03`), operational efficiency is critical. Every second saved per case returns **~1.5 hours of senior specialist capacity per week**.

| Stage | Activity | Time Budget (Sec) | Cognitive Focus |
| :--- | :--- | :---: | :--- |
| **1. Ingestion / Selection** | Row auto-selected via keyboard (`[J]`/`[K]`) | **0.2s** | Zero-latency DOM update; cursor jumps to next case. |
| **2. Clinical Scanning** | Review full note text & highlighted failing sections | **3.5s** | Right pane displays complete SOAP note without clicks (`R-02`). |
| **3. Metric Verification** | Inspect the 7 sub-scores vs. historical threshold | **1.8s** | Provenance card highlights the SLA & rubric active on note date (`R5`). |
| **4. Disposition Decision** | Select disposition code (`[1]` Overturn, `[2]` Uphold, `[3]` Re-route) | **0.5s** | One keystroke maps disposition & reason code. |
| **5. Optimistic Commit** | Commit verdict via `[C]` / `[Enter]` | **0.5s** | Immediate optimistic removal from queue with 5-second undo toast (`R7`). |
| **Total Time per Case** | **End-to-End Triage Cycle** | **6.5s** | **Throughput: ~550 cases/hour per triage lead.** |

---

## 2. Requirement R2 Interaction Count Math

**Requirement R2:** A full triage decision on one case takes $\le 4$ interactions after selection.

### Actual Interaction Math: Exactly 2 Keystrokes (or 2 Clicks)
After selecting a case from the queue:
1. **Interaction 1 (Keystroke `[1]`–`[3]`):** Sets the triage disposition and pre-populates the default operational reason code:
   * Key `[1]`: Overturn Audit (Reason: *Corrupted v2 Formula* / *Pass Standard Met*).
   * Key `[2]`: Uphold Audit (Reason: *Confirmed Clinical Inaccuracy*).
   * Key `[3]`: Re-route to Clinical Lead (Reason: *Ambiguous Documentation*).
2. **Interaction 2 (Keystroke `[C]` or `[Enter]`):** Submits the disposition optimistically, broadcasts the update, and automatically advances the selection to the next row.

$$\text{Actual Interaction Count} = 1 \text{ (Set Disposition)} + 1 \text{ (Commit)} = \mathbf{2 \text{ Interactions}} \le 4 \quad \checkmark$$

---

## 3. Keyboard-Only Navigation Keymap (`R3`)

The entire triage loop operates with zero mouse dependency:

| Key Binding | Action | Operational Purpose |
| :---: | :--- | :--- |
| `J` / `↓` | Select Next Case | Move selection down the 3,000-row queue. |
| `K` / `↑` | Select Previous Case | Move selection up the queue. |
| `1` | Disposition: **Overturn Fail** | Marks case as passing; applies default correction code. |
| `2` | Disposition: **Uphold Fail** | Confirms audit failure; schedules clinician feedback. |
| `3` | Disposition: **Re-route to Pod Lead** | Transfers case to specialized pod review. |
| `C` or `Enter` | **Commit Decision** | Executes optimistic update, removes from active queue, advances to next. |
| `U` or `Ctrl+Z` | **Undo Last Action** | Reverses last optimistic commit within 5-second rollback window. |
| `/` | **Focus Search** | Jumps cursor to queue search input. |

---

## 4. Two Rejected Layouts & Architectural Trade-offs

### Rejected Layout 1: Modal Dialog / Pop-up Inspector
* **The Concept:** Clicking a row opens a modal dialog overlaying the screen with the note text and scoring inputs.
* **Why Rejected:**
  1. **Cognitive Disorientation:** Modals obstruct queue context, preventing the operator from assessing queue velocity or adjacent cases.
  2. **Interaction Inflation:** Requires an explicit close/dismiss interaction (`[Esc]` or clicking "X"), raising the interaction count to 4–5 steps and violating requirement `R2`.
  3. **Layout Shift:** Violates requirement `R6` (modal pop-ups cause disruptive layout shifts).

### Rejected Layout 2: Accordion Table Row Expansion
* **The Concept:** Expanding the table row downward to show note text and sub-scores inline beneath the row.
* **Why Rejected:**
  1. **Height Distortion:** A 500-word note expands a 35px table row into an 800px block, immediately blowing past the 768px vertical limit (`R1`) and causing erratic viewport jumping during keyboard scrolling.
  2. **Poor Contrast & Scanning:** Compressing 7 metric scorecards into an inline table expansion fails accessibility text contrast guidelines (`R9`).

### Selected Layout: Split Master-Detail Workspace (55% Queue / 45% Review Pane)
* **Left Pane (55% width):** High-density virtualized queue displaying Case ID, MDS author, Rubric Version, Recorded Score, and Flag badges.
* **Right Pane (45% width):** Fixed Reviewer Pane with 3 sticky sections:
  1. **Clinical Note Preview:** Full transcript with word count and encounter context.
  2. **7-Dimension Scorecard:** Color-neutral chips showing individual scores with contrast $\ge 4.5:1$ (`R9`).
  3. **Historical Provenance Panel (`R5`):** Displays which rule triggered the flag, the rubric active on the *note date*, and the SLA target in force when written.

---

## 5. Deliberately Unsatisfied Requirement & The Trade Made

* **Requirement Not Fully Satisfied:** Operations Director's Request `R-01` (*"One click, straight from the table, no save button"*).
* **The Trade Made:** We deliberately enforced an explicit two-stroke commit (`[Key]` $\rightarrow$ `[Commit]`) rather than a single row-click mutation.
* **Justification:** 
  Single-click row mutation is catastrophic in clinical operations. Accidental mouse clicks during rapid queue browsing would inadvertently overturn safety-critical audit fails and transmit unreviewed records to external EHRs, creating severe compliance liabilities (`R-04`) and violating engineering rule `R7`. The two-stroke keyboard model delivers identical sub-second velocity with zero risk of misclicks.
