"""Source/row equivalence and unchanged state/history; no candidate evaluation."""
from tests.historical_generation import generate as historical_generate
from pathlib import Path
from fractions import Fraction as F
import copy,gzip,hashlib,importlib.util,json,subprocess,tempfile,unittest
from tests.reference_gzip_transport import subprocess
from atlas.model import ROOT,load
from atlas.compiler import generate
P=ROOT/'docs/reviews/tresca-pressure-split-v1'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaPressureSplitTests(unittest.TestCase):
    def test_candidate_keeps_full_source_contract(self):
        m=load(P/'model.json');old=load(ROOT/'docs/reviews/tresca-declarative-v1/model.json')
        self.assertEqual(m,module('split_proposal',P/'propose.py').proposal(ROOT))
        self.assertEqual({k for k in old if old[k]!=m[k]},{'id','name','description','derived','equations'})
        self.assertEqual(m['initial_checks'],old['initial_checks']);self.assertEqual(m['initialization']['required_state'],['sigma','ep'])
        self.assertEqual(sum(6 if f['shape']=='sym' else 1 for f in m['state']),12)
        with tempfile.TemporaryDirectory()as d:
            historical_generate(d,[P/'model.json'],'tresca-pressure-split-v1');expected=json.loads((P/'candidate-validation.json').read_text())['generated_sha256']
            for n,pin in expected.items():self.assertEqual(hashlib.sha256((Path(d)/n).read_bytes()).hexdigest(),pin)
    def test_saved_independent_equivalence(self):
        result=module('split_saved',P/'verify.py').verify(P,ROOT)
        self.assertEqual(result['direct_saved_row_checks']['components'],57384)
        self.assertEqual(result['source_checks']['pressure_split_updated_components'],1464)
        self.assertFalse(result['source_checks']['initial_membership_resolution'])
    def test_jointly_corrupted_residuals_reject(self):
        v=module('split_corruption',P/'verify.py')
        for mode in ('state','seed'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as d:
                t=Path(d)
                for precision in (200,280):
                    name='reference-full-row-p'+str(precision)+'.json.gz';data=json.loads(gzip.decompress((P/name).read_bytes()))
                    if mode=='state':data['cases'][0]['reference']['residual'][6]='123'
                    else:data['cases'][0]['reference']['directions'][37]['residual'][6]='123'
                    (t/name).write_bytes(gzip.compress(json.dumps(data).encode(),mtime=0))
                with self.assertRaises(AssertionError):v.verify_rows(t,ROOT)
    def test_failed_serialized_attempt_and_full_precision_replay(self):
        for precision in (200,280):
            failed=json.loads((P/('transform-p'+str(precision)+'-process.json')).read_text());self.assertEqual(failed['returncode'],1);self.assertIn('scaled-face--80',failed['stderr']);self.assertIn('E-51',failed['stderr'])
            self.assertEqual(json.loads((P/('full-row-p'+str(precision)+'-process.json')).read_text())['returncode'],0)
        with tempfile.TemporaryDirectory()as d:
            out=Path(d)/'row-replay.json.gz';result=subprocess.run(['python3','-B',str(P/'transform_full_precision.py'),'--precision','200','--output',str(out)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(out.read_bytes(),(P/'reference-full-row-p200.json.gz').read_bytes())
    def test_exact_block_row_identity(self):
        def C(v,lam,mu):return [2*mu*x+(lam*sum(v[:3])if i<3 else 0)for i,x in enumerate(v)]
        def inv(v,lam,mu):return [(x-(lam*sum(v[:3])/(3*lam+2*mu)if i<3 else 0))/(2*mu)for i,x in enumerate(v)]
        def dev(v):return [x-(sum(v[:3])/3 if i<3 else 0)for i,x in enumerate(v)]
        parent=list(map(F,[3,-2,5,1,-4,7]));de=[F(x,7)for x in [2,-3,6,-4,7,1]];current=[F(x,11)for x in [4,-7,8,1,-5,9]];epdiff=[F(x,13)for x in [2,3,-4,6,-7,8]];rd=list(map(F,[1,2,-3,5,-2,4]))
        for lam,mu in [(F(3),F(2)),(F(7,3),F(5,4))]:
            trial=[x+y for x,y in zip(parent,C(de,lam,mu))];D=[x+2*mu*y for x,y in zip(dev(parent),dev(de))];mean=sum(parent[:3])/3+(lam+2*mu/3)*sum(de[:3]);self.assertEqual(trial,[x+(mean if i<3 else 0)for i,x in enumerate(D)])
            R=[x+(mean if i<3 else 0)for i,x in enumerate(rd)];rs=[x-y for x,y in zip(current,R)];old=[x-y for x,y in zip(epdiff,inv([x-y for x,y in zip(trial,current)],lam,mu))];transformed=[x-y for x,y in zip(old,inv(rs,lam,mu))];new=[x-(y-z)/(2*mu)for x,y,z in zip(epdiff,D,rd)];self.assertEqual(transformed,new)
