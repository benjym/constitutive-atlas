"""Complete native/Wasm generated-context evidence; no compiled execution."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'catalogue/investigations'
def module(version):
 path=BASE/('trace-generated-context-'+version)/'assess.py'
 spec=importlib.util.spec_from_file_location('context_'+version,path)
 result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
class TraceContextEvidence(unittest.TestCase):
 def test_corrected_complete_study_and_exact_json_types(self):
  study=BASE/'trace-generated-context-v2';result=module('v2').assess()
  self.assertTrue(result['pass'],result)
  self.assertEqual(result,json.loads((study/'assessment.json').read_text()))
  expected={'version':'trace-generated-context-observations-v1','material':json.loads((study/'expected.json').read_text()),'history':json.loads((study/'history-expected.json').read_text())}
  for backend in ['native','wasm']:
   actual=json.loads((study/backend/'observe.stdout.txt').read_text())
   self.assertEqual(json.dumps(actual,sort_keys=True),json.dumps(expected,sort_keys=True))
 def test_original_failed_study_retains_exact_two_mismatches(self):
  study=BASE/'trace-generated-context-v1';result=module('v1').assess()
  self.assertFalse(result['pass']);self.assertTrue(result['native_wasm_bit_parity'])
  self.assertEqual(result,json.loads((study/'assessment.json').read_text()))
  for backend in ['native','wasm']:
   self.assertEqual(result['backends'][backend]['mismatches'],['material:7719:trace-observable-scale-dev/extreme','material:10809:trace-state-scale-dev/extreme'])
 def test_missing_duplicate_corrupt_derivative_rows_reject(self):
  original=BASE/'trace-generated-context-v2'
  for change in ['missing','duplicate','derivative']:
   with self.subTest(change=change),tempfile.TemporaryDirectory()as tmp:
    root=Path(tmp)
    for name in ['README.md','protocol.json','prospective-freeze.json','expected.json','history-expected.json']:
     shutil.copyfile(original/name,root/name)
    for backend in ['native','wasm']:
     (root/backend).mkdir()
     for name in ['receipt.json','observe.stdout.txt','observe.stderr.txt']:shutil.copyfile(original/backend/name,root/backend/name)
    path=root/'native/observe.stdout.txt';data=json.loads(path.read_text())
    if change=='missing':data['material'].pop()
    elif change=='duplicate':data['material'][1]=data['material'][0]
    else:
     row=next(x for x in data['material']if x['id']=='trace-equation-direct/cancellation')
     row['derivative_bits'][37][0]='0000000000000000'
    path.write_text(json.dumps(data))
    assessor=module('v2');assessor.STUDY=root;self.assertFalse(assessor.assess()['pass'])
