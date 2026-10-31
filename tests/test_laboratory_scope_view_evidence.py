"""Saved receipts reject scope, history and CSV corruption without compiled calls."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT
P=ROOT/'docs/reviews/laboratory-scope-view-v1'
spec=importlib.util.spec_from_file_location('lab_view_receipts',P/'verify.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
class LaboratoryScopeViewEvidenceTests(unittest.TestCase):
    def test_saved_gate(self):self.assertEqual(gate.assess(P)['public_native_pairs'],9)
    def test_corruptions(self):
        for case in ('scope','pore','history','csv'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
                dest=Path(d)
                for f in P.iterdir():
                    if f.is_file():shutil.copyfile(f,dest/f.name)
                if case=='csv':
                    f=dest/'browser-total-exact.csv';f.write_text(f.read_text().replace(',total,unavailable,',',total,reconstructed,',1))
                else:
                    f=dest/('browser-total-exact.json' if case=='history' else 'browser-total-1.json');v=json.loads(f.read_text())
                    if case=='scope':v['result']['stress']['scope']='effective'
                    elif case=='pore':v['result']['points'][0]['u']=0
                    else:v['result']['points'][8]['state'][-1]+=0.01
                    f.write_text(json.dumps(v))
                with self.assertRaises(AssertionError):gate.assess(dest)

    def test_exported_documents_use_strict_parser(self):
        import subprocess
        script="""import {readFileSync} from 'node:fs';import {parseLaboratoryDocument} from './web/laboratory-document.mjs';
const p='docs/reviews/laboratory-scope-view-v1/',privateC=JSON.parse(readFileSync(p+'private-catalogue.json')),publicC=JSON.parse(readFileSync(p+'public-catalogue.json'));
for(const n of ['total-0','total-1','total-2','total-3','total-4','total-exact','effective','legacy','public'])parseLaboratoryDocument(readFileSync(p+'browser-'+n+'.json','utf8'),n==='public'?publicC:privateC);
console.log('9 strict document imports');"""
        result=subprocess.run(['node','--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
