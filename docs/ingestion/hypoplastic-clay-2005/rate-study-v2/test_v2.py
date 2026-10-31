import copy
from decimal import Decimal,localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from atlas.model import load,defaults,evaluation_environment
from atlas.compiler import generate
import check_study
import reference
import support

HERE=Path(__file__).resolve().parent


class RevisionV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(os.environ['ATLAS_REPO']) if 'ATLAS_REPO'in os.environ else next((r for r in HERE.parents if(r/'atlas/model.py').is_file()),None)
        if cls.repo is None:raise RuntimeError('ATLAS_REPO required for staged historical comparison')
        cls.old=cls.repo/'docs/ingestion/hypoplastic-clay-2005/rate-study-v1'
        cls.model=load(HERE/'model.json')

    def test_historical_bytes_and_all41_rate_outputs_preserved(self):
        protocol=json.loads((HERE/'protocol.json').read_text())
        for name,digest in protocol['historical_pins'].items():
            self.assertEqual(hashlib.sha256((self.old/name).read_bytes()).hexdigest(),digest)
        self.assertEqual((HERE/'invalid-cases.json').read_bytes(),(self.old/'invalid-cases.json').read_bytes())
        old=json.loads((self.old/'reference.json').read_text())['cases']
        new=reference.build_reference()['cases']
        self.assertEqual(old,new)

    def test_only_separate_support_changed_in_draft_algebra(self):
        old=json.loads((self.old/'model.json').read_text())
        self.assertEqual(self.model['parameters'],old['parameters'])
        self.assertEqual(self.model['state'],old['state'])
        self.assertEqual(self.model['equations'],old['equations'])
        self.assertEqual([d for d in self.model['derived']if not d['name'].startswith('support_')],old['derived'])
        self.assertEqual(self.model['domain'][6:],old['domain'])
        self.assertIn('Eq38 has PLUS',self.model['description'])
        self.assertEqual(self.model['status'],'draft')

    def test_separate_decimal_support_refinement29cases(self):
        ref=support.build_support_reference()
        self.assertEqual(ref,json.loads((HERE/'support-reference.json').read_text()))
        self.assertEqual(len(ref['cases']),29)
        for c in ref['cases']:
            self.assertIs(c['oracle80']['ideal_arithmetic_support_accepts'],c['oracle120']['ideal_arithmetic_support_accepts'])
        by={c['id']:c for c in ref['cases']}
        self.assertTrue(by['tiny-positive-excluded']['oracle120']['actual_mandel_cartesian_spd'])
        self.assertFalse(by['tiny-positive-excluded']['expected_accepted'])
        self.assertTrue(by['tiny-positive-interior']['expected_accepted'])
        self.assertFalse(by['negative-eigenvalue']['oracle120']['actual_mandel_cartesian_spd'])
        self.assertFalse(by['rank-loss']['oracle120']['actual_mandel_cartesian_spd'])
        self.assertTrue(by['margin-above']['expected_accepted'])
        self.assertFalse(by['margin-below']['expected_accepted'])

    def test_repaired_guard_and_adversarial_shear_and_rotations(self):
        result=check_study.assess(self.repo)
        self.assertEqual(len(result['support_cases']),29)
        self.assertEqual(len(result['rate_cases']),41)
        self.assertEqual(len(result['historical_invalids']),10)
        for row in result['support_cases']:
            for backend in ['draft','cartesian']:
                self.assertIs(row['results'][backend]['accepted'],row['expected_accepted'])
        self.assertFalse(result['compiled_execution'])
        self.assertIn('support-only cases do not certify near-singular rate accuracy',result['limitations'])

    def test_research_guard_is_scale_independent_for_retained_witnesses(self):
        inp=json.loads((HERE/'support-inputs.json').read_text())['cases']
        for c in inp:
            if not c['id'].startswith('scaled-'):continue
            diag=support.diagnostics(c)
            self.assertIs(diag['ideal_arithmetic_support_accepts'],c['expected_accepted'])

    def test_reference_forgery_bool_alias_missing_and_duplicate_rejected(self):
        rate,sup=check_study.fresh_references()
        bad=copy.deepcopy(rate);bad['cases'][0]['expected'][0]+=1.
        with self.assertRaises(ValueError):check_study.fresh_references(bad,sup)
        bad=copy.deepcopy(rate);bad['zero_spin']=1
        with self.assertRaises(ValueError):check_study.fresh_references(bad,sup)
        bad=copy.deepcopy(rate);bad['cases'].pop()
        with self.assertRaises(ValueError):check_study.fresh_references(bad,sup)
        bad=copy.deepcopy(sup);bad['cases'][1]=copy.deepcopy(bad['cases'][0])
        with self.assertRaises(ValueError):check_study.fresh_references(rate,bad)
        bad=copy.deepcopy(sup);bad['cases'][0]['oracle120']['ideal_arithmetic_support_accepts']=1
        with self.assertRaises(ValueError):check_study.fresh_references(rate,bad)

    def test_retained_guard_arithmetic_error_is_small_relative_to_margin(self):
        observed=check_study.assess(self.repo)
        oracle={x['id']:x for x in support.build_support_reference()['cases']}
        with localcontext()as context:
            context.prec=150
            for row in observed['support_cases']:
                target=Decimal(oracle[row['id']]['oracle120']['normalized_det_decimal'])
                value=Decimal.from_float(row['computed_guard']['support_det'])
                self.assertLess(abs(target-value),support.MARGIN/100)
        # Empirical retained-set diagnostic, not an errorbound for arbitrary tensors.

    def test_common_schema_cpp_generation_only(self):
        with tempfile.TemporaryDirectory()as tmp:
            generate(tmp,[HERE/'model.json'])
            text=(Path(tmp)/'models.hpp').read_text()
            self.assertIn('support_det',text)
            self.assertIn('hypoplastic-clay-2005-appc-plus-spd-interior-v2-research',text)
            self.assertNotIn('barodesy',text)

if __name__=='__main__':unittest.main()
