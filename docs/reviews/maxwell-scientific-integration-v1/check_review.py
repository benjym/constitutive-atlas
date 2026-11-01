"""Independent Maxwell algebra and read-only saved-evidence review.
Run: python3 -B docs/reviews/maxwell-scientific-agent-v1/check_review.py
No compiled/vendor execution, calls to production evaluators, or input writes.
"""
import ast
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path
import tarfile
import sys
import importlib.util

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/ingestion/maxwell-itasca900'
INT = BASE / 'integration-v1'
examined = {}

def read(path):
    path = Path(path)
    if not path.is_absolute(): path = ROOT / path
    data = path.read_bytes()
    key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    examined[key] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    return data

def obj(path): return json.loads(read(path))
def digest(path): return hashlib.sha256(read(path)).hexdigest()
def close(a,b):
    assert len(a)==len(b)
    return max(abs(x-y) for x,y in zip(a,b))
def split(v):
    mean=sum(v[:3])/3
    return mean,[x-mean if i<3 else x for i,x in enumerate(v)]
def rhs(z,d,p):
    K,G,eta=p;mean,s=split(z);tr=sum(d[:3]);_,dev=split(d)
    return [(K*tr if i<3 else 0)+2*G*dev[i]-G/eta*s[i] for i in range(6)]
def solution(z,d,p,t):
    K,G,eta=p;mean,s=split(z);_,q=split(d);r=math.exp(-G/eta*t)
    return [(mean+K*sum(d[:3])*t if i<3 else 0)+r*s[i]-2*eta*math.expm1(-G/eta*t)*q[i] for i in range(6)]

def main():
    instructions=['AGENTS.md','IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/RESEARCH_CHARTER.md','docs/STATUS.md','docs/admission/REVIEWER_INSTRUCTIONS.md','docs/FORMULATION_CONTRACT.md','schemas/model-v0.3.schema.json','docs/TIME_ODE_API.md','docs/TIMED_SCHEDULES.md']
    for p in instructions: read(p)
    # All local packet files are examined: JSON/report contents and source code;
    # the archive is inspected as bytes/member hashes, never extracted/executed.
    for p in sorted(BASE.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts: read(p)
    for p in ['tests/test_maxwell.py','tools/test_maxwell_wasm.mjs','cpp/include/atlas/time.hpp','cpp/include/atlas/schedule.hpp','atlas/compiler.py','cmake/maxwell/CMakeLists.txt','examples/maxwell/README.md']:
        read(p)
    for p in (ROOT/'examples/maxwell').glob('*.json'): read(p)
    modelpath='models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'
    model=obj(modelpath)
    assert read(modelpath)==read(BASE/'candidate-v03.json')
    catalogue=hashlib.sha256(json.dumps([model],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    pinchecks=[]
    for mp in [BASE/'manifest.json',INT/'manifest.json',INT/'execution-freeze.json',INT/'transaction-driver-freeze.json',INT/'parity-driver-freeze.json',INT/'parity-driver-v2-freeze.json']:
        m=obj(mp); entries=m.get('files',[m] if 'path' in m else [])
        for e in entries:
            actual=digest(e['path']); assert actual==e['sha256'],(e['path'],actual,e['sha256'])
        pinchecks.append(dict(manifest=str(mp.relative_to(ROOT)),verified=len(entries)))
    for e in obj(BASE/'source-receipts.json')['sources']:
        assert digest(e['private_path'])==e['sha256']
    archive=[]
    with tarfile.open(INT/'source-closure.tar.gz') as t:
        members={m.name:m for m in t.getmembers() if m.isfile()}
        for e in obj(INT/'execution-freeze.json')['files']:
            actual=hashlib.sha256(t.extractfile(members[e['path']]).read()).hexdigest()
            assert actual==e['sha256']; archive.append(e['path'])
    artifacts=[]
    for e in obj(INT/'manifest.json')['private_artifacts']:
        actual=digest(e['path']); assert actual==e['sha256']
        artifacts.append(dict(path=e['path'],sha256=actual,inspection='hash only; not executed'))
    # Exact algebra from Eq4, independently rearranged, including rate factor.
    algebra=[]
    for K,G,eta in [(F(20),F(12),F(24)),(F(7),F(3),F(11)),(F(5),F(19),F(2))]:
        for h in [F(1,100),F(1),F(8)]:
            x=G*h/(2*eta);old=F(7);inc=F(1,30)
            new=((1-x)*old+2*G*inc)/(1+x)
            assert (new-old)/h==2*G*inc/h-G/(2*eta)*(new+old)
        # Oedometer derives from axial equilibrium and two zero lateral rates.
        A=K+4*G/3;a=2*G/A;b=K*G/(eta*A);c=4*G/(3*A);P=F(13)
        for r in [F(1),F(2,7),F(0)]:
            z=[P*(1-a*r),P*(1-a*r),P,0,0,0]
            d=[0,0,P/K*c*b*r,0,0,0]
            assert rhs(z,d,[K,G,eta])==[P*a*b*r,P*a*b*r,0,0,0,0]
        assert P/K*(1-c)==P/A
        z=[F(8),F(3),F(-2),F(4),F(5),F(-1)]
        d=[F(1,3),F(1,7),F(-1,2),F(3,11),0,F(-1,13)]
        zdot=rhs(z,d,[K,G,eta]);p,s=split(z);pd,sd=split(zdot)
        work=sum(x*y for x,y in zip(z,d))
        stored_dot=p*pd/K+sum(x*y for x,y in zip(s,sd))/(2*G)
        assert work-stored_dot==sum(x*x for x in s)/(2*eta)>0
        assert rhs([-x for x in z],[-x for x in d],[K,G,eta])==[-x for x in zdot]
        algebra.append(dict(K=str(K),G=str(G),eta=str(eta),oedometer_rate=str(b),passed=True))
    # Independent Cartesian shear work/packing identity challenges factors of 2.
    raw_shear=F(9);raw_rate=F(2,7)
    assert 2*raw_shear*raw_rate==F(2)*raw_shear*raw_rate
    mandel_work=(math.sqrt(2)*float(raw_shear))*(math.sqrt(2)*float(raw_rate))
    assert abs(mandel_work-float(2*raw_shear*raw_rate))<1e-13
    # Saved references are challenged without calling their generation function.
    frozen=obj(INT/'reference-cases.json')['cases']
    Z=[140000,80000,80000,3000,-2000,1000];P=[20e6,12e6,24e6];zero=[0]*6
    def ref(ident,t):
        if ident.startswith('refine-') or ident in ['relaxation-schedule','restart-relax']:
            return solution(Z,zero,P,t),zero
        if ident in ['creep-schedule','creep-one-sample','restart-creep']:
            return Z,[s*t/(2*P[2]) for s in split(Z)[1]]
        if ident=='oedometer':
            K,G,eta=P;A=K+4*G/3;r=math.exp(-K*G/(eta*A)*t);load=1e5
            return [load*(1-2*G/A*r)]*2+[load,0,0,0],[0,0,load/K*(1-4*G/(3*A)*r),0,0,0]
        assert ident=='load-hold-reverse'
        rate=[.001,-.0005,-.0005,.0004,-.0003,.0002]
        if t<=1:return solution(Z,rate,P,t),[x*t for x in rate]
        at1=solution(Z,rate,P,1)
        if t<=2:return solution(at1,zero,P,t-1),rate
        at2=solution(at1,zero,P,1)
        return solution(at2,[-x for x in rate],P,t-2),[x*(3-t) for x in rate]
    errors={}; endpoint_checks={};reference_max=0; original_assessments={}
    # Safe import: inspected main block is guarded and no imported path invokes
    # execution. Call only the saved-data assessor; never its native collector.
    sys.path.insert(0,str(ROOT))
    spec=importlib.util.spec_from_file_location('maxwell_saved_review',ROOT/'tests/test_maxwell.py')
    assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
    for backend in ['native','wasm']:
        rows=obj(INT/f'{backend}-raw.json');transaction_cases=obj(INT/f'{backend}-transaction-cases.json')['cases']
        transactions=obj(INT/f'{backend}-transactions-raw.json')
        assert len(rows)==24 and len(transactions)==14
        original_assessments[backend]=assessor.assess_rows(frozen,rows)
        original_assessments[backend+'_transactions']={c['id']:assessor.assess(c,json.loads(r['calls'][0]['stdout'])) for c,r in zip(transaction_cases,transactions)}
        backend_errors={};max_equilibrium=0;regular=0
        for c,row in zip(frozen+transaction_cases,rows+transactions):
            assert c['id']==row['id'] and len(row['calls'])==2
            parsed=[json.loads(call['stdout']) for call in row['calls']]
            assert parsed[0]==parsed[1]
            for call,data in zip(row['calls'],parsed):
                assert call['returncode']==(0 if c['ok'] else 1) and data['ok']==c['ok']
                if not c['ok']:
                    if c['id']=='late-budget-rollback':assert data['state']==Z and data['time']==3 and data['substeps']>0
                    if c['id']=='schedule-budget-rollback':assert data['points'][-1]['state']==Z and data['points'][-1]['time']==0
                    continue
                assert data['catalogue_hash']==catalogue
                if c['kind']=='direct':
                    p=list(map(float,c['args'][1].split(',')));z=list(map(float,c['args'][2].split(',')));d=list(map(float,c['args'][3].split(',')))
                    expected=solution(z,d,p,c['args'][5]);err=close(expected,data['state'])
                    reference_max=max(reference_max,close(expected,c['expected']))
                    assert err<=c['tolerance'];backend_errors[c['id']]=err
                else:
                    worst=0
                    for pt in data['points']:
                        expected,strain=ref(c['id'],pt['time']);worst=max(worst,close(expected,pt['state']))
                        assert close(strain,pt['strain'])<=c['strain_tolerance']
                        if pt['side']=='left' and pt['segment']>=0:
                            regular+=1
                            f=rhs(pt['state'],pt['strain_rate'],P)
                            for i,controlled in enumerate(pt['strain_rate']):
                                control=c['specification']['segments'][pt['segment']]['controls'][i]
                                if control['quantity']=='stress' and control['kind']=='hold':max_equilibrium=max(max_equilibrium,abs(f[i]))
                    assert worst<=c['tolerance'];backend_errors[c['id']]=worst
        assert regular>0
        errors[backend]=backend_errors;endpoint_checks[backend]=dict(regular_points=regular,maximum_held_stress_rate_residual_Pa_per_s=max_equilibrium)
    # Replay just the pure parity function via AST; omit its module-level I/O.
    parity=[]
    for filename in ['compare_backends.py','compare_backends_v2.py']:
        tree=ast.parse(read(INT/filename));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compare')
        env=dict(math=math,COUNT=0,MAX_STRESS=0,MAX_STRAIN=0)
        exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'),env)
        failure=None
        try:
            for suffix in ['raw','transactions-raw']:
                native=obj(INT/f'native-{suffix}.json');wasm=obj(INT/f'wasm-{suffix}.json')
                assert len(native)==len(wasm)
                for n,w in zip(native,wasm):
                    assert n['id']==w['id'] and len(n['calls'])==len(w['calls'])==2
                    for nc,wc in zip(n['calls'],w['calls']):env['compare'](json.loads(nc['stdout']),json.loads(wc['stdout']))
        except AssertionError as e:failure=repr(e)
        parity.append(dict(assessor=filename,passed=failure is None,failure=failure,numeric_comparisons=env['COUNT'],maximum_stress=env['MAX_STRESS'],maximum_strain_rate=env['MAX_STRAIN']))
    assert parity[0]['failure'] and parity[1]['passed']
    # Exploratory analytical counterexample, not a compiled observation: legal
    # loose tolerance can accept energy growth with direct explicit midpoint.
    stability=lambda x:1-x+x*x/2
    full=stability(F(6));two=stability(F(3))**2
    estimator_upper=abs(two-full)/(3*F(1,2)*two)
    assert full==13 and two==F(25,4) and estimator_upper==F(18,25)<1
    result=dict(passed=True,review='AI technical review only',model_sha256=digest(modelpath),catalogue_hash=catalogue,pinchecks=pinchecks,source_closure_verified_members=len(archive),private_artifacts=artifacts,independent_exact_algebra=algebra,saved_reference_maximum_difference_Pa=reference_max,saved_trajectory_errors_Pa=errors,original_saved_assessor_replay=original_assessments,exploratory_endpoint_equilibrium=endpoint_checks,parity_replay=parity,counterexamples=dict(literal_isotropic_deviator_trace=6,central_difference_h4tau_multiplier='-1/3',exact_h4tau_multiplier=math.exp(-4),minimum_declared_tau_seconds=1e-42,minimum_supported_half_step_seconds=1e-12,legal_loose_tolerance_direct_hold=dict(h_over_tau=6,relative_tolerance=0.5,full_multiplier=str(full),accepted_two_half_multiplier=str(two),error_estimator_upper_bound=str(estimator_upper),elastic_energy_ratio=str(two**2),compiled_observation=False)),compiled_executions=0,vendor_executions=0)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'inputs.json').write_text(json.dumps(dict(review_id='SCI-maxwell-agent-v1',date='2026-11-01',source_access='Four pinned original private HTML pages read; no PDF or source website refresh; figures, called parameter file and Jaeger book not inspected.',archive_inspection='All 92 members hashed against freeze; not all unrelated engine files technically reviewed.',files=[dict(path=p,**v) for p,v in sorted(examined.items())]),indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
