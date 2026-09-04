# AI Usage Disclosure & Engineering Judgment Record

**Document:** `AI_USAGE.md`  
**Author:** Senior Business Intelligence & Database Engineer  
**Reference:** Commure Practical Assessment Grading Requirement `6.6`  

---

## 1. Where AI Was Used & Scope of Assistance

In alignment with the assessment instructions (*"Using AI is allowed and expected. What we are measuring is judgment, not abstinence"*), generative AI was utilized as a pair-programming partner in the following areas:

1. **SQL Ingestion Scaffolding:** Assisting in generating the initial PostgreSQL DDL types (`schema_postgres.sql`) and `\copy` stream pipelines.
2. **Data Profiling Automation:** Writing rapid Python profiling scripts to iterate through Cartesian product checks across the 7 CSV tables.
3. **Drafting Initial Layout Ideas:** Proposing candidate UI layouts for the Retool Triage Workbench.

---

## 2. Concrete Instance Where AI Output Was Rejected & Corrected

### The AI's Proposal:
During the initial reconciliation of the **79.9% Audit Pass Rate**, the AI model suggested that the drop below the 90% target was driven by **clinician specialization variance** (e.g., that Family Medicine or Cardiology notes had lower documentation completeness). The model proposed writing a query that filtered out "outlier surgical specialties" to explain away the pass rate deficit to leadership.

### Why It Was Rejected (Engineering Judgment):
1. **Clinical Invalidity:** In operational healthcare, you cannot arbitrarily slice out medical specialties to manufacture a passing metric. That is deceptive reporting, not reconciliation.
2. **Data Ground Truth:** When we inspected the raw mathematical dimension scores (`score_accuracy`, `score_completeness`, `score_plan`), clinicians were consistently scoring between **0.88 and 0.98**, with the actual mathematical average sitting at **0.9161** (well above the 0.90 quality standard).
3. **The True Underlying Defect:** By inspecting the row-level records rather than blindly accepting the AI's statistical grouping, we uncovered that **150 audits under rubric `v2` had their `composite_score` corrupted by a buggy ETL script** (e.g., audit `AU-10829` evaluated to `0.9246 PASS`, but was recorded as `0.7890 FAIL`).

### The Correction Applied:
We discarded the AI's specialty-filtering hypothesis and instead built the **exact mathematical formula recalculation engine** that compared stored composite scores against the weighted sum of the 7 rubric dimensions. This proved that the pass rate gap was an ETL calculation bug rather than a clinician skill deficit, ultimately saving the company from funding a $410,000 retraining program.
