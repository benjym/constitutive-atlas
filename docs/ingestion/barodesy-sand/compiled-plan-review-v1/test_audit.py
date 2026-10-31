import copy
import json
import os
from pathlib import Path
import unittest
import audit

ROOT=Path(os.environ.get('ATLAS_REVIEW_REPO','/Users/bmar5496/code/constitutive-atlas'))
class ProspectiveAudit(unittest.TestCase):
    def setUp(self):self.p=json.loads((ROOT/audit.STUDY/'protocol.json').read_text())
    def reject(self,p):
        with self.assertRaises(ValueError):audit.audit(ROOT,p,fresh=False)
    def test_fresh_mapping(self):self.assertEqual(audit.audit(ROOT)['total_rows_per_backend'],71)
    def test_swapped_parameter_slots(self):
        xs=self.p['cases'][0]['args'][1].split(',');xs[0],xs[1]=xs[1],xs[0];self.p['cases'][0]['args'][1]=','.join(xs);self.reject(self.p)
    def test_swapped_mandel_channels(self):
        xs=self.p['cases'][0]['args'][2].split(',');xs[3],xs[4]=xs[4],xs[3];self.p['cases'][0]['args'][2]=','.join(xs);self.reject(self.p)
    def test_forged_reference_and_budget(self):
        for key in ['values','absolute_budgets','parity_budgets']:
            p=copy.deepcopy(self.p);p['cases'][0]['expectation'][key][0]+=1;self.reject(p)
    def test_bool_alias_reference(self):
        row=next(x for x in self.p['cases']if x['id']=='valid:zero');row['expectation']['values'][0]=False;self.reject(self.p)
    def test_missing_reject_or_recovery(self):
        for i in [38,39]:
            p=copy.deepcopy(self.p);del p['cases'][i];self.reject(p)
    def test_wrong_recovery(self):
        self.p['cases'][39]['args']=copy.deepcopy(self.p['cases'][1]['args']);self.reject(self.p)
    def test_pin_missing_or_corrupt(self):
        for change in ['missing','corrupt']:
            p=copy.deepcopy(self.p)
            if change=='missing':del p['files']['atlas/compiler.py']
            else:p['files']['atlas/compiler.py']='0'*64
            self.reject(p)

if __name__=='__main__':unittest.main()
