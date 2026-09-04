# ADR-003: Two-Stroke Keyboard Commit vs. Single-Click Row Mutation

## Status
Accepted

## Context
In `APPENDIX_B_STAKEHOLDER_REQUESTS.md`, the Operations Director requested a single-click row mutation workflow (`R-01`: *"Click the row and have it be done, straight from the table"*). Conversely, the QA Lead (`R-02`), Compliance (`R-04`), and engineering requirements (`R7`) require explicit confirmation to avoid accidental mutations on clinician-facing records.

## Options Considered
1. **Option 1: Unconfirmed Single Row-Click Mutation:** Fastest for operators, but highly susceptible to accidental misclicks, creating compliance liabilities.
2. **Option 2: Modal Dialog Confirmation:** Safe, but adds 3–4 clicks per case and breaks keyboard-only navigation flow (`R2`, `R3`).
3. **Option 3: Two-Stroke Keyboard Commit with Optimistic UI & Rollback Window:** Operator presses `[1]`–`[3]` to set disposition, followed by `[C]` or `[Enter]` to commit. The UI updates optimistically with a 5-second undo toast (`[U]`).

## Decision
We chose **Option 3**. The two-stroke keyboard model satisfies the velocity requirements of Operations while guaranteeing deliberate confirmation and audit compliance.

## Consequences
* **Positive:** Sub-second operational cycle time ($\le 2$ interactions after selection), compliant with `R2`, `R3`, and `R7`.
* **Positive:** Zero risk of accidental table click mutations.
* **Negative:** Deliberately does not satisfy the Ops Director's single-click request, but replaces it with an equally fast keyboard alternative.
