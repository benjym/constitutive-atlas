"""Offline checks for the independently written audit tool; no OpenSees copy."""
import importlib.util
import math
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1]/'tools/verify_sanisand_source.py'
SPEC = importlib.util.spec_from_file_location('sanisand_source_probe', PATH)
s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)


class SanisandSourceProbeTests(unittest.TestCase):
    def test_exact_method_extraction_ignores_comment_and_string_braces(self):
        # Synthetic code only. Declarations and bodies must remain untouched.
        source = "orphan ' before unrelated code\n"+'\n'.join(f'double ManzariDafalias::{name}({"int a,int b,int c,int d" if name == "GetElasticModuli" else "int a"})\n'
                           '{ /* } */ const char* x="}"; if(a){return 1;} // }\n return 2; }'
                           for name in s.METHODS)
        methods = s.extract_methods(source)
        self.assertEqual([m['name'] for m in methods], list(s.METHODS))
        for method in methods:
            self.assertTrue(method['text'].endswith('return 2; }'))
            self.assertIn('const char* x="}"', method['text'])
            self.assertEqual(source.splitlines()[method['first_line']-1].split('(')[0],
                             'double ManzariDafalias::'+method['name'])
        with self.assertRaises(ValueError):
            s.extract_methods(source.replace('ManzariDafalias::GetPSI', 'ManzariDafalias::NotPSI'))

    def test_cartesian_oracle_limits_and_units(self):
        cases = {c['id']: c for c in s.cases()}
        results = {name: dict(zip(s.NAMES, s.oracle(case))) for name, case in cases.items()}
        self.assertEqual(len(cases), len(s.cases()))
        for case in cases.values():
            values = s.oracle(case)
            self.assertEqual(len(values), len(s.NAMES))
            self.assertTrue(all(math.isfinite(x) for x in values))
        zero = results['isotropic-zero-direction']
        self.assertEqual([zero[f'n[{i}]'] for i in range(6)], [0.]*6)
        self.assertEqual(zero['h'], 1e10)
        self.assertEqual(results['singular-memory-distance']['h'], 1e10)
        self.assertLess(results['signed-hardening-distance']['h'], 0)
        a, b = results['sheared-reference'], results['sheared-reference-pa']
        for name in ('K', 'G', 'F'):
            self.assertAlmostEqual(a[name]*1000, b[name], delta=1e-8*max(1, abs(b[name])))
        for name in ('psi', 'cos3', 'h', 'aB', 'aD', 'b0', 'A', 'D', 'B', 'C'):
            self.assertAlmostEqual(a[name], b[name], delta=1e-8*max(1, abs(b[name])))
        self.assertGreater(abs(results['pressure-0.2-kpa']['D']-results['pressure-0.2-pa']['D']), 1e-4)
        for name in ('K', 'G'):
            self.assertEqual(a[name], results['current-void-ratio-change'][name])

    def test_cartesian_rotation_covariance(self):
        cases = {c['id']: c for c in s.cases()}
        base = dict(zip(s.NAMES, s.oracle(cases['sheared-reference'])))
        for i, angle in enumerate((.17, .53, 1.2)):
            actual = dict(zip(s.NAMES, s.oracle(cases[f'rotated-reference-{i}'])))
            co, si = math.cos(angle), math.sin(angle)
            q = [[co, -si, 0], [si, co, 0], [0, 0, 1]]
            qt = [list(row) for row in zip(*q)]
            for name in s.SCALARS:
                self.assertAlmostEqual(base[name], actual[name], delta=2e-10*max(1, abs(base[name])))
            for name in ('n', 'b', 'd', 'R', 'sym_product'):
                expected = s.vector(s.product(s.product(q, s.matrix([base[f'{name}[{j}]'] for j in range(6)])), qt))
                for j in range(6):
                    self.assertAlmostEqual(expected[j], actual[f'{name}[{j}]'], delta=2e-10)


if __name__ == '__main__':
    unittest.main()
