"""Parameter information and exact historical binding; no fitting or responses."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from atlas.study_parameters import validate_parameter_policy
from tools.check_study_parameters import check

ROOT=Path(__file__).resolve().parents[1]
ALLOCATION=ROOT/'studies/kfs-development-v1'
HERE=ALLOCATION/'parameters-v1'

class StudyParameterAccountingTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((HERE/'parameter-policy.json').read_text())
        self.definitions={};self.digests={}
        for record in self.policy['models']:
            content=(HERE/'models'/(record['id']+'.json')).read_bytes()
            self.definitions[record['id']]=json.loads(content)
            self.digests[record['id']]=hashlib.sha256(content).hexdigest()
        self.allocation_hash=hashlib.sha256((ALLOCATION/'allocation.json').read_bytes()).hexdigest()

    def validate(self,policy=None):
        return validate_parameter_policy(policy or self.policy,self.definitions,
            allocation_sha256=self.allocation_hash,definition_sha256=self.digests)

    def test_partial_calibration_information_is_retained(self):
        rows=self.validate()['models'];self.assertEqual([r['fitted_parameter_count'] for r in rows],[2,4,4])
        self.assertEqual(rows[2]['fixed_literature_material_parameters'],['n','ed0','ec0','ei0'])
        self.assertEqual(rows[2]['literature_seeded_fitted_parameters'],['phi','hs','alpha','beta'])
        self.assertEqual(rows[1]['specializations'],['c'])
        self.assertTrue(all(r['numerical_scales']==['p_ref'] for r in rows))

    def test_missing_extra_and_duplicate_accounting_rejected(self):
        for mutation in ['missing','extra','duplicate_model']:
            policy=copy.deepcopy(self.policy)
            if mutation=='missing':policy['models'][2]['parameters'].pop('n')
            elif mutation=='extra':policy['models'][0]['parameters']['unlisted']=policy['models'][0]['parameters']['E']
            else:policy['models'].append(policy['models'][0])
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):self.validate(policy)

    def test_units_bounds_seed_and_fixed_role_cannot_silently_change(self):
        cases=[('unit','kPa'),('bounds',[0,1e15]),('value',1e15),('value',True),('value',float('nan'))]
        for key,value in cases:
            policy=copy.deepcopy(self.policy);policy['models'][0]['parameters']['E'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.validate(policy)
        self.policy['models'][0]['parameters']['p_ref']['bounds']=[1,1e9]
        with self.assertRaises(ValueError):self.validate()

    def test_log_search_cannot_include_zero_and_seed_must_be_in_search_range(self):
        for parameter in [dict(bounds=[0,.4],transform='log'),dict(bounds=[.1,.2])]:
            policy=copy.deepcopy(self.policy);policy['models'][0]['parameters']['nu'].update(parameter)
            with self.subTest(parameter=parameter),self.assertRaises(ValueError):self.validate(policy)

    def test_missing_literature_source_and_false_default_provenance_rejected(self):
        self.policy['models'][2]['parameters']['n']['provenance'].pop('url')
        with self.assertRaisesRegex(ValueError,'URL required'):self.validate()
        policy=copy.deepcopy(self.policy)
        policy['models'][2]['parameters']['n']['provenance']={'kind':'definition_default','locator':'incorrectly relabelled inherited n'}
        with self.assertRaisesRegex(ValueError,'not the declared default'):self.validate(policy)

    def test_definition_and_allocation_identity_required(self):
        self.policy['models'][0]['definition_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'definition identity'):self.validate()
        self.policy['models'][0]['definition_sha256']=self.digests['linear-elastic']
        self.policy['allocation_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'allocation identity'):self.validate()

    def test_changed_snapshot_is_rejected_by_supported_checker(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            for mid,definition in self.definitions.items():(folder/(mid+'.json')).write_text(json.dumps(definition))
            with self.assertRaisesRegex(ValueError,'definition identity'):
                check(HERE/'parameter-policy.json',ALLOCATION/'allocation.json',ALLOCATION/'reservation-policy.json',folder)

    def test_invalid_allocation_stops_before_reading_parameter_or_model_files(self):
        with tempfile.TemporaryDirectory() as temp:
            plan=Path(temp)/'allocation.json';content=json.loads((ALLOCATION/'allocation.json').read_text())
            content['evaluation_ids'].append('KFS-TMD6');plan.write_text(json.dumps(content))
            original=Path.read_bytes;opened=[]
            allowed={plan,ALLOCATION/'reservation-policy.json'}
            def read_bytes(path):
                self.assertIn(path,allowed,'parameter/model opened before allocation rejection')
                opened.append(path);return original(path)
            with patch.object(Path,'read_bytes',read_bytes),self.assertRaisesRegex(ValueError,'reserved'):
                check(HERE/'parameter-policy.json',plan,ALLOCATION/'reservation-policy.json',HERE/'models')
            self.assertCountEqual(opened,allowed)

    def test_checker_has_no_response_file_access(self):
        allowed={HERE/'parameter-policy.json',ALLOCATION/'allocation.json',ALLOCATION/'reservation-policy.json'}
        allowed.update(HERE/'models'/(mid+'.json') for mid in self.definitions)
        original=Path.read_bytes;opened=[]
        def read_bytes(path):
            self.assertIn(path,allowed,'unexpected response or unrelated file access')
            opened.append(path);return original(path)
        with patch.object(Path,'read_bytes',read_bytes):
            self.assertTrue(check(HERE/'parameter-policy.json',ALLOCATION/'allocation.json',ALLOCATION/'reservation-policy.json',HERE/'models')['passed'])
        self.assertEqual(set(opened),allowed)

if __name__=='__main__':unittest.main()
