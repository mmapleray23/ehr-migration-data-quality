"""Import-preparation demo: preserve every row and quarantine ambiguous data."""
import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    'clients': ['client_id', 'display_name', 'dob'],
    'admissions': ['admission_id', 'client_id', 'program_code', 'admit_date', 'discharge_date'],
    'mapping': ['source_code', 'target_code'],
}
EXCEPTION_COLUMNS = ['table', 'source_row', 'record_id', 'rule', 'detail']

def parse_date(value):
    """Explicit formats avoid locale-dependent date guesses."""
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None

def read_table(path, name):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = set(SCHEMAS[name]) - set(df.columns)
    if missing:
        raise ValueError(f'{name}: missing columns {sorted(missing)}')
    return df[SCHEMAS[name]].copy()

def validate(clients, admissions, mapping):
    frames = {'clients': clients.copy(), 'admissions': admissions.copy(), 'mapping': mapping.copy()}
    for name, df in frames.items():
        missing = set(SCHEMAS[name]) - set(df.columns)
        if missing:
            raise ValueError(f'{name}: missing columns {sorted(missing)}')
        for col in SCHEMAS[name]:
            df[col] = df[col].fillna('').astype(str).str.strip()
        df['source_row'] = range(2, len(df) + 2)
    c, a, m = frames['clients'], frames['admissions'], frames['mapping']
    if (m['source_code'].eq('').any() or m['target_code'].eq('').any()
            or m['source_code'].duplicated().any()):
        raise ValueError('Mapping must have unique nonempty source codes and nonempty targets.')
    lookup = dict(zip(m['source_code'], m['target_code']))
    errors = []
    blocked = {'clients': set(), 'admissions': set()}

    def flag(table, idx, rule, detail):
        df = frames[table]
        id_col = 'client_id' if table == 'clients' else 'admission_id'
        errors.append({'table': table, 'source_row': int(df.at[idx, 'source_row']),
                       'record_id': df.at[idx, id_col], 'rule': rule, 'detail': detail})
        blocked[table].add(idx)

    for table, id_col in [('clients', 'client_id'), ('admissions', 'admission_id')]:
        df = frames[table]
        for idx in df.index[df[id_col].duplicated(keep=False) & df[id_col].ne('')]:
            flag(table, idx, 'duplicate_id', 'All rows sharing this ID require review.')

    for idx, row in c.iterrows():
        for col in SCHEMAS['clients']:
            if not row[col]:
                flag('clients', idx, 'required_missing', col)
        date = parse_date(row['dob'])
        if row['dob'] and date is None:
            flag('clients', idx, 'invalid_date', 'dob')
        c.at[idx, 'dob'] = date or ''

    valid_client_ids = set(c.loc[~c.index.isin(blocked['clients']), 'client_id'])
    source_client_ids = set(c['client_id'])
    for idx, row in a.iterrows():
        for col in ['admission_id', 'client_id', 'program_code', 'admit_date']:
            if not row[col]:
                flag('admissions', idx, 'required_missing', col)
        if row['client_id'] and row['client_id'] not in valid_client_ids:
            rule = 'client_not_ready' if row['client_id'] in source_client_ids else 'orphan_client'
            flag('admissions', idx, rule, 'Client must pass validation before admission export.')
        target = lookup.get(row['program_code'], '')
        if row['program_code'] and not target:
            flag('admissions', idx, 'unmapped_program', row['program_code'])
        a.at[idx, 'target_program_code'] = target
        admit = parse_date(row['admit_date'])
        discharge = parse_date(row['discharge_date']) if row['discharge_date'] else None
        if row['admit_date'] and admit is None:
            flag('admissions', idx, 'invalid_date', 'admit_date')
        if row['discharge_date'] and discharge is None:
            flag('admissions', idx, 'invalid_date', 'discharge_date')
        if admit and discharge and discharge < admit:
            flag('admissions', idx, 'date_order', 'Discharge precedes admission.')
        a.at[idx, 'admit_date'] = admit or ''
        a.at[idx, 'discharge_date'] = discharge or ''

    result = {}
    reconciliation = []
    for table in ('clients', 'admissions'):
        df = frames[table]
        mask = df.index.isin(blocked[table])
        result[f'{table}_ready'] = df.loc[~mask].copy()
        result[f'{table}_review'] = df.loc[mask].copy()
        reconciliation.append({'table': table, 'input_rows': len(df),
                               'ready_rows': int((~mask).sum()), 'review_rows': int(mask.sum()),
                               'balanced': len(df) == int((~mask).sum()) + int(mask.sum())})
    result['exceptions'] = pd.DataFrame(errors, columns=EXCEPTION_COLUMNS)
    result['reconciliation'] = pd.DataFrame(reconciliation)
    counts = Counter(e['rule'] for e in errors)
    result['summary'] = {'synthetic_demo': True, 'scope': 'Import preparation only',
                         'rule_violations': len(errors), 'rules': dict(sorted(counts.items())),
                         'tables': reconciliation}
    return result

def run(root=ROOT):
    result = validate(read_table(root/'data/raw/clients.csv', 'clients'),
                      read_table(root/'data/raw/admissions.csv', 'admissions'),
                      read_table(root/'data/reference/program_mapping.csv', 'mapping'))
    out = root / 'outputs'
    out.mkdir(exist_ok=True)
    for name, frame in result.items():
        if isinstance(frame, pd.DataFrame):
            frame.to_csv(out / f'{name}.csv', index=False)
    (out / 'summary.json').write_text(json.dumps(result['summary'], indent=2) + '\n')
    print(result['reconciliation'].to_string(index=False))
    print(f"Rule violations: {result['summary']['rule_violations']} (a row may have several)")
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    run(parser.parse_args().root)
