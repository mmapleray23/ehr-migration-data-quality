"""Create reproducible, entirely fictional fixtures. No source-system data."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def generate(root=ROOT):
    raw = root / 'data/raw'
    ref = root / 'data/reference'
    raw.mkdir(parents=True, exist_ok=True)
    ref.mkdir(parents=True, exist_ok=True)
    clients = pd.DataFrame([
        {'client_id': f'{i:05d}', 'display_name': f' Fictional Client {i:03d} ',
         'dob': '1985-06-15' if i % 2 else '06/15/1985'}
        for i in range(1, 101)
    ])
    clients.loc[4, 'dob'] = 'not-a-date'
    clients.loc[5, 'display_name'] = ''
    clients = pd.concat([clients, clients.iloc[[6]]], ignore_index=True)
    admissions = pd.DataFrame([
        {'admission_id': f'A{i:04d}', 'client_id': f'{(i-1)%100+1:05d}',
         'program_code': ['BH_OLD', 'SUD_OLD', 'ELDER_OLD'][i % 3],
         'admit_date': '01/10/2024' if i % 2 else '2024-01-10',
         'discharge_date': '' if i % 4 == 0 else '2024-03-10'}
        for i in range(1, 201)
    ])
    admissions.loc[9, 'client_id'] = '99999'
    admissions.loc[10, 'program_code'] = 'UNMAPPED'
    admissions.loc[11, 'discharge_date'] = '2023-12-31'
    admissions.loc[12, 'admit_date'] = ''
    admissions.loc[13, 'discharge_date'] = 'bad-date'
    admissions = pd.concat([admissions, admissions.iloc[[14]]], ignore_index=True)
    clients.to_csv(raw / 'clients.csv', index=False)
    admissions.to_csv(raw / 'admissions.csv', index=False)
    pd.DataFrame([
        {'source_code': 'BH_OLD', 'target_code': 'BH01'},
        {'source_code': 'SUD_OLD', 'target_code': 'SU01'},
        {'source_code': 'ELDER_OLD', 'target_code': 'EL01'},
    ]).to_csv(ref / 'program_mapping.csv', index=False)
    print('Created 101 client rows and 201 admission rows. All data is synthetic.')

if __name__ == '__main__':
    generate()
