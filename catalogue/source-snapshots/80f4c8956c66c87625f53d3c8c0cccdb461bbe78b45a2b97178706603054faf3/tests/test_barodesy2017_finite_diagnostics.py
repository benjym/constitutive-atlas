"""Strict rate diagnostics/CLI tests; subprocess never invoked."""
import copy,io,tempfile,pathlib,unittest
from unittest.mock import patch
from tools import barodesy2017_integration_study as s
from atlas.model import load
class Diagnostics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  _,cls.cases=s.checked_reference();cls.model=load(s.MODEL_PATH);cls.request=s.control_request(cls.model,cls.cases)
 def response(self):
  r=self.request
  return dict(ok=True,message='',state=r['initial'].copy(),model=r['model'],catalogue_hash=s.digest([self.model]),parameters=r['parameters'].copy(),initial=r['initial'].copy(),strain=r['strain'].copy(),integration_settings=s.settings(r),diagnostics=dict(substeps=2,iterations=0,rejected=0,increment_fractions=[.5,.5]))
 def check(self,a,r=None):return s.check_response(a,self.request if r is None else r,self.model)
 def test_valid_equal_dyadic_pairs(self):
  for f in ([.5,.5],[.25]*4,[.25,.25,.125,.125,.125,.125]):
   a=self.response();a['diagnostics'].update(substeps=len(f),increment_fractions=f);self.check(a)
 def test_impossible_fractions_and_counts(self):
  mutations=[lambda a:a.update(message='integration failed'),lambda a:a['diagnostics'].update(substeps=2,increment_fractions=[.3,.7]),lambda a:a['diagnostics'].update(substeps=2,increment_fractions=[.4,.4]),lambda a:a['diagnostics'].update(substeps=3,increment_fractions=[.5,.25,.25]),lambda a:a['diagnostics'].update(substeps=2,increment_fractions=[.25,.75])]
  for change in mutations:
   a=self.response();change(a)
   with self.assertRaises(ValueError):self.check(a)
 def test_substep_limit_and_depth(self):
  a=self.response();a['diagnostics'].update(substeps=20002,increment_fractions=[1/32768]*20002)
  with self.assertRaisesRegex(ValueError,'budget'):self.check(a)
  # Fraction below supporteddepth rejects even if totalcoverage tolerance could
  # hide two tiny extra paired entries next to a complete valid pair.
  a=self.response();a['diagnostics'].update(substeps=4,increment_fractions=[.5,.5,2.**-30,2.**-30])
  with self.assertRaisesRegex(ValueError,'depth'):self.check(a)
 def test_budget_partial_observed_shape(self):
  r=copy.deepcopy(self.request);r['settings'][4]=3;a=self.response();a.update(ok=False,message='state rolled back',integration_settings=s.settings(r),initial=r['initial'].copy());a['diagnostics'].update(substeps=2,rejected=6,increment_fractions=[.0078125,.0078125])
  self.assertEqual(s.check_response(a,r,self.model,False,True),.015625)
 def test_wasm_cli_requires_native_before_verification(self):
  with patch('sys.argv',['study','--report','unused','--output','unused']),patch.object(s,'read',return_value={'backend':'wasm'}),patch.object(s,'verify',side_effect=AssertionError('must not verify without parity binding')):
   with self.assertRaisesRegex(ValueError,'requires --native-report'):s.main()
 def test_native_cli_does_not_require_parity(self):
  with tempfile.TemporaryDirectory()as tmp,patch('sys.stdout',new_callable=io.StringIO):
   output=pathlib.Path(tmp)/'report.json'
   with patch('sys.argv',['study','--report','unused','--output',str(output)]),patch.object(s,'read',return_value={'backend':'native'}),patch.object(s,'verify',return_value={'checked':True}):s.main()
   self.assertTrue(output.exists())
if __name__=='__main__':unittest.main()
