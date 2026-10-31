"""Independent scalar diagnostic tests; no native/Wasm or source-rate execution."""
import ast,copy,json,math,os,tempfile,unittest
from pathlib import Path
from tools import clay2014_midpoint_diagnostic as d
ROOT=Path(os.environ.get('ATLAS_DIAGNOSTIC_ROOT',d.ROOT))
class ScalarDiagnostic(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.result=d.build(ROOT)
 def test_no_production_imports_and_fresh_retained_replay(self):
  tree=ast.parse(Path(d.__file__).read_text());imports=[n.module if isinstance(n,ast.ImportFrom)else x.name for n in ast.walk(tree)if isinstance(n,(ast.Import,ast.ImportFrom))for x in(getattr(n,'names',[])[:1]if isinstance(n,ast.ImportFrom)else n.names)]
  self.assertFalse(any(x.startswith(('atlas','tools'))for x in imports))
  retained=Path(d.__file__).resolve().parents[1]/'catalogue/investigations/clay2014-midpoint-diagnostic-v1/evidence.json'
  self.assertEqual(json.loads(retained.read_text()),self.result);d.verify(self.result,ROOT)
 def test_fixed_fraction_replay_matches_native_and_plateau(self):
  rows=self.result['recorded_partition_replays'];self.assertEqual([x['tolerance']for x in rows],[1e-4,1e-6,1e-8])
  self.assertTrue(all(c['fractions']==[.5,.5]for row in rows[:2]for c in row['calls'][:7]))
  for row in rows:
   for c in row['calls']:
    self.assertLessEqual(abs(c['scalar_midpoint_minus_native'][0]),2e-10);self.assertLessEqual(abs(c['scalar_midpoint_minus_native'][1]),2e-15);self.assertLessEqual(abs(c['decimal_midpoint_void_minus_native']),2e-15)
  self.assertLess(1e-8,self.result['estimated_first_piece_acceptance_error']);self.assertLess(self.result['estimated_first_piece_acceptance_error'],1e-6)
 def test_void_local_polynomial_and_sign(self):
  report=d.read_inputs(ROOT);p=report['records'][21]['calls'][0]['request']['parameters'];z=[1e5,.65]
  for v in(.001,-.001,0.):
   e=d.midpoint(z,v,p)[1];want=(1+z[1])*(1-v+v*v/2)-1
   self.assertLessEqual(abs(e-want),5e-16)
   if v:self.assertEqual(math.copysign(1,e-((1+z[1])*math.exp(-v)-1)),math.copysign(1,v))
 def test_unloading_cancellation_and_independent_uniform_grid(self):
  rows=self.result['recorded_partition_replays'];loose=rows[0]['calls'];middle=rows[1]['calls']
  self.assertEqual(loose[6]['signed_void_truncation'],middle[6]['signed_void_truncation'])
  self.assertLess(loose[13]['signed_void_truncation'],middle[13]['signed_void_truncation'])
  self.assertEqual([r['uniform_substeps_per_piece']for r in self.result['uniform_scalar_midpoint_diagnostic']],[2,4,8,16])
 def test_corrupted_replay_and_claims_rejected(self):
  edits=[lambda r:r['recorded_partition_replays'][0]['calls'][0]['scalar_midpoint_minus_native'].__setitem__(0,1.),lambda r:r['recorded_partition_replays'][0]['calls'][0]['fractions'].__setitem__(0,True),lambda r:r.__setitem__('estimated_first_piece_acceptance_error',0),lambda r:r['claims'].__setitem__('original_study_passed',True),lambda r:r['input_pins'].__setitem__(d.RAW,'0'*64)]
  for edit in edits:
   r=copy.deepcopy(self.result);edit(r)
   with self.assertRaises(ValueError):d.verify(r,ROOT)
 def test_input_report_raw_reference_bytes_pinned(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory)
   for name in d.PINS:
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
   for name in d.PINS:
    target=root/name;original=target.read_bytes();target.write_bytes(original+b' ')
    with self.assertRaisesRegex(ValueError,'immutable input hash'):d.build(root)
    target.write_bytes(original)
 def test_no_bool_numeric_alias(self):
  self.assertFalse(d.same([True],[1]));self.assertTrue(d.same([1.],[1]));self.assertFalse(d.same([math.nan],[math.nan]))
if __name__=='__main__':unittest.main()
