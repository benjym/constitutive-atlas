"""Saved laboratory adapter evidence, including the original auxiliary failure."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT
PACKET=ROOT/'docs/reviews/laboratory-scope-adapter-v1'
s=importlib.util.spec_from_file_location('laboratory_adapter_saved',PACKET/'verify.py');gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate)
class LaboratoryAdapterEvidenceTests(unittest.TestCase):
    def test_saved_outputs_without_processes(self):
        with patch('subprocess.run',side_effect=AssertionError('execution forbidden')):r=gate.assess(PACKET)
        self.assertEqual(r['native_pairs'],10);self.assertEqual(r['wasm_material_requests'],11);self.assertTrue(r['original_auxiliary_failure_retained'])
    def test_scope_pore_stress_and_prefix_corruption_rejected(self):
        for kind in ['scope','pore','stress','prefix']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                p=Path(temp)/'packet';shutil.copytree(PACKET,p);f=p/'responses.json';d=json.loads(f.read_text());x=d[-1]['result']
                if kind=='scope':x['stress']['scope']='total'
                elif kind=='pore':x['points'][1]['u']=0
                elif kind=='stress':x['points'][1]['state'][0]+=1
                else:x['points'].pop()
                f.write_text(json.dumps(d))
                with self.assertRaises((AssertionError,ValueError)):gate.assess(p)
