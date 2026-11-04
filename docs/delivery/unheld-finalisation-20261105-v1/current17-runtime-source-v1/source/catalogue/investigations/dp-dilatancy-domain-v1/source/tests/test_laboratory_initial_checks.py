"""Laboratory initialization must reject out-of-yield states before recording them."""
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

SOLVER = os.environ.get('ATLAS_SOLVER')

@unittest.skipUnless(SOLVER, 'ATLAS_SOLVER required for native laboratory checks')
class LaboratoryInitialChecks(unittest.TestCase):
    def test_outside_yield_is_rejected_before_first_point(self):
        # DP: p=400kPa,q=900kPa, so q-1.2p-10kPa=410kPa>0.
        # MCC: spherical p=300kPa exceeds pc=200kPa; p(p-pc)>0.
        examples = [
            ('drucker-prager',[1000000,100000,100000,0,0,0,.7,0]),
            ('modified-cam-clay',[300000,300000,300000,0,0,0,.7,200000,0]),
        ]
        with tempfile.TemporaryDirectory() as directory:
            wire = Path(directory)/'controls.csv'
            wire.write_text(','.join(struct.pack('>d',x).hex() for x in [0,.001]))
            for model, initial in examples:
                for mode in ['run','run-controls']:
                    with self.subTest(model=model,mode=mode):
                        args=[SOLVER,'--mode',mode,'--model',model,'--initial',','.join(map(str,initial)),'--protocol','1']
                        if mode=='run':args+=['--target','.001','--steps','1','--cycles','0']
                        else:args+=['--laboratory-controls-file',str(wire)]
                        result=subprocess.run(args,text=True,capture_output=True,timeout=30)
                        self.assertEqual(result.returncode,1,result.stderr)
                        response=json.loads(result.stdout)
                        self.assertIs(response['ok'],False)
                        if 'points' in response:self.assertIsInstance(response['points'],list)
                        self.assertEqual(response.get('points',[]),[])

if __name__=='__main__':
    unittest.main()
