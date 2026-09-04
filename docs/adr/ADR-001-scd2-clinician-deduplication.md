# ADR-001: SCD Type 2 Clinician Handling in Operational Serving Layer

## Status
Accepted

## Context
The operational replica lands clinician dimension updates as Slowly Changing Dimension Type 2 (SCD-2) records without a primary key constraint. Four clinicians currently have multiple active/historical rows. Naive downstream queries joining on `clinician_id` cause Cartesian multiplication, duplicating 433 clinical notes and inflating billing and audit counts.

## Options Considered
1. **Option 1: Query-level filtering on `is_current_record = true`:** Simple, but historical encounters authored prior to a clinician's transfer would be improperly attributed to their new department/region.
2. **Option 2: Point-in-time effective date joining (`note.submitted_at_utc BETWEEN record_effective_from AND record_effective_to`):** Accurate, but complex for ad-hoc BI querying and computationally expensive on unindexed tables.
3. **Option 3: Modeled Serving View (`core_clinician_at_submission`):** A pre-joined dimensional view that materializes the exact clinician state in effect at the moment of encounter submission.

## Decision
We chose **Option 3** for core reporting views, combined with strict `(clinician_id, record_effective_from)` composite primary keys in the serving schema.

## Consequences
* **Positive:** Completely eliminates Cartesian fan-outs in executive reporting while preserving historical audit attribution.
* **Negative:** Requires ingestion pipelines to enforce temporal validity checks (`record_effective_to >= record_effective_from`).
