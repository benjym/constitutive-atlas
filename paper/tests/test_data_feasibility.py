import unittest
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.data_feasibility import classify


class FeasibilityTests(unittest.TestCase):
    def record(self):
        return dict(kind='experiment', protocol='drained-triaxial',
                    initial=dict(effective_stress=[100000]*3+[0]*3, void_ratio=.7),
                    rows=[dict(axial_strain=0, q=0, volumetric_strain=0),
                          dict(axial_strain=.01, q=10000, volumetric_strain=.001)])

    def test_complete_fields_do_not_establish_admission(self):
        result = classify(self.record())
        self.assertTrue(result['native_drained_field_candidate'])
        self.assertEqual(result['scientific_admission'], 'not_assessed')

    def test_one_missing_volume_value_blocks_candidate(self):
        record = self.record()
        del record['rows'][1]['volumetric_strain']
        result = classify(record)
        self.assertFalse(result['minimum_triaxial_fields_present'])
        self.assertEqual(result['missing_or_incomplete_required_channels'], ['volumetric_strain'])

    def test_reported_stress_is_not_effective_initial_stress(self):
        record = self.record()
        record['initial'] = dict(reported_stress=[100000]*3+[0]*3, void_ratio=.7)
        self.assertFalse(classify(record)['initial_effective_stress_present'])

    def test_summary_cannot_become_history_from_channel_names(self):
        record = self.record()
        record['kind'] = 'test-summary'
        result = classify(record)
        self.assertFalse(result['minimum_triaxial_fields_present'])
        self.assertEqual(result['disposition'], 'summary_not_a_loading_history')

    def test_undrained_requires_mean_effective_stress(self):
        record = self.record()
        record['protocol'] = 'undrained-triaxial'
        self.assertFalse(classify(record)['minimum_triaxial_fields_present'])
        for row in record['rows']:
            row['p'] = 100000
        result = classify(record)
        self.assertTrue(result['minimum_triaxial_fields_present'])
        self.assertFalse(result['native_drained_field_candidate'])

    def test_reserved_curated_member_rejected_before_asset_loader(self):
        path = Path(__file__).resolve().parents[1]/'scripts/audit_public_feasibility.py'
        spec = importlib.util.spec_from_file_location('paper_public_feasibility', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'data/curated').mkdir(parents=True)
            (root/'data/curated/index.json').write_text(json.dumps(dict(records=[dict(id='KFS-TMD6')])))
            (root/'data/public_sources.json').write_text('{}')
            with patch.object(module, 'ROOT', root), patch.object(module, 'load_curated') as loader:
                with self.assertRaisesRegex(ValueError, 'reserved final'):
                    module.audit()
                loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
