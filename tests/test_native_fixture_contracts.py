"""Current13 failure contract rejects accidental successes and altered failures."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from tools.check_native_fixture_contracts import check_contract, check_observation

ROOT = Path(__file__).resolve().parents[1]


class NativeFixtureContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / 'catalogue/native-fixture-contracts-thirteen-occ-v1.json').read_text())
        self.policy = json.loads((ROOT / 'catalogue/laboratory-package-policy.json').read_text())

    def test_closed_identity_and_case_set(self):
        check_contract(self.contract, self.policy)
        for change in ('models', 'cases', 'returncode'):
            bad = copy.deepcopy(self.contract)
            if change == 'models':
                bad['models'].pop(next(iter(bad['models'])))
            elif change == 'cases':
                bad['cases'][0] = bad['cases'][1]
            else:
                bad['cases'][0]['returncode'] = 0
            with self.assertRaises(AssertionError):
                check_contract(bad, self.policy)

    def test_original_occ_failure_cannot_be_success_or_different_failure(self):
        case = self.contract['cases'][2]
        stderr = ('failed knot 1 residual 0.00086977407608239442 trials 1 de0 0.0001 de1 0\n'
                  'drained replay failed: original-cam-clay-sw-electronic-log-recovery-v1 singular mixed-control system; last committed knot retained\n')
        valid = SimpleNamespace(returncode=1, stdout=case['stdout'], stderr=stderr)
        check_observation(case, valid)
        changes = [dict(returncode=0), dict(stdout=''), dict(stderr=stderr+'extra\n'),
                   dict(stderr=stderr.replace('0.00086977407608239442', '0')),
                   dict(stderr=stderr.replace('knot 1', 'knot 2')),
                   dict(stderr=stderr.replace('trials 1', 'trials 2')),
                   dict(stderr=stderr.replace('last committed knot retained', 'state changed'))]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(AssertionError):
                check_observation(case, SimpleNamespace(**(vars(valid) | change)))

    def test_both_unknown_profiles_reject_exactly(self):
        for case in self.contract['cases']:
            if case['profile'] != 'unknown':
                continue
            valid = SimpleNamespace(returncode=1, stdout='', stderr=case['stderr'])
            check_observation(case, valid)
            with self.assertRaises(AssertionError):
                check_observation(case, SimpleNamespace(returncode=0, stdout='', stderr=''))
