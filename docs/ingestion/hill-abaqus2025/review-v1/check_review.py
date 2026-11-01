"""Independent reviewer checks: no compiled calls or production equation imports."""
from pathlib import Path
from decimal import Decimal, localcontext
import hashlib, importlib.util, json
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'docs/ingestion/hill-abaqus2025'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    count=0
    def check(test):
        nonlocal count
        assert test
        count+=1
    receipts=load(BASE/'source-v1/source-receipts.json')
    for s in receipts['sources']:check(sha(Path(s['private_path']))==s['sha256'])
    freeze=load(BASE/'execution-v1/source-freeze-v2.json')
    for f,h in freeze['files'].items():check(sha(Path('/private/tmp/atlas-hill-delivery-v1')/f)==h)
    build=load(BASE/'execution-v1/build-receipt.json')
    for p,h in build['artifacts'].items():check(sha(Path(p))==h)
    refs=load(BASE/'execution-v1/references.json');m=ROOT/'models/research/hill/hill-abaqus2025-perfect-be.json'
    check(sha(m)==refs['model_sha256']=='1f98a70a68098d95804639e3abeb69da57e7ceeaf302d621e4738db4340e2621')
    check(sha(BASE/'source-v1/check_algebra.py')==refs['oracle_sha256'])
    # Separate literal source quadratic and gradient, not the production matrix or DSL.
    def q2(s,p):
        f,g,h,l,mm,n=p[4:]
        x,y,z,xy,yz,xz=s
        return f*(y-z)**2+g*(z-x)**2+h*(x-y)**2+n*xy**2+l*yz**2+mm*xz**2
    def normal(s,p):
        f,g,h,l,mm,n=p[4:];x,y,z,xy,yz,xz=s
        return [g*(x-z)+h*(x-y),f*(y-z)+h*(y-x),f*(z-y)+g*(z-x),n*xy,l*yz,mm*xz]
    d=lambda v:Decimal(str(v))
    kktmax=Decimal(0);closedmax=Decimal(0)
    with localcontext() as ctx:
        ctx.prec=75
        for case in refs['cases']:
            p=list(map(d,case['parameters']));sn=list(map(d,case['initial'][:6]));mu=p[2];y=p[3]
            for de,row in zip(case['increments'],case['expected']):
                de=list(map(d,de));s=list(map(d,row[:6]));gam=d(row[6]);tr=sum(de[:3]);n=normal(s,p)
                trial=[sn[i]+p[1]*tr+2*mu*(de[i]-tr/3) if i<3 else sn[i]+2*mu*de[i] for i in range(6)]
                residual=max(abs(s[i]-trial[i]+2*mu*gam*n[i]/y) for i in range(6));kktmax=max(kktmax,residual)
                check(residual<Decimal('1e-8'))
                check(gam>=0);check(q2(s,p)<=y*y+Decimal('.0001'))
                if gam>Decimal('1e-15'):check(abs(q2(s,p)-y*y)<Decimal('.0001'))
                # Closed shear return and isotropic radial return, distinct from bisection oracle.
                active=[i for i,v in enumerate(trial) if v]
                if len(active)==1 and active[0]>=3:
                    i=active[0];a=p[{3:9,4:7,5:8}[i]];limit=y/a.sqrt();target=max(-limit,min(limit,trial[i]));gc=max(Decimal(0),y/(2*mu*a)*(abs(trial[i])/limit-1))
                    closedmax=max(closedmax,abs(s[i]-target));check(abs(s[i]-target)<Decimal('1e-8'));check(abs(gam-gc)<Decimal('1e-16'))
                if p[4:]==list(map(d,[.5,.5,.5,1.5,1.5,1.5])):
                    mean=sum(trial[:3])/3;dev=[v-mean if i<3 else v for i,v in enumerate(trial)];qt=(Decimal('1.5')*sum(v*v for v in dev)).sqrt();fac=min(Decimal(1),y/qt) if qt else Decimal(1)
                    target=[v*fac+(mean if i<3 else 0) for i,v in enumerate(dev)]
                    check(max(abs(s[i]-target[i]) for i in range(6))<Decimal('1e-8'));check(abs(gam-max(Decimal(0),(qt-y)/(3*mu)))<Decimal('1e-16'))
                sn=s
    # Reproduce immutable saved backend assessment only; do not invoke run/native.
    spec=importlib.util.spec_from_file_location('assessor',BASE/'execution-v1/qualify.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reports={}
    for backend in ['native','wasm']:
        reports[backend]=module.assess(load(BASE/f'execution-v1/{backend}-raw.json'))
        check(reports[backend]==load(BASE/f'execution-v1/{backend}-assessment.json'))
    nraw=load(BASE/'execution-v1/native-raw.json');wraw=load(BASE/'execution-v1/wasm-raw.json');parity=[0.,0.]
    for nc,wc in zip(nraw,wraw):
        for nr,wr in zip(nc['runs'],wc['runs']):
            for n,w in zip(nr,wr):
                for i,(a,b) in enumerate(zip(n['state'],w['state'])):
                    error=abs(a-b);parity[i==6]=max(parity[i==6],error);check(error<=(1e-12 if i==6 else 1e-7))
    rollback=load(BASE/'execution-v1/rollback-raw.json');initial=next(c['initial'] for c in refs['cases'] if c['id']=='mixed-nonproportional')
    check(rollback['before']==rollback['after']);check(rollback['before']['ok'])
    for k in ['failed','native']:check(not rollback[k]['ok']);check(rollback[k]['state']==initial)
    neg=load(BASE/'execution-v1/negative-results-v2.json')
    for row in neg['rows']:
        check(not row['native']['ok']);check(not row['wasm']['ok']);check(row['recovered']['ok'])
        if row['id']=='outside-yield':
            for be in ['native','wasm']:check(row[be]['state']==row[be]['initial'])
        else:
            for be in ['native','wasm']:check('state' not in row[be])
    return dict(status='pass',checks=count,compiled_calls=0,private_source_hashes=5,source_freeze_files=len(freeze['files']),backend_assessments=reports,reference_KKT_max_Pa=str(kktmax),closed_shear_max_Pa=str(closedmax),parity_stress_Pa=parity[0],parity_gamma=parity[1],retained_failure='Original negative.mjs full-state-echo policy fails for prevalidation responses lacking state; separate V2 diagnostic and actual material-failure rollback reviewed without reclassifying original gate.')
if __name__=='__main__': print(json.dumps(main(),indent=2))
