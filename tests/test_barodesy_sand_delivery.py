"""Current common-engine regressions against independent2015 stress histories."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT/'docs/ingestion/barodesy-sand/delivery-v1'
SOLVER = Path(os.environ.get('ATLAS_SOLVER', str(ROOT/'build/atlas_solver')))

class BarodesySandDelivery(unittest.TestCase):
    def test_exact_qualified_definition(self):
        self.assertEqual(hashlib.sha256((ROOT/'models/barodesy-sand.json').read_bytes()).hexdigest(),
                         '3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239')
        refs = json.loads((PACKET/'references.json').read_text())
        self.assertEqual(len(refs), 10)
        for ref in refs.values():
            self.assertLessEqual(max(ref['refinement_maximum'][:3]), .01)
            self.assertLessEqual(max(ref['refinement_maximum'][3:]), 1e-10)

    @unittest.skipUnless(SOLVER.is_file(), 'Build the common atlas_solver for current numerical regression')
    def test_current_compiled_all_five_controls_and_reversals(self):
        refs = json.loads((PACKET/'references.json').read_text())
        for key, ref in refs.items():
            with self.subTest(history=key):
                case = ref['case']
                command = [str(SOLVER), '--mode', 'run', '--model', 'barodesy-sand',
                           '--parameters', '-1.0246,1,-2.3,465000,28,.87,.35',
                           '--initial', '100000,100000,100000,0,0,0,.75']
                for name in ['protocol','target','steps','cycles']:
                    command += ['--'+name, str(case[name])]
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                out = json.loads(result.stdout)
                self.assertTrue(out['ok'], out.get('message'))
                self.assertEqual(len(out['points']), len(ref['points']))
                for point, expected in zip(out['points'], ref['points']):
                    self.assertLessEqual(max(abs(a-b) for a,b in zip(point['state'][:3],expected[:3])), 5.)
                    self.assertLessEqual(abs(point['state'][6]-expected[3]), 2e-7)
                    self.assertLessEqual(max(abs(a-b) for a,b in zip(point['strain'][:3],expected[4:])), 2e-7)

if __name__ == '__main__':
    unittest.main()
