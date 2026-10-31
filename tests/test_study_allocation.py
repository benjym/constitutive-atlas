"""Scientific leakage and reservation checks without measured response access."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from atlas.study_allocation import validate_allocation
from tools.check_study_allocation import check, main

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'studies/kfs-development-v1'

class WholeTestAllocationTests(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((STUDY/'allocation.json').read_text())
        self.content=(STUDY/'reservation-policy.json').read_bytes()
        self.policy=json.loads(self.content)
        self.digest=hashlib.sha256(self.content).hexdigest()

    def validate(self):
        return validate_allocation(self.plan,self.policy,policy_sha256=self.digest)

    def test_development_frame_preserves_shared_calibration_test_across_packages(self):
        result=self.validate()
        self.assertEqual(result['calibration_package_sizes'],{'pressure3':3,'density3':3})
        self.assertEqual(len(result['calibration_union_ids']),5)
        self.assertEqual(len(result['evaluation_ids']),6)
        self.assertEqual(len(result['reserved_ids_excluded']),14)
        self.assertFalse(result['final_evaluation_release'])
        self.assertEqual(result['evaluation_claim'],'previously_exposed_development')

    def test_overlap_in_any_calibration_package_is_rejected(self):
        for package in self.plan['calibration_packages']:
            plan=copy.deepcopy(self.plan)
            plan['calibration_packages'][package].append(plan['evaluation_ids'][0])
            with self.subTest(package=package),self.assertRaisesRegex(ValueError,'whole-test overlap'):
                validate_allocation(plan,self.policy,policy_sha256=self.digest)

    def test_reserved_and_unknown_aliases_cannot_enter_either_role(self):
        for identifier,reason in [('KFS-TMD6','reserved'),('KFS-TMD02','unknown'),('kfs-tmd2','unknown')]:
            for role in ['calibration','evaluation']:
                plan=copy.deepcopy(self.plan)
                (plan['evaluation_ids'] if role=='evaluation' else plan['calibration_packages']['pressure3']).append(identifier)
                with self.subTest(identifier=identifier,role=role),self.assertRaisesRegex(ValueError,reason):
                    validate_allocation(plan,self.policy,policy_sha256=self.digest)

    def test_ambiguous_duplicate_assignments_and_policy_ids_rejected(self):
        self.plan['evaluation_ids'].append(self.plan['evaluation_ids'][0])
        with self.assertRaisesRegex(ValueError,'duplicate whole-test'):self.validate()
        self.setUp()
        self.plan['calibration_packages']['pressure3'].append('KFS-TMD2')
        with self.assertRaisesRegex(ValueError,'duplicate whole-test'):self.validate()
        self.setUp()
        self.policy['experiments'].append(dict(self.policy['experiments'][0],role='reserved_final'))
        with self.assertRaisesRegex(ValueError,'duplicate reservation'):self.validate()

    def test_changed_policy_bytes_or_identity_do_not_carry_over_binding(self):
        with self.assertRaisesRegex(ValueError,'bytes changed'):
            validate_allocation(self.plan,self.policy,policy_sha256=hashlib.sha256(self.content+b'\n').hexdigest())
        self.policy['id']='other-policy'
        with self.assertRaisesRegex(ValueError,'identity mismatch'):self.validate()

    def test_sample_selectors_and_unproven_final_or_blind_claims_rejected(self):
        for key,value in [('grouping_unit','row'),('phase','final'),('evaluation_claim','blind'),('rows',[0,1])]:
            plan=copy.deepcopy(self.plan);plan[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_allocation(plan,self.policy,policy_sha256=self.digest)

    def test_supported_checker_reads_only_two_metadata_files(self):
        allowed={STUDY/'allocation.json',STUDY/'reservation-policy.json'}
        original=Path.read_bytes;opened=[]
        def read_bytes(path):
            self.assertIn(path,allowed,'response or unrelated file access')
            opened.append(path)
            return original(path)
        with patch.object(Path,'read_bytes',read_bytes):
            self.assertTrue(check(STUDY/'allocation.json',STUDY/'reservation-policy.json')['passed'])
        self.assertCountEqual(opened,allowed)

    def test_serialized_duplicate_roles_and_nonfinite_extras_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            policy=Path(temp)/'policy.json'
            for content in [self.content.replace(b'"role": "development"',b'"role":"reserved_final","role":"development"',1),b'{"unused":1e999}']:
                policy.write_bytes(content)
                with self.subTest(content=content[:35]),self.assertRaises(ValueError):
                    check(STUDY/'allocation.json',policy)

    def test_cli_returns_nonzero_without_a_success_report_for_reserved_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            plan=Path(temp)/'allocation.json';output=Path(temp)/'result.json'
            self.plan['evaluation_ids'].append('KFS-TMD6');plan.write_text(json.dumps(self.plan))
            argv=['check-study-allocation',str(plan),'--policy',str(STUDY/'reservation-policy.json'),'--output',str(output)]
            with patch('sys.argv',argv),contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(main(),1)
            self.assertIn('reserved',errors.getvalue())
            self.assertFalse(output.exists())

if __name__=='__main__':unittest.main()
