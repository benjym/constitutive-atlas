"""Synthetic complete-candidate scoring; no experiment files or solver calls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from atlas.study_objective import score_objective
from tools.score_study_objective import check

ROOT = Path(__file__).resolve().parents[1]


class CompleteObjectiveTests(unittest.TestCase):
    def setUp(self):
        self.reservations = {'paper_reservation_version': 1, 'id': 'synthetic-reservations',
            'experiments': [{'id': t, 'role': 'reserved_final' if t == 'R' else 'development'}
                            for t in ['A', 'B', 'E', 'R']]}
        self.rb = json.dumps(self.reservations).encode()
        self.rh = hashlib.sha256(self.rb).hexdigest()
        self.allocation = {'schema_version': '0.1', 'kind': 'whole-test-study-allocation',
            'id': 'synthetic-allocation', 'phase': 'development', 'grouping_unit': 'whole_test',
            'evaluation_claim': 'previously_exposed_development',
            'calibration_packages': {'fit': ['A', 'B']}, 'evaluation_ids': ['E'],
            'reservation_policy': {'id': 'synthetic-reservations', 'sha256': self.rh},
            'limitations': ['Synthetic metadata; no scientific admission.']}
        self.ab = json.dumps(self.allocation).encode()
        self.ah = hashlib.sha256(self.ab).hexdigest()
        self.policy = {'schema_version': '0.1', 'kind': 'study-objective', 'id': 'synthetic-objective',
            'allocation_sha256': self.ah, 'package': 'fit',
            'method': 'piecewise-linear-residual-axial-travel-v1',
            'test_aggregation': 'equal_whole_test', 'failure_policy': 'reject_entire_candidate',
            'channels': {'q': {'unit': 'Pa', 'scale': 2., 'weight': 1.},
                         'volumetric_strain': {'unit': '1', 'scale': .1, 'weight': 3.}}}
        units = {'q': 'Pa', 'volumetric_strain': '1'}
        self.observations = {t: {'units': units.copy(), 'rows': [
            {'axial_strain': 0., 'q': 0., 'volumetric_strain': 0.},
            {'axial_strain': .01, 'q': 0., 'volumetric_strain': 0.}]} for t in ['A', 'B']}
        self.predictions = {t: {'units': units.copy(), 'status': 'success', 'points': [
            {'observation_index': 0, 'axial_strain': 0., 'q': 0., 'volumetric_strain': 0.},
            {'observation_index': 1, 'axial_strain': .01, 'q': q, 'volumetric_strain': .1}]}
            for t, q in [('A', 2.), ('B', 4.)]}

    def score(self):
        return score_objective(self.policy, self.allocation, self.reservations,
            self.observations, self.predictions, allocation_sha256=self.ah, reservation_sha256=self.rh)

    def write_inputs(self, folder):
        records = {'policy': json.dumps(self.policy).encode(), 'allocation': self.ab,
                   'reservations': self.rb, 'observations': json.dumps(self.observations).encode(),
                   'predictions': json.dumps(self.predictions).encode()}
        paths = {k: folder / (k + '.json') for k in records}
        for k, b in records.items(): paths[k].write_bytes(b)
        return paths

    def test_exact_weighted_analytic_objective_and_no_mutation(self):
        before = copy.deepcopy((self.policy, self.observations, self.predictions))
        report = self.score()
        # A=(1/4)*(1/3)+(3/4)*(1/3); B=(1/4)*(4/3)+(3/4)*(1/3).
        self.assertAlmostEqual(report['objective'], 11/24)
        self.assertEqual([t['id'] for t in report['tests']], ['A', 'B'])
        self.assertFalse(report['scientific_admission'])
        self.assertEqual(before, (self.policy, self.observations, self.predictions))

    def test_redundant_sampling_does_not_change_whole_test_weight(self):
        expected = self.score()['objective']
        self.observations['A']['rows'].insert(1, {'axial_strain': .005, 'q': 0., 'volumetric_strain': 0.})
        self.predictions['A']['points'].insert(1, {'observation_index': 1, 'axial_strain': .005, 'q': 1., 'volumetric_strain': .05})
        self.predictions['A']['points'][2]['observation_index'] = 2
        self.assertAlmostEqual(self.score()['objective'], expected)

    def test_missing_extra_evaluation_and_reserved_tests_reject(self):
        for tid in ['E', 'R', 'unknown']:
            with self.subTest(tid=tid):
                self.predictions[tid] = self.predictions['A']
                with self.assertRaisesRegex(ValueError, 'exactly'): self.score()
                del self.predictions[tid]
        del self.observations['B']
        with self.assertRaisesRegex(ValueError, 'exactly'): self.score()

    def test_failure_truncation_and_reordering_never_score_successful_prefix(self):
        good = copy.deepcopy(self.predictions['B'])
        for bad in ['status', 'truncated', 'index', 'coordinate', 'nonfinite']:
            self.predictions['B'] = copy.deepcopy(good)
            p = self.predictions['B']
            if bad == 'status': p['status'] = 'failed'
            if bad == 'truncated': p['points'].pop()
            if bad == 'index': p['points'][1]['observation_index'] = 0
            if bad == 'coordinate': p['points'][1]['axial_strain'] = .02
            if bad == 'nonfinite': p['points'][1]['q'] = float('nan')
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'B/q'): self.score()

    def test_unit_and_policy_mutations_reject(self):
        baseline = copy.deepcopy(self.policy)
        for key, value in [('allocation_sha256', '0'*64), ('package', 'evaluation'),
                           ('method', 'historical-trapezoid'), ('test_aggregation', 'pooled_rows'),
                           ('failure_policy', 'drop_failed_tests')]:
            self.policy = copy.deepcopy(baseline); self.policy[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.score()
        self.policy = baseline
        self.predictions['A']['units']['q'] = 'kPa'
        with self.assertRaisesRegex(ValueError, 'units'): self.score()

    def test_bad_scales_weights_channels_and_numeric_overflow_reject(self):
        for key, val in [('scale', 0), ('scale', True), ('scale', float('inf')),
                         ('weight', -1), ('weight', float('nan'))]:
            old = self.policy['channels']['q'][key]; self.policy['channels']['q'][key] = val
            with self.subTest(key=key, val=val), self.assertRaises(ValueError): self.score()
            self.policy['channels']['q'][key] = old
        self.policy['channels']['axial_strain'] = self.policy['channels']['q']
        with self.assertRaisesRegex(ValueError, 'channel'): self.score()
        del self.policy['channels']['axial_strain']
        self.predictions['B']['points'][1]['q'] = 1e308
        with self.assertRaises(ValueError): self.score()

    def test_metadata_rejection_precedes_response_file_access(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.write_inputs(Path(d))
            bad = copy.deepcopy(self.allocation); bad['evaluation_ids'].append('R')
            paths['allocation'].write_text(json.dumps(bad))
            original = Path.read_bytes; opened = []
            def read(path):
                self.assertNotIn(path, [paths['observations'], paths['predictions']])
                opened.append(path); return original(path)
            with patch.object(Path, 'read_bytes', read), self.assertRaisesRegex(ValueError, 'reserved'):
                check(**paths)
            self.assertEqual(len(opened), 3)

    def test_cli_strict_json_failure_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); paths = self.write_inputs(folder); output = folder/'report.json'
            cmd = [sys.executable, '-B', str(ROOT/'tools/score_study_objective.py')]
            for k, path in paths.items(): cmd += ['--'+k, str(path)]
            cmd += ['--output', str(output)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            report = json.loads(output.read_text())
            self.assertAlmostEqual(report['objective'], 11/24)
            for k, path in paths.items():
                self.assertEqual(report['input_sha256'][k if k != 'policy' else 'objective'], hashlib.sha256(path.read_bytes()).hexdigest())
            original = output.read_bytes()
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), original)
            output.unlink(); paths['predictions'].write_text('{"A":{},"A":{}}')
            failed = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(failed.returncode, 0); self.assertFalse(output.exists())

if __name__ == '__main__': unittest.main()
