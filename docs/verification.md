# Starter verification

Verified in the preparation environment with Python 3.12, pandas 2.2.3 and
Streamlit 1.65.0. This does not verify the learner's Mac or a cloud deployment.

- Six validation behavior tests passed.
- Every source row appears exactly once across its ready/review partitions.
- Ready admission references are a subset of ready client IDs.
- Streamlit AppTest passed startup, button click, metric values, and rule filter.
- Client fixture: 101 input = 97 ready + 4 review.
- Admission fixture: 201 input = 188 ready + 13 review.
- 17 rule violations and 17 review rows in these fixtures; these counts need not
  be equal for other data (a row can violate multiple rules).
- Downloads are generated from the validated dataframes; no manual browser or
  public deployment verification was performed.
