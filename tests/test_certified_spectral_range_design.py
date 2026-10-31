"""Source-only generic exact membership design evidence."""
from pathlib import Path
import hashlib,json,subprocess,sys,unittest
from atlas.model import ROOT
P=ROOT/'docs/reviews/certified-spectral-range-v1'
class CertifiedSpectralRangeDesignTests(unittest.TestCase):
    def test_frozen_exact_design_replay(self):
        result=subprocess.run([sys.executable,'-B',str(P/'check.py')],capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout);self.assertEqual(data,json.loads((P/'checks.json').read_text()))
        self.assertEqual(data['history_outside'],[[200,7],[280,7]])
        self.assertEqual(data['gap_polynomial_identities'],676)
        self.assertEqual(data['reference_parent_checks'],146)
        self.assertFalse(data['runtime_implemented'])
    def test_exact_predicate_rejects_boundary_neighbor(self):
        # Below/equal/above at a repeated spectrum; no source-yield tolerance.
        code="""import sys,math;sys.path.insert(0,sys.argv[1]);from exact import range_le,sturm_range_le
for f in [range_le,sturm_range_le]:
 assert not f([-1,-1,1,0,0,0],math.nextafter(2.,0))
 assert f([-1,-1,1,0,0,0],2.)
 assert f([-1,-1,1,0,0,0],math.nextafter(2.,math.inf))
# Common-root endpoint in the Sturm chain still counts the larger root.
assert not sturm_range_le([-1,0,1,0,0,0],1.)
"""
        result=subprocess.run([sys.executable,'-B','-c',code,str(P)],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
    def test_no_runtime_dependency_and_source_identity(self):
        import ast
        allowed={'fractions','math','pathlib','gzip','hashlib','json','exact'}
        for name in ('exact.py','check.py'):
            for n in ast.walk(ast.parse((P/name).read_text())):
                if isinstance(n,ast.Import):self.assertTrue(all(a.name in allowed for a in n.names))
                if isinstance(n,ast.ImportFrom):self.assertIn(n.module,allowed)
        for name,pin in json.loads((P/'pre-check-freeze.json').read_text()).items():self.assertEqual(hashlib.sha256((P/name).read_bytes()).hexdigest(),pin)
