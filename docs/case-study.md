# Implementation case study: import preparation

## Context and boundaries

This fictional scenario models the preparation of two years of demographic and
admission history for an EHR transition. It is inspired by healthcare data work,
but the fixtures, program codes, schemas, and counts are invented. My real
Avatar-to-Credible work currently covers extraction, cleaning, mapping, and
preparation in provided spreadsheet templates; this project does not claim a
completed production import.

## Source-to-target mapping

| Source field | Demo target | Transformation or decision |
|---|---|---|
| client_id | client_id | Text type; preserve leading zeros; required and unique |
| display_name | display_name | Trim whitespace; required in this fictional schema |
| dob | dob | Normalize ISO or US date to YYYY-MM-DD |
| admission_id | admission_id | Required unique identifier |
| admission.client_id | admission.client_id | Must reference a validated client |
| program_code | target_program_code | Approved lookup; unknown codes go to review |
| admit_date | admit_date | Required; supported date formats only |
| discharge_date | discharge_date | Optional; cannot precede admission |

These rules are demo choices, not vendor requirements. The first CSV data row
is source row 2, matching ordinary spreadsheet row numbering.

## Workflow and responsibilities

| Stage | Data team | QI / program owner | System / vendor team |
|---|---|---|---|
| Define scope | Inventory extracts, fields, periods | Confirm programs and meaning | Confirm accepted import structure |
| Map | Draft transformation and lookup | Approve code equivalence and workflow decisions | Clarify system constraints |
| Validate | Automated checks and exception report | Review correctness against authorized source | Review technical import constraints |
| Resolve | Apply documented approved corrections | Decide ambiguous record or code meaning | Support unresolved system issues |
| Accept | Reconcile rows and retain evidence | Sign off on reviewed business mappings | Validate import and UAT when performed |

The runnable demo implements automated import preparation only; the review and
signoff process described above remains a case-study design.

## Acceptance evidence

- Every source row belongs to exactly one ready/review partition.
- Ready IDs are nonempty and unique within their tables.
- Every ready admission references a ready client.
- Ready records have valid required dates and mapped programs.
- Review records are traceable to table, source row, and rule.
- Original source files remain unchanged.

## Results

See `outputs/reconciliation.csv` and `outputs/summary.json` for actual fixture
results. Do not interpret count balance as proof of factual accuracy. No speed,
cost, or employer improvement claims are measured by this demo.
