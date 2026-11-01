"""Checklist reconciliation checks: source, covariance, tangent, saved evidence.
No compiled/vendor calls. Historical dependency failures are retained separately.
"""
from pathlib import Path
import hashlib, json, math, re, sys, tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from atlas.model import load, defaults, interpret
from atlas.compiler import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    path=ROOT/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json'
    expected='1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c'
    assert sha(path)==expected
    model=load(path); params=defaults(model)
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        generate(tmp,[path])
        assert json.loads((Path(tmp)/'models.json').read_text())['models']==[model]
    retention=json.loads((ROOT/'docs/admission/burgers-approved-v1/source-retention.json').read_text())
    sources=[]
    for item in retention['sources']:
        p=Path(item['durable_private_path']); text=p.read_text()
        assert sha(p)==item['sha256']
        assert re.search(r"VERSION:\s*'9\.0\.184'",text)
        assert 'Updated: Dec 11, 2025' in text
        assert '<title>' in text and 'Model' in text
        sources.append({'id':item['id'],'sha256':sha(p),'private_path':str(p),'version':'9.0.184'})
    audit=ROOT/'docs/ingestion/burgers-itasca900/checklist-audit-v1'
    for name,digest in json.loads((audit/'manifest.json').read_text()).items():
        assert sha(audit/name)==digest,name
    for item in json.loads((audit/'checks.json').read_text()):
        assert item['returncode']==0 and sha(audit/item['output'])==item['sha256']

    def evaluate(s,k,d):
        out=interpret(model,{'sigma':s,'ek':k},None,d,params,time=4)
        return list(out['sigma'].v)+list(out['ek'].v)
    def tensor(v):
        a,b,c,d,e,f=v; rt=math.sqrt(2)
        return [[a,d/rt,f/rt],[d/rt,b,e/rt],[f/rt,e/rt,c]]
    def rotate(v,q):
        a=tensor(v)
        r=[[sum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
        return [r[0][0],r[1][1],r[2][2],math.sqrt(2)*r[0][1],math.sqrt(2)*r[1][2],math.sqrt(2)*r[0][2]]
    sigma=[140000,80000,80000,12000,-8000,4000]
    kelvin=[.002,-.001,-.001,.0003,-.0002,.0001]
    d=[.001,-.0002,-.0001,.0003,-.0004,.0002]
    rates=evaluate(sigma,kelvin,d)
    q=[[float(i==j)-2*[1,2,3][i]*[1,2,3][j]/14 for j in range(3)] for i in range(3)]
    transformed=evaluate(rotate(sigma,q),rotate(kelvin,q),rotate(d,q))
    target=rotate(rates[:6],q)+rotate(rates[6:],q)
    covariance=max(abs(x-y)/max(1,abs(y)) for x,y in zip(transformed,target))
    assert covariance<1e-12
    # Exact linear directional derivative with respect to loading: source
    # Kelvin rate has no direct D dependence; instantaneous stress tangent
    # is K I (I:D) + 2 Gm dev(D). Central difference is exact up to roundoff.
    zero=[0.]*6; base=evaluate(sigma,kelvin,zero); worst=0.
    for j in range(6):
        direction=[float(i==j) for i in range(6)]
        pos=evaluate(sigma,kelvin,direction); neg=evaluate(sigma,kelvin,[-x for x in direction])
        actual=[(a-b)/2 for a,b in zip(pos,neg)]
        tr=sum(direction[:3]); ref=[params['Kmod']*tr*(i<3)+2*params['Gm']*(direction[i]-(tr/3 if i<3 else 0)) for i in range(6)]+[0.]*6
        worst=max(worst,max(abs(x-y)/max(1,abs(y)) for x,y in zip(actual,ref)))
    assert worst<1e-12
    return {'identity':'REVIEW-burgers-checklist-v2','model_sha256':expected,
            'current_load_generate':'pass','retained_sources':sources,
            'audit_original_commands_verified':5,'covariance_scaled_error':covariance,
            'instantaneous_loading_tangent_scaled_error':worst,
            'tangent_scope':'instantaneous fixed-state source rate tangent; no finite-step/FE tangent claim',
            'compiled_calls':0,'builds':0,'experimental_validation':'not_assessed'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
