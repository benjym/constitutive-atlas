"""Saved scope contracts and tamper rejection; never build or invoke native code."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.model import ROOT, validate
from tests.laboratory_scope_support import synthetic_total
PACKET=ROOT/'docs/reviews/laboratory-scope-contract-v1'
spec=importlib.util.spec_from_file_location('laboratory_scope_saved',PACKET/'assess.py')
ASSESSOR=importlib.util.module_from_spec(spec);spec.loader.exec_module(ASSESSOR)

class LaboratoryScopeContractTests(unittest.TestCase):
    def test_saved_gate_replays_with_process_execution_denied(self):
        with patch('subprocess.run',side_effect=AssertionError('native execution forbidden')):
            result=ASSESSOR.assess(PACKET)
        self.assertEqual(result['saved_processes'],48);self.assertEqual(result['native_calls'],0)

    def test_production_total_profile_stays_disabled(self):
        with self.assertRaisesRegex(ValidationError,'effective Cauchy'):validate(synthetic_total())

    def test_changed_scope_pore_wire_response_and_exit_are_rejected(self):
        mutations=['scope','null','wire','mechanics','returncode','missing']
        for mutation in mutations:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                target=Path(directory)/'packet';shutil.copytree(PACKET,target)
                summary=json.loads((target/'observations/summary.json').read_text())
                label='total-analytical-2' if mutation in ['scope','null'] else 'scoped-explicit' if mutation=='wire' else 'current-public-linear-elastic'
                records=[(target/'observations'/n) for n in summary['receipts']]
                path=next(p for p in records if json.loads(p.read_text())['label']==label)
                record=json.loads(path.read_text());data=json.loads(record['stdout'])
                if mutation=='scope':data['stress']['scope']='effective'
                elif mutation=='null':data['points'][0]['u']=0
                elif mutation=='wire':data['loading']['controls_bits'][1]='0'*16
                elif mutation=='mechanics':data['points'][-1]['p']+=1
                elif mutation=='returncode':record['returncode']=1
                elif mutation=='missing':summary['receipts'].remove(path.name);(target/'observations/summary.json').write_text(json.dumps(summary))
                record['stdout']=json.dumps(data);path.write_text(json.dumps(record))
                with self.assertRaises((AssertionError,KeyError,ValueError)):ASSESSOR.assess(target)

if __name__=='__main__':unittest.main()
