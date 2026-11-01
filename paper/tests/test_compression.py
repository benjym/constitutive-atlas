import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.compression_data import normalize_oedometer, audit_oedometer
from analysis.reservations import load_policy, select_members

SOURCE = b'sigma1 eps1 Void ratio\n[kPa] [%] [-]\n\n0.000 0.000 0.80000\n100.000 1.000 0.78200\n'


class CompressionTests(unittest.TestCase):
    def test_units_order_and_no_invented_full_stress(self):
        r = normalize_oedometer(SOURCE, 'OE1.dat', 'a', 'b')
        self.assertEqual(r['rows'][1]['axial_stress'], 100000)
        self.assertEqual(r['rows'][1]['axial_strain'], .01)
        self.assertEqual(r['rows'][0]['source_line'], 4)
        self.assertNotIn('effective_stress', r['initial'])
        self.assertEqual(r['initial']['axial_stress'], 0)
        self.assertLess(audit_oedometer(r)['maximum_print_rounding_ratio'], 1e-7)

    def test_wrong_units_and_nonfinite_data_rejected(self):
        for content in (SOURCE.replace(b'[kPa]', b'[Pa]'), SOURCE.replace(b'100.000', b'nan')):
            with self.assertRaises(ValueError):
                normalize_oedometer(content, 'OE1.dat', 'a', 'b')

    def test_reserved_member_rejected_before_content_parsing(self):
        with self.assertRaisesRegex(ValueError, 'reserved final'):
            normalize_oedometer(b'not read', 'OE2.dat', 'a', 'b')
        self.assertEqual(select_members(['OE1.dat', 'OE2.dat'], ['KFS-OE1']), {'KFS-OE1': 'OE1.dat'})

    def test_reversals_across_repeated_stresses(self):
        r = normalize_oedometer(SOURCE, 'OE1.dat', 'a', 'b')
        r['rows'] += [dict(axial_stress=s, axial_strain=x, void_ratio=.8-1.8*x)
                      for s, x in [(100000, .01), (50000, .006), (50000, .006), (100000, .01)]]
        result = audit_oedometer(r)
        self.assertEqual(result['stress_direction_changes'], 2)
        self.assertEqual(result['repeated_stress_steps'], 2)
        self.assertEqual(result['decreasing_axial_strain_steps'], 1)

    def test_inconsistent_volume_is_not_explained_by_rounding(self):
        r = normalize_oedometer(SOURCE, 'OE1.dat', 'a', 'b')
        r['rows'][1]['void_ratio'] += .001
        self.assertGreater(audit_oedometer(r)['maximum_print_rounding_ratio'], 1)

    def test_extraction_leaves_reserved_bytes_unparsed(self):
        file = Path(__file__).resolve().parents[1]/'scripts/prepare_development_data.py'
        spec = importlib.util.spec_from_file_location('compression_preparation', file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root/'source.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('OE1.dat', SOURCE)
                z.writestr('OE2.dat', b'RESERVED: this would fail normalization')
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps(dict(reservation_id=load_policy()['id'], sources=[dict(
                filename=archive.name, url='never-contact-network', protocol='oedometer',
                sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), size_bytes=archive.stat().st_size,
                development_ids=['KFS-OE1'])])))
            ledger = module.prepare(manifest, root/'output', raw_dir=root)
            self.assertEqual(ledger['read_member_ids'], ['KFS-OE1'])
            self.assertFalse((root/'output/normalized/KFS-OE2.json').exists())


if __name__ == '__main__':
    unittest.main()
