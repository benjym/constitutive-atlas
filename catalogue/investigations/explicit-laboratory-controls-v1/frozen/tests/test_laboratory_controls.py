"""Independent elasticity and failure-prefix checks for the explicit bit-wire API."""
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

SOLVER = os.environ.get('ATLAS_SOLVER')

@unittest.skipUnless(SOLVER, 'ATLAS_SOLVER required for native integration checks')
class ExplicitLaboratoryControls(unittest.TestCase):
    def run_controls(self, protocol, values=None, *, wire=None, initial=None):
        if wire is None:
            wire = ','.join(struct.pack('>d', value).hex() for value in values)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'controls.csv'
            path.write_bytes(wire.encode())
            result = subprocess.run([
                SOLVER, '--mode', 'run-controls', '--model', 'linear-elastic',
                '--initial', ','.join(map(str, initial or [100000,100000,100000,0,0,0,.7])),
                '--protocol', str(protocol), '--laboratory-controls-file', str(path),
            ], capture_output=True, text=True, timeout=30)
        self.assertIn(result.returncode, (0,1), result.stderr)
        return json.loads(result.stdout)

    def test_five_protocols_against_isotropic_elasticity(self):
        for protocol in range(5):
            with self.subTest(protocol=protocol):
                controls = [0,10000,-5000,0] if protocol == 3 else [0,.001,-.0005,0]
                run = self.run_controls(protocol, controls)
                self.assertTrue(run['ok'], run.get('message'))
                self.assertEqual(len(run['points']), len(controls))
                self.assertEqual(run['loading']['controls_bits'], [struct.pack('>d',c).hex() for c in controls])
                self.assertNotIn('target',run)
                self.assertNotIn('cycles',run)
                for control, point in zip(controls, run['points']):
                    axial = control / 36000000 if protocol == 3 else control
                    lateral = -.25*axial if protocol == 1 else -.5*axial if protocol in (2,3) else axial if protocol == 4 else 0
                    strain = [axial,lateral,lateral,0,0,0]
                    volume = axial + 2*lateral
                    for j in range(6):
                        self.assertAlmostEqual(point['strain'][j],strain[j],delta=2e-10)
                        expected = 100000+12000000*volume+24000000*strain[j] if j<3 else 0
                        self.assertAlmostEqual(point['state'][j],expected,delta=.003)
                    self.assertAlmostEqual(point['state'][6],1.7*math.exp(-volume)-1,delta=2e-10)

    def test_rejects_malformed_and_nonfinite_whole_files(self):
        zero = '0000000000000000'
        for wire in ('', zero, zero+',', zero+',7ff0000000000000',zero+',7ff0000000000001',zero+',000000000000000G',zero+','+zero+'\0suffix',zero+','+zero+'\n'):
            with self.subTest(wire=repr(wire)):
                result = self.run_controls(0, wire=wire)
                self.assertFalse(result['ok'])
                self.assertFalse(result.get('points'))

    def test_signed_zero_and_subnormal_transport(self):
        controls = [-0.,float.fromhex('0x0.0000000000001p-1022'),-float.fromhex('0x0.0000000000001p-1022'),0.]
        run = self.run_controls(0, controls)
        self.assertTrue(run['ok'],run.get('message'))
        expected = [struct.pack('>d',c).hex() for c in controls]
        self.assertEqual(run['loading']['controls_bits'], expected)
        self.assertEqual([struct.pack('>d',p['control']).hex() for p in run['points']],expected)

    def test_failure_retains_committed_prefix(self):
        initial = [100000,100000,100000,0,0,0,.01]
        failed = self.run_controls(4,[0,.001,.1],initial=initial)
        recovered = self.run_controls(4,[0,.001],initial=initial)
        self.assertFalse(failed['ok'])
        self.assertIn('step 2',failed['message'])
        self.assertTrue(recovered['ok'],recovered.get('message'))
        self.assertEqual(len(failed['points']),2)
        self.assertEqual(failed['points'],recovered['points'])

if __name__ == '__main__':
    unittest.main()
