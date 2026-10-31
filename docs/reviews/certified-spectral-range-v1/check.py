"""Frozen exact arithmetic design gates; no Atlas or compiled calls."""
from pathlib import Path
from fractions import Fraction as F
import gzip,hashlib,json,math
from exact import Q,invariants,range_le,sturm_range_le
P=Path(__file__).parent;ROOT=P.parents[2]
def run():
    for name,h in json.loads((P/'pre-check-freeze.json').read_text()).items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
    for name,h in json.loads((P/'source-pins.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    grid=0;identities=0
    for a in range(13):
        for b in range(13):
            # Eigenvalues -a,0,b: exact gaps a,b,a+b. Scaling by3 below.
            v=[-a,0,b,0,0,0];j2,j3,_=invariants(v,a+b)
            for q in [F(0),F(1,7),F((3*(a+b))**2),F(7,3)]:
                h=Q(q**3-6*j2*q*q+9*j2*j2*q-4*j2**3)+27*j3*j3
                direct=(q-9*a*a)*(q-9*b*b)*(q-9*(a+b)**2)
                assert h==direct,(a,b,q);identities+=1
            width=float(a+b)
            for w in [width,math.nextafter(width,math.inf)]+([math.nextafter(width,0)]if width else []):
                expected=F(w)>=a+b
                assert range_le(v,w)==expected,(a,b,w,'bounded')
                assert sturm_range_le(v,w)==expected,(a,b,w,'sturm')
                grid+=1
    rows=[]
    for case in json.loads((P/'inputs.json').read_text())['cases']:
        v=[float.fromhex(x)for x in case['mandel']];w=float.fromhex(case['width'])
        result=range_le(v,w);independent=sturm_range_le(v,w)
        assert result==independent,case['id']
        if case['expected']is not None:assert result==case['expected'],case['id']
        rows.append({'id':case['id'],'inside':result})
    data=json.loads((ROOT/'docs/reviews/tresca-rounded-reference-v1/inputs.json').read_text());parents=[];outside=[]
    for prec in (200,280):
        refs=json.loads(gzip.decompress((ROOT/f'docs/reviews/tresca-rounded-reference-v1/reference-p{prec}.json.gz').read_bytes()))
        for case,ref in zip(data['cases'],refs['cases']):
            v=[float.fromhex(x)for x in case['parent'][:6]];w=2*case['parameters']['k']
            result=range_le(v,w);assert result==sturm_range_le(v,w)
            assert result==ref['reference']['parent_admissible'],(prec,case['id'])
            parents.append({'precision':prec,'id':case['id'],'inside':result})
        for row in refs['history']:
            v=[float.fromhex(x)for x in row['input']['parent'][:6]];w=2*row['input']['parameters']['k']
            result=range_le(v,w);assert result==sturm_range_le(v,w)
            assert result==row['reference']['parent_admissible'],(prec,row['step'])
            if not result:outside.append([prec,row['step']])
    assert outside==[[200,7],[280,7]],outside
    invalid=0
    for v,w in [([0]*5,1),([0]*7,1),([math.nan]+[0]*5,1),([math.inf]+[0]*5,1),([0]*6,math.nan),([0]*6,math.inf),([0]*6,-1)]:
        for f in (range_le,sturm_range_le):
            try:f(v,w)
            except ValueError:invalid+=1
            else:raise AssertionError('invalid input accepted')
    # Irrational signs, including cancellation and negative conjugates.
    for a,b,expected in [(0,0,0),(1,-1,-1),(-1,1,1),(2,-1,1),(-2,1,-1),(0,1,1),(0,-1,-1)]:assert Q(a,b).sign()==expected
    return {'version':'exact-spectral-range-design-checks-0.1','gap_polynomial_identities':identities,'diagonal_boundary_checks':grid,'literal_sturm_cases':len(rows),'literal_results':rows,'reference_parent_checks':len(parents)+24,'history_outside':outside,'invalid_rejections':invalid,'runtime_implemented':False,'compiled_calls':0}
if __name__=='__main__':print(json.dumps(run(),indent=2))
