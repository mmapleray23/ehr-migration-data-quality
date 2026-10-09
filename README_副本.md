# EHR Migration & Data Quality Pipeline

**Author:** Min Gao  
**Status:** Runnable learning starter; synthetic demonstration.  
**Scope:** Data preparation, transformation, validation, and reconciliation before import.

This project demonstrates how demographic and admission data can be prepared for
an EHR migration. The scenario is informed by my healthcare data and implementation
work, including Avatar-to-Credible import preparation. All fixtures are fictional;
the target schema is generic and is not an official vendor import format. There is
no connection to either EHR, no production import, and no clinical decision-making.

## Business problem

An EHR transition requires consistent identifiers, dates, program codes, and
relationships. Formatting a spreadsheet alone does not establish that the data
is ready. This demo separates records that satisfy defined rules from records
requiring review, retaining an auditable source-row reference.

## Run locally

Use Python 3.11 or 3.12. From this project's root folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.pipeline
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

Input fixtures are included. To reset them after experimenting:

```bash
python -m src.generate_data
```

The generator replaces the three fixture files. Keep edits in a separate branch
or commit before resetting if you want to preserve your exercises.

## Pipeline

1. Check source schemas; read every ID as text to preserve leading zeros.
2. Trim whitespace and normalize explicitly supported date formats.
3. Validate demographic records and quarantine ambiguous duplicate IDs.
4. Map program codes and validate admission dates and client dependencies.
5. Export ready/review partitions, exceptions, and count reconciliation.

Duplicate IDs quarantine **all** affected rows; the demo does not guess which
record is correct. A blank discharge date represents an open admission and is
allowed. An invalid nonblank discharge date is flagged. Admissions linked to a
client that failed validation are held for review. The demo does not merge people
or modify clinical meaning automatically.

## Files

| Path | Purpose |
|---|---|
| `src/generate_data.py` | Reproducible fictional fixtures with deliberate errors |
| `src/pipeline.py` | Shared validation engine and CSV export command |
| `app.py` | Streamlit demo with a validation button, charts, filters, downloads |
| `data/raw/` | Fictional demographic and admission inputs |
| `data/reference/program_mapping.csv` | Generic program-code mapping |
| `outputs/` | Reproducible sample results |
| `tests/test_pipeline.py` | Behavioral checks for critical failure cases |
| `docs/case-study.md` | Implementation scope, responsibilities, acceptance criteria |
| `docs/learning-guide-zh.md` | Step-by-step Mac tutorial and exercises |

## Outputs and interpretation

`clients_ready.csv` and `admissions_ready.csv` contain normalized records passing
the rules. Corresponding `*_review.csv` files retain source-row references for
blocked records; raw inputs remain unchanged. `exceptions.csv` contains one row
per violated rule, so its row count can exceed the number of blocked records.
`reconciliation.csv` checks **input rows = ready rows + review rows** for each
table. `summary.json` reports measured results for the fixtures.

These are fixture outcomes, not employer outcomes or production performance.
Inspect the actual output after changes instead of retaining outdated numbers.

## Limitations

Rule compliance and row reconciliation do not prove factual correctness or
successful vendor import. Real acceptance would additionally require authorized
source-to-target review, approved mappings, vendor validation, and import/UAT.
This small in-memory demo does not implement access control, production logging,
large-scale processing, a database, or ML. The app only uses bundled synthetic
fixtures and deliberately has no patient-data upload feature.

## Learning ownership

This starter was prepared with AI assistance. Before presenting it in an
interview, I will understand the code, independently add and test rules, and
document those changes. The starter code is distinct from my employer's systems
and my professional accomplishments.

## Next milestones

- Add a future-DOB rule with an injected reference date and a meaningful test.
- Add a program-by-month reconciliation report.
- Add a documented SQLite staging layer.
- Publish the synthetic Streamlit demo and add its verified URL to my portfolio.

## References

- https://docs.streamlit.io/get-started/installation/command-line
- https://pandas.pydata.org/docs/user_guide/io.html
- https://docs.github.com/en/desktop/adding-and-cloning-repositories
