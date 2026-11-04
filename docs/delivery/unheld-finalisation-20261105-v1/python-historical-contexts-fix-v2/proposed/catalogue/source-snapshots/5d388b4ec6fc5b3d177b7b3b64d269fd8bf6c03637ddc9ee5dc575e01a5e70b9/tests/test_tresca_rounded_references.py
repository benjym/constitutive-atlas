"""Independent reference construction, replay and meaningful receipt corruptions."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,tempfile,unittest
from atlas.model import ROOT
P=ROOT/'docs/reviews/tresca-rounded-reference-v1'
class TrescaRoundedReferencesTests(unittest.TestCase):
    def test_reference_gate_and_generation_replay(self):
        result=subprocess.run(['python3','-B',str(P/'check.py')],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads(result.stdout);self.assertEqual(report['cases'],61);self.assertEqual(report['columns'],38);self.assertEqual(report['history_steps'],12)
        self.assertEqual(report['rounded_history_parents_outside_source_yield'],[7])
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'replay.json.gz';result=subprocess.run(['python3','-B',str(P/'generate.py'),'--precision','200','--output',str(output)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(output.read_bytes(),(P/'reference-p200.json.gz').read_bytes())
    def test_exact_source_ideal_ancestry(self):
        # Exercise the new six-plane enumerator against all12 previously frozen exact certificates.
        script="""import sys,json;from decimal import Decimal as D,localcontext;from fractions import Fraction
sys.path.insert(0,sys.argv[1]);import generate as g
f=json.load(open(sys.argv[2]));conv=lambda s:D(Fraction(str(s)).numerator)/D(Fraction(str(s)).denominator)
with localcontext() as c:
 c.prec=200
 for row in f['cases']:
  trial=[conv(x)for x in row['trial_eigenvalues']];expected=[conv(x)for x in row['expected_return_eigenvalues']];got,active,_=g.project(trial,2*conv(f['parameters_Pa']['k']));assert max(abs(x-y)for x,y in zip(got,expected))<D('1e-100'),row['id'];assert g.branch(active,got)==row['branch'],row['id']
  # Rational active-set reconstruction certifies exact ancestry despite Decimal thirds.
  F=Fraction;t=list(map(Fraction,row['trial_eigenvalues']));width=2*F(f['parameters_Pa']['k']);N=[[F(i==a)-F(i==b)for i in range(3)]for a,b in active];v=[sum(x*y for x,y in zip(n,t))-width for n in N]
  alpha=[] if not N else [v[0]/2] if len(N)==1 else [(2*v[0]-sum(x*y for x,y in zip(N[0],N[1]))*v[1])/3,(2*v[1]-sum(x*y for x,y in zip(N[0],N[1]))*v[0])/3]
  exact=[t[i]-sum(a*n[i]for a,n in zip(alpha,N))for i in range(3)];assert exact==list(map(Fraction,row['expected_return_eigenvalues'])),row['id']
print(len(f['cases']))"""
        result=subprocess.run(['python3','-B','-c',script,str(P),str(ROOT/'docs/ingestion/tresca/prospective-freeze.json')],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(result.stdout.strip(),'12')
    def test_corrupted_values_derivatives_and_history_reject(self):
        for corruption in ('returned-state','mixed-derivative','history-link'):
            with self.subTest(corruption=corruption),tempfile.TemporaryDirectory()as d:
                t=Path(d)
                for f in P.iterdir():
                    if f.is_file():shutil.copyfile(f,t/f.name)
                for name in ('reference-p200.json.gz',)if corruption=='returned-state'else ('reference-p200.json.gz','reference-p280.json.gz'):
                    f=t/name;data=json.loads(gzip.decompress(f.read_bytes()))
                    if corruption=='returned-state':data['cases'][0]['reference']['returned_state'][0]='1234'
                    elif corruption=='mixed-derivative':data['cases'][0]['reference']['directions'][37]['residual'][0]='1234'
                    else:data['history'][2]['input']['parent'][0]='0x1.0p+50'
                    f.write_bytes(gzip.compress(json.dumps(data).encode(),mtime=0))
                result=subprocess.run(['python3','-B',str(t/'check.py')],capture_output=True,text=True,timeout=30)
                self.assertNotEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('AssertionError',result.stderr)
    def test_frozen_inputs_and_reference_code_have_no_candidate_import(self):
        import ast
        allowed={'pathlib','decimal','itertools','argparse','gzip','json','math','hashlib','spectral_source'}
        for name in ('generate.py','spectral_source.py'):
            tree=ast.parse((P/name).read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):self.assertTrue(all(a.name in allowed|{'sys','decimal'} for a in n.names),name)
                if isinstance(n,ast.ImportFrom):self.assertIn(n.module,allowed,name)
        for name,pin in json.loads((P/'pre-generation-freeze.json').read_text()).items():self.assertEqual(hashlib.sha256((P/name).read_bytes()).hexdigest(),pin,name)

    def test_literal_negative_and_seed_freeze(self):
        data=json.loads((P/'inputs.json').read_text());negative=json.loads((P/'backend-negative-input-freeze.json').read_text())
        self.assertEqual(len(negative['cases']),22);self.assertEqual(negative['seed_poison']['column'],37)
        self.assertEqual(negative['source_inputs_sha256'],hashlib.sha256((P/'inputs.json').read_bytes()).hexdigest())
        self.assertGreater(float(negative['initial_yield_boundary']['exact_rounded_yield_excess']),0)
        for j,seed in enumerate(data['seeds'][:30]):
            values=[float.fromhex(v)for key in ('current','parent','loading')for v in seed[key]]
            self.assertEqual(values,[float(i==j)for i in range(30)])
