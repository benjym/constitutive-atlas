"""Burgers installation, saved analytical evidence and corruption rejection.
No compiled artifacts are required for this regression test.
"""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from atlas.compiler import generate
from atlas.initialization import initialize_state
from atlas.model import ROOT,all_models,defaults,load
R=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'

class BurgersIntegrationTests(unittest.TestCase):
    def test_saved_source_accuracy_restart_and_native_wasm_parity(self):
        p=subprocess.run([sys.executable,'-B',str(R/'verify.py')],capture_output=True,text=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads(p.stdout)
        self.assertTrue(result['native']['ok'])
        self.assertTrue(result['wasm']['ok'])
        self.assertTrue(result['parity']['ok'])

    def test_separate_generated_catalogue_retains_exact_draft(self):
        model_path=ROOT/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json'
        self.assertEqual(model_path.read_bytes(),(R/'model.json').read_bytes())
        self.assertNotIn(load(model_path)['id'],[m['id'] for m in all_models()])
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp,[model_path])
            descriptor=json.loads((Path(tmp)/'models.json').read_text())
            self.assertEqual(descriptor['models'],[load(model_path)])
            native=json.loads((R/'native-calls.json').read_text())[0]['response']
            self.assertEqual(descriptor,native)

    def test_independent_reference_rejects_corrupted_repeatable_stress(self):
        calls=json.loads((R/'native-calls.json').read_text())
        for c in calls:
            if c['label'] in ['relaxation','relaxation-repeat']:
                point=c['response']['points'][-1]
                point['state'][0]+=1000;point['observables'][0]+=1000
        with tempfile.TemporaryDirectory() as tmp:
            corrupted=Path(tmp)/'corrupted.json';corrupted.write_text(json.dumps(calls))
            p=subprocess.run([sys.executable,'-B',str(R/'study.py'),'assess',str(corrupted)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('AssertionError',p.stderr)

    def test_kelvin_restart_history_cannot_be_omitted(self):
        model=load(R/'model.json')
        with self.assertRaises(ValueError):
            initialize_state(model,{'sigma':[100000]*3+[0]*3},defaults(model),time=0,loading=[0]*6)
        with self.assertRaises(ValueError):
            initialize_state(model,{'sigma':[100000]*3+[0]*3,'ek':[.1,0,0,0,0,0]},defaults(model),time=0,loading=[0]*6)

if __name__=='__main__':unittest.main()
