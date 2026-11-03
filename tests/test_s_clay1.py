"""Original S-CLAY1 source compliance and public monotonic regressions."""
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODEL = json.loads((ROOT / 'models/s-clay1.json').read_text())
BASE = [x for f in MODEL['state'] for x in (f['initial'] if isinstance(f['initial'], list) else [f['initial']])]
SOLVER = Path(os.environ.get('ATLAS_SOLVER', ROOT / 'build/atlas_solver'))

class SClay1Tests(unittest.TestCase):
    def call(self, **options):
        args = [str(SOLVER), '--model', 's-clay1']
        for name, value in options.items():
            if isinstance(value, list): value = ','.join(format(x, '.17g') for x in value)
            args += ['--' + name.replace('_', '-'), str(value)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=60)
        data = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(data['ok'], result.stdout)
        return data

    def test_monotonic_public_examples_and_zero_hold(self):
        for protocol in (1, 2):
            run = self.call(mode='run', initial=BASE, protocol=protocol, target=.01, steps=100, cycles=0)
            self.assertEqual(len(run['points']), 101)
            self.assertNotEqual(run['points'][-1]['q'], run['points'][0]['q'])
            self.assertTrue(all(math.isfinite(x) for pt in run['points'] for x in pt['state']))
        held = self.call(mode='integrate', initial=BASE, strain=[0.] * 6)['state']
        for actual, expected in zip(held[:14], BASE[:14]):
            self.assertLessEqual(abs(actual - expected), 2e-10 * max(1., abs(expected)))

    def test_independent_original_compliance_refinement(self):
        path = ROOT / 'docs/ingestion/s-clay1/supplied-original-v3/independent-review/reference_compliance.py'
        spec = importlib.util.spec_from_file_location('sclay1_independent_reference', path)
        ref = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ref)
        errors = []
        for n in (128, 512):
            y = [ref.v0, ref.a0, ref.pm0, 0., 0.]
            z = [14000., 8000., 8000., 0., 0., 0., .28, -.14, -.14, 0., 0., 0., ref.v0, ref.pm0, 0.]
            step = (ref.p1 - ref.p0) / n
            stats = {'min_H': math.inf, 'min_multiplier_derivative': math.inf}
            for i in range(n):
                p = ref.p0 + i * step
                a = ref.derivative(p, y, stats)
                b = ref.derivative(p + step/2, [v + step*k/2 for v,k in zip(y,a)], stats)
                c = ref.derivative(p + step/2, [v + step*k/2 for v,k in zip(y,b)], stats)
                d = ref.derivative(p + step, [v + step*k for v,k in zip(y,c)], stats)
                yn = [v + step*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(y,a,b,c,d)]
                dv, dd = yn[3]-y[3], yn[4]-y[4]
                z[-1] = 0.
                z = self.call(mode='integrate', initial=z, strain=[dv/3+dd, dv/3-dd/2, dv/3-dd/2, 0., 0., 0.])['state']
                y = yn
            target = [16800., 9600., 9600., 0., 0., 0., 2*y[1]/3, -y[1]/3, -y[1]/3, 0., 0., 0., y[0], y[2]]
            scales = [20000.] * 6 + [1.] * 7 + [20000.]
            errors.append(max(abs(a-b)/s for a,b,s in zip(z[:14], target, scales)))
        self.assertLess(errors[-1], 3e-3)  # Original prospectively frozen source-reference gate.
        self.assertLess(errors[-1], errors[0])

if __name__ == '__main__':
    unittest.main()
