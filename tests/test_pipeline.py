import unittest
import pandas as pd
from src.pipeline import validate

class ValidationTests(unittest.TestCase):
    def fixtures(self):
        c = pd.DataFrame([{'client_id':'00001', 'display_name':' Fictional ', 'dob':'06/15/1985'}])
        a = pd.DataFrame([{'admission_id':'A1', 'client_id':'00001', 'program_code':'OLD',
                           'admit_date':'01/10/2024', 'discharge_date':''}])
        m = pd.DataFrame([{'source_code':'OLD','target_code':'NEW'}])
        return c, a, m

    def test_valid_open_admission_and_leading_zero(self):
        r = validate(*self.fixtures())
        self.assertEqual(r['clients_ready'].iloc[0]['client_id'], '00001')
        self.assertEqual(r['clients_ready'].iloc[0]['dob'], '1985-06-15')
        self.assertEqual(r['admissions_ready'].iloc[0]['target_program_code'], 'NEW')
        self.assertTrue(r['exceptions'].empty)

    def test_duplicate_client_blocks_dependent_admission(self):
        c,a,m = self.fixtures()
        r = validate(pd.concat([c,c], ignore_index=True), a, m)
        self.assertEqual(len(r['clients_review']), 2)
        self.assertEqual(len(r['admissions_ready']), 0)
        self.assertIn('client_not_ready', set(r['exceptions']['rule']))
        self.assertTrue(r['reconciliation']['balanced'].all())

    def test_orphan_mapping_and_date_order(self):
        c,a,m = self.fixtures()
        a.loc[0, ['client_id','program_code','discharge_date']] = ['99999','UNKNOWN','2023-01-01']
        r = validate(c,a,m)
        self.assertEqual(set(r['exceptions']['rule']), {'orphan_client','unmapped_program','date_order'})
        self.assertEqual(len(r['admissions_review']), 1)

    def test_conflicting_mapping_stops_pipeline(self):
        c,a,m = self.fixtures()
        with self.assertRaises(ValueError):
            validate(c,a,pd.concat([m,m], ignore_index=True))

    def test_missing_schema_stops_pipeline(self):
        c,a,m = self.fixtures()
        with self.assertRaises(ValueError):
            validate(c.drop(columns='dob'),a,m)

    def test_invalid_discharge_is_not_treated_as_open(self):
        c,a,m = self.fixtures()
        a.loc[0,'discharge_date'] = 'bad-date'
        r = validate(c,a,m)
        self.assertEqual(len(r['admissions_ready']),0)
        self.assertIn('invalid_date', set(r['exceptions']['rule']))

if __name__ == '__main__':
    unittest.main()
