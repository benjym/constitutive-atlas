"""Retained generated v0.3 routing evidence; these tests do not compile."""
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'catalogue/investigations/expression-generated-context-v1'
spec=importlib.util.spec_from_file_location('expression_context_assessor',STUDY/'assess.py')
ASSESSOR=importlib.util.module_from_spec(spec);spec.loader.exec_module(ASSESSOR)
class ExpressionContextEvidence(unittest.TestCase):
    def test_complete_rows_and_backend_bits(self):
        result=ASSESSOR.assess()
        self.assertTrue(result['pass'])
        self.assertEqual(result,json.loads((STUDY/'assessment.json').read_text()))
        for backend in ('native','wasm'):
            self.assertEqual(result['backends'][backend]['material_rows'],10870)
            self.assertEqual(result['backends'][backend]['history_rows'],18)
        models=list((STUDY/'models').glob('*.json'))
        self.assertEqual(len(models),64)
        self.assertTrue(all(json.loads(p.read_text())['schema_version']=='0.3'for p in models))

    def test_missing_duplicate_types_column37_and_history_rollback_reject(self):
        for change in ('missing','duplicate','bool-type','column37','history-event'):
            with self.subTest(change=change),tempfile.TemporaryDirectory()as temp:
                copy=Path(temp)/'study';shutil.copytree(STUDY,copy)
                p=copy/'native/observe.stdout.txt';data=json.loads(p.read_text())
                if change=='missing':data['material'].pop()
                elif change=='duplicate':data['material'].append(data['material'][0])
                elif change=='bool-type':data['material'][0]['ok']=int(data['material'][0]['ok'])
                elif change=='column37':
                    row=next(r for r in data['material']if r['derivative_bits'])
                    row['derivative_bits'][37][0]='3ff0000000000000'
                else:
                    row=next(r for r in data['history']if not r['ok'])
                    row['events']=[0]
                p.write_text(json.dumps(data))
                self.assertFalse(ASSESSOR.assess(copy)['pass'])

    def test_changed_frozen_header_rejects(self):
        with tempfile.TemporaryDirectory()as temp:
            copy=Path(temp)/'study';shutil.copytree(STUDY,copy)
            p=copy/'frozen/cpp/include/atlas/checked_expression.hpp'
            p.write_text(p.read_text()+'\n//changed\n')
            with self.assertRaisesRegex(ValueError,'changed frozen input'):
                ASSESSOR.assess(copy)

    def test_frozen_generators_reproduce_model_and_history_headers(self):
        code="""import pathlib,sys,hashlib,json
frozen=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(frozen))
import atlas.compiler,atlas.history_compiler
assert pathlib.Path(atlas.compiler.__file__).resolve().is_relative_to(frozen)
assert pathlib.Path(atlas.history_compiler.__file__).resolve().is_relative_to(frozen)
s=pathlib.Path(sys.argv[2]);out=pathlib.Path(sys.argv[3])
atlas.compiler.generate(out,sorted((s/'models').glob('*.json')))
(out/'history.hpp').write_text(atlas.history_compiler.generate(json.loads((s/'history-programs.json').read_text())))
print(json.dumps({name:hashlib.sha256((out/name).read_bytes()).hexdigest()for name in ('models.hpp','models.json','history.hpp')}))
"""
        with tempfile.TemporaryDirectory()as temp:
            env={k:v for k,v in os.environ.items()if not k.startswith(('PYTHON','ATLAS'))}
            result=subprocess.run([sys.executable,'-I','-S','-B','-c',code,str(STUDY/'frozen'),str(STUDY),temp],
                                  env=env,cwd=temp,text=True,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            for name,pin in json.loads(result.stdout).items():
                self.assertEqual(pin,hashlib.sha256((STUDY/'generated'/name).read_bytes()).hexdigest())
