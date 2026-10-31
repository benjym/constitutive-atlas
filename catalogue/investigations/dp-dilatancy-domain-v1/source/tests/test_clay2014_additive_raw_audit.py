"""Opaque transport regressions; no native/Wasm execution or scientific corpus."""
import copy,json,pathlib,tempfile,unittest
from unittest.mock import patch
from tools import clay2014_rate_assessment as a
from tools import clay2014_rate_study as s
class RawNumberIdentity(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=pathlib.Path(self.tmp.name)/'raw.json'
 def pair(self,raw_number=0.0,report_number=0):
  descriptor={'models':[{'state':[{'initial':report_number}]}],'sha256':'a'*64}
  report={'backend':'wasm','descriptor':descriptor,'calls':[]}
  raw_descriptor=copy.deepcopy(descriptor);raw_descriptor['models'][0]['state'][0]['initial']=raw_number
  raw=[{'name':'atlas_describe','types':[],'args':[],'raw':json.dumps(raw_descriptor)}]
  self.p.write_text(json.dumps(raw));report['transport_sha256']=s.sha(self.p);return report
 def test_old_auditor_records_representation_failure(self):
  with self.assertRaises(ValueError):s.verify_transport(self.pair(),self.p)
 def test_additive_accepts_raw_float_report_integer(self):self.assertEqual(a.verify_transport(self.pair(),self.p),1)
 def test_additive_accepts_raw_integer_report_float(self):self.assertEqual(a.verify_transport(self.pair(0,0.0),self.p),1)
 def test_additive_rejects_raw_boolean_for_numeric_zero(self):
  with self.assertRaises(ValueError):a.verify_transport(self.pair(False,0),self.p)
 def test_additive_rejects_report_boolean_for_numeric_zero(self):
  with self.assertRaises(ValueError):a.verify_transport(self.pair(0.0,False),self.p)
 def test_additive_still_binds_opaque_bytes(self):
  report=self.pair();self.p.write_text(self.p.read_text()+' ')
  with self.assertRaises(ValueError):a.verify_transport(report,self.p)
 def test_additive_rejects_changed_numeric(self):
  with self.assertRaises(ValueError):a.verify_transport(self.pair(1.,0),self.p)
 def test_assessment_rejects_input_mutation_during_checks(self):
  paths=[pathlib.Path(self.tmp.name)/name for name in ('wasm.json','native.json','wasmraw.json','nativeraw.json')]
  for p in paths:p.write_text('{"claims":{}}')
  def mutate(*args):paths[0].write_text('{"claims":{},"changed":true}');return 0.
  with patch.object(s,'verify',return_value={}),patch.object(a,'verify_transport',return_value=1),patch.object(a,'compare',side_effect=mutate):
   with self.assertRaises(ValueError):a.assess(paths[0],paths[1],paths[2],paths[3])
if __name__=='__main__':unittest.main()
