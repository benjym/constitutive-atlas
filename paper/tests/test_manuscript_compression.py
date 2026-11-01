"""Prevent development tables from losing their fixed-baseline provenance."""
import itertools
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analysis.common import ROOT, digest, read_json, write_json
from plot_compression_sensitivity import load_checked_report
from run_compression_sensitivity import summarize


class ManuscriptCompressionIntegrityTests(unittest.TestCase):
    def fixture(self, directory):
        config = read_json(ROOT/'paper/study/compression_sensitivity.json')
        models = {mid: read_json(ROOT/'models'/f'{mid}.json') for mid in config['model_ids']}
        parameters = {mid: {name: p['default'] for name, p in model['parameters'].items()}
                      for mid, model in models.items()}
        for mid, model in models.items():
            write_json(directory/'models'/f'{mid}.json', model)
        solver = directory/'solver/atlas_solver'
        solver.parent.mkdir()
        # The reader checks provenance only; adapter physics has separate tests.
        solver.write_text('nonexecuted checksum fixture')
        model_hashes = {mid: digest(directory/'models'/f'{mid}.json') for mid in models}
        baseline_path = directory/'inputs'/config['baseline_report']
        write_json(baseline_path, dict(solver_sha256=digest(solver), model_sha256=model_hashes,
            config=dict(models=[dict(id=mid, baseline_parameters=p) for mid, p in parameters.items()])))
        records = []
        for mid, ratio, coordinate, spacing in itertools.product(config['model_ids'],
                config['initial_radial_to_axial_stress_ratios'], config['coordinates'], config['maximum_increments']):
            points = [dict(observation_index=i, imposed_axial_coordinate=x,
                           axial_stress=1000+x*1e7, void_ratio=1.8*math.exp(-x)-1)
                      for i, x in enumerate([0., .01])]
            records.append(dict(experiment_id='synthetic', model_id=mid, minimum_stress_Pa=1000,
                parameters=parameters[mid], initial_stress_ratio=ratio, coordinate=coordinate,
                maximum_increment=spacing, source_lines=[4, 5], initial_void_ratio=.8,
                prediction=dict(status='success', points=points)))
        report = dict(kind='fixed_parameter_oedometer_initialization_development_diagnostic',
            input_integrity='verified', config=config, solver_sha256=digest(solver), model_sha256=model_hashes,
            input_sha256={config['baseline_report']: digest(baseline_path)},
            protocol=dict(experiment_ids=['synthetic'], minimum_axial_stresses_Pa=[1000]),
            records=records, summary=summarize(records, config))
        path = directory/'report.json'
        write_json(path, report)
        return path, report

    def test_fixed_baseline_report_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path, report = self.fixture(Path(folder))
            self.assertEqual(load_checked_report(path), report)

    def test_changed_archived_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path, report = self.fixture(Path(folder))
            (path.parent/'inputs'/report['config']['baseline_report']).write_text('{}')
            with self.assertRaisesRegex(ValueError, 'archived input'):
                load_checked_report(path)

    def test_different_constants_cannot_be_presented_as_fixed_baseline(self):
        with tempfile.TemporaryDirectory() as folder:
            path, report = self.fixture(Path(folder))
            report['records'][0]['parameters'] = dict(report['records'][0]['parameters'], E=12345)
            write_json(path, report)
            with self.assertRaisesRegex(ValueError, 'fixed baseline constants'):
                load_checked_report(path)

    def test_stale_summary_and_absent_whole_threshold_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path, report = self.fixture(Path(folder))
            original = report['summary'][0]['maximum_coordinate_scenario_difference_Pa']
            report['summary'][0]['maximum_coordinate_scenario_difference_Pa'] = original+1
            write_json(path, report)
            with self.assertRaisesRegex(ValueError, 'recomputed'):
                load_checked_report(path)
            report['summary'][0]['maximum_coordinate_scenario_difference_Pa'] = original
            report['protocol']['minimum_axial_stresses_Pa'].append(5000)
            write_json(path, report)
            with self.assertRaisesRegex(ValueError, 'missing scheduled'):
                load_checked_report(path)


if __name__ == '__main__':
    unittest.main()
