"""Independent reviewer checks. No Atlas imports, compiled calls, or author code."""
from pathlib import Path
import hashlib,json,math
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[5]
HERE=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
    paths=['models/barodesy-sand.json','docs/ingestion/barodesy-sand/source-audit.json','docs/ingestion/barodesy-sand/rate-study-v2/inputs.json','docs/ingestion/barodesy-sand/rate-study-v2/reference.json','catalogue/investigations/barodesy2015-rates-v2/RESULTS.md','catalogue/investigations/barodesy2015-preview-v1/RESULTS.md','catalogue/investigations/barodesy2015-preview-v1/assessment.json']
    hashes={p:digest(ROOT/p) for p in paths}
    assert hashes[paths[0]]=='3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239'
    sources=json.loads((ROOT/paths[1]).read_text())['sources']
    for s in sources:assert digest(Path(s['private_path']))==s['sha256']
    inputs=json.loads((ROOT/paths[2]).read_text()); refs=json.loads((ROOT/paths[3]).read_text())
    oracle={r['id']:r['oracle120']['values'] for r in refs['records']}
    checks=[]; maxerr=0
    for c in inputs['valid']+inputs['additional_operational_valid']:
        z=c['state']; load=c['loading']; p=c['parameters']; exp=oracle[c['id']]
        exact=float(-(1+Fraction.from_float(float(z[6])))*sum((Fraction.from_float(float(x)) for x in load[:3]),Fraction(0)))
        assert exact==exp[6],c['id']
        # Diagonal stretching makes the Cartesian matrix exponential three scalar exponentials.
        if any(load[3:]) or not any(load):continue
        speed=math.sqrt(sum(x*x for x in load)); delta=-sum(load[:3])/speed
        a=p['c1']*math.exp(p['c2']*delta)
        r=[-math.exp(-a*x/speed) for x in load[:3]]
        rn=math.sqrt(sum(x*x for x in r)); sn=math.sqrt(sum(x*x for x in z[:6])); e=z[6]
        b=(p['ec0']-p['emin'])/(p['ec0']+1)*(1+p['c5']*sn/p['c4'])**(-(1+p['emin'])/p['c5'])
        ec=(p['emin']+b)/(1-b); h=-(p['c4']+p['c5']*sn)/(e-p['emin']); f=delta+p['c3']*ec; g=-p['c3']*e
        values=[-h*(f*(r[i]/rn if i<3 else 0)-g*z[i]/sn)*speed for i in range(6)]
        scale=max(p['c4']*speed,math.sqrt(sum(x*x for x in exp[:6])))
        err=max(abs(x-y) for x,y in zip(values,exp[:6]))/scale
        assert err<=2e-12,(c['id'],err)
        maxerr=max(maxerr,err);checks.append(c['id'])
    model=json.loads((ROOT/paths[0]).read_text())
    assert model['schema_version']=='0.3' and model['formulation']['objective_rate']=='none'
    assert [s['name'] for s in model['state']]==['sigma','e']
    assert set(model['parameters'])=={'c1','c2','c3','c4','c5','ec0','emin'}
    assert {k:v['default'] for k,v in model['parameters'].items()}==dict(c1=-1.0246,c2=1,c3=-2.3,c4=465000,c5=28,ec0=.87,emin=.35)
    return {'reviewer':'/root/barodesy_sand_review','scope':'preliminary source/finite-path-gap review; no canonical approval','model_sha256':hashes[paths[0]],'input_hashes':hashes,'private_source_hashes':[s['sha256'] for s in sources],'exact_volume_cases':len(oracle),'independent_scalar_exponential_cases':checks,'maximum_scaled_stress_error':maxerr,'pass':True,'compiled_calls':0,'approval':False}
if __name__=='__main__':
    result=check(); print(json.dumps(result,indent=2))
