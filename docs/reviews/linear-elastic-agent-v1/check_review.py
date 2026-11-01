"""Independent source/algebra and saved-data review; no candidate execution.
Usage: python3 -B check_review.py --repo PATH --output PATH
"""
import argparse, hashlib, json, math
from fractions import Fraction as F
from pathlib import Path

ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.repo.resolve()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seen={}
def inspect(p):
    p=Path(p);seen[str(p.relative_to(r)) if p.is_relative_to(r) else str(p)]=sha(p);return p
m=read(inspect(r/'models/linear-elastic.json'))
assert sha(r/'models/linear-elastic.json')=='33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041'
receipts=read(inspect(r/'docs/ingestion/linear-elastic/source-receipts.json'));sources=[]
for e in receipts:
    p=inspect(r/'.local/private-sources/linear-elastic'/e['url'].split('/')[-1]);assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'];sources.append({'path':str(p),'url':e['url'],'sha256':sha(p),'verified':True})
# Stiffness expressed independently as lambda tr(d)I+2mu d.
regimes=[]
for nu in [F(-99,100),F(-1,5),F(1,4),F(49,100),F(499,1000)]:
    E=F(30000000);mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));bulk=E/(3*(1-2*nu));assert bulk==lam+2*mu/3 and mu>0 and bulk>0
    for j in range(6):
        d=[F(i==j) for i in range(6)];tr=sum(d[:3]);source=[2*mu*d[i]+(lam*tr if i<3 else 0) for i in range(6)];atlas=[2*mu*(d[i]-(tr/3 if i<3 else 0))+(bulk*tr if i<3 else 0) for i in range(6)];assert source==atlas
    regimes.append(str(nu))
# Exact covariance on a rational oblique orthogonal basis: fixed passive frame only.
Q=[[F(1,3),F(2,3),F(2,3)],[F(2,3),F(1,3),F(-2,3)],[F(-2,3),F(2,3),F(-1,3)]]
rot=lambda A:[[sum(Q[i][k]*A[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)]for i in range(3)]
assert [[sum(Q[i][k]*Q[j][k] for k in range(3)) for j in range(3)]for i in range(3)]==[[F(i==j)for j in range(3)]for i in range(3)]
D=[[F(2),F(3),F(-4)],[F(3),F(-1),F(5)],[F(-4),F(5),F(7)]]
C=lambda A:[[F(12)*sum(A[k][k]for k in range(3))*int(i==j)+F(24)*A[i][j]for j in range(3)]for i in range(3)]
assert rot(C(D))==C(rot(D))
# Bookkeeping domain: finite stress need not imply admissible e.
e0=.7;critical=math.log1p(e0);counterexample_trace=critical+.01;negative=(1+e0)*math.exp(-counterexample_trace)-1;assert negative<0
parts=[.001,-.0007,.0002];v=1+e0
for t in parts:v*=math.exp(-t)
assert abs(v-(1+e0)*math.exp(-sum(parts)))<1e-15
# Independent closed-form reference; no imports from atlas or existing oracle.
def state(initial,d,E,nu):
    lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu));tr=math.fsum(d[:3])
    return [initial[i]+2*mu*d[i]+(lam*tr if i<3 else 0) for i in range(6)]+[(1+initial[6])*math.exp(-tr)-1]
# All material history is sigma/e: restarting from a saved accepted state
# reproduces chained updates algebraically; no serialized-runtime claim.
z0=[110000,90000,125000,1400,-900,650,.7]
d1=[.00031,-.00012,.00007,.00009,-.00005,.00011]
d2=[-.0001,.0002,-.00004,-.00003,.00002,.00001]
z1=state(z0,d1,3e7,.25);z2=state(z1,d2,3e7,.25)
zt=state(z0,[x+y for x,y in zip(d1,d2)],3e7,.25)
restart_stress_error=max(abs(x-y)for x,y in zip(z2[:6],zt[:6]));restart_void_error=abs(z2[6]-zt[6])
assert restart_stress_error<1e-9 and restart_void_error<1e-15
# Derivative is C for stress and -(1+e_new) tr(delta_de) for e;
# a central difference is an additional smooth-state diagnostic only.
h=1e-7;dplus=d1.copy();dminus=d1.copy();dplus[0]+=h;dminus[0]-=h
fd=(state(z0,dplus,3e7,.25)[6]-state(z0,dminus,3e7,.25)[6])/(2*h)
void_derivative_error=abs(fd+(1+z1[6]));assert void_derivative_error<2e-9
def fraction(actual,expected):
    assert len(actual)==len(expected)==7
    return max(abs(x-y)/((1e-4 if i<6 else 1e-10)+1e-10*abs(y))for i,(x,y)in enumerate(zip(actual,expected)))
envelope=read(inspect(r/'catalogue/evidence/linear-elastic-analytical-v1.json'));ref=envelope['artifacts'][0];assert sha(inspect(r/ref['path']))==ref['sha256'];report=read(r/ref['path']);assert len(report['cases'])==29
checks=[]
for c in report['cases']:
    params=list(map(float,c['arguments'][c['arguments'].index('--parameters')+1].split(',')));expected=state(c['initial'],c['total_strain'],*params[1:]);er=fraction(c['expected'],expected);ar=fraction(c['actual'],expected);assert er<=1 and ar<=1 and c['solver_ok'] is True and c['returncode']==0
    checks.append({'id':c['id'],'saved_expected_budget_fraction':er,'saved_actual_budget_fraction':ar})
# Qualified historical freeze: exact unchanged model and all saved evidence manifest entries.
s=r/'catalogue/investigations/laboratory-q-cancellation-v1';manifest=read(inspect(s/'manifest.json'));evidence=read(inspect(s/'evidence-manifest.json'));hash_count=0
for pins in (manifest,evidence):
    for p,h in pins.items():assert sha(s/p)==h,p;hash_count+=1
assert manifest['frozen/models/linear-elastic.json']==sha(r/'models/linear-elastic.json');inspect(s/'frozen/models/linear-elastic.json')
freeze=read(inspect(s/'prospective-freeze.json'));assert freeze['manifest_sha256']==sha(s/'manifest.json') and freeze['compiled_calls_at_freeze']==0
for role in ['native','wasm','post']:
    receipt=read(inspect(s/role/'receipt.json'));assert receipt['completed'] and receipt['manifest_sha256']==sha(s/'manifest.json') and all(c['exit_code']==0 for c in receipt['commands'])
# Raw result binding and independent elastic reference at every retained caller point.
raw=read(inspect(s/'post/backend-results.json.raw.json'));pairs=read(inspect(s/'post/backend-results.json'))['pairs'];journal=iter(raw);selected=[];point_checks=0;worst=0
physical=lambda x:{k:v for k,v in x.items()if k!='elapsed_ms'}
for row in pairs:
    for role in ['native','wasm']:
        o=next(journal);assert o['role']==role and physical(read_raw:=json.loads(o['raw']))==physical(row[role])
    if row['name'].startswith('legacy/'):
        for role in ['native','wasm']:
            o=next(journal);assert o['role']==role and physical(json.loads(o['raw']))==physical(row['direct_'+role])==physical(row[role])
    if row['name'].startswith(('legacy/','current/')):
        o=next(journal);assert o['role']=='wasm' and physical(json.loads(o['raw']))==physical(row['wasm']) and row['roundtrip_replayed'] is True
    spec=row['specification']
    if spec['model']!='linear-elastic':continue
    E,nu=spec['parameters'][1:];G=E/(2*(1+nu));protocol=spec['protocol'];maximum=0
    for role in ['native','wasm']:
        response=row[role]
        for pt in response['points']:
            c=pt['control'];x=c/(3*G) if protocol==3 else c
            radial=0 if protocol==0 else (-nu*x if protocol==1 else (x if protocol==4 else -x/2))
            d=[x,radial,radial,0,0,0]
            assert max(abs(v-w)for v,w in zip(pt['strain'],d))<=1e-10
            expected=state(spec['initial'],d,E,nu);f=fraction(pt['state'],expected);assert f<=1,(row['name'],role,f);maximum=max(maximum,f);point_checks+=1
            if protocol in (2,3):assert abs(pt['u']-(spec['initial'][1]-(expected[1]+expected[2])/2))<=1e-4+1e-10*abs(pt['u'])
    if row['name']=='limited-prefix':assert not row['native']['ok'] and not row['wasm']['ok'] and len(row['native']['points'])==len(row['wasm']['points'])==1 and row['native']['points'][0]['state']==spec['initial']
    else:assert row['native']['ok'] and row['wasm']['ok']
    worst=max(worst,maximum);selected.append({'name':row['name'],'points_per_backend':len(row['native']['points']),'ok':row['native']['ok'],'independent_reference_max_budget_fraction':maximum})
assert next(journal,None)is None and len(selected)==13
result={'kind':'independent-linear-elastic-agent-check-v1','passed':True,'candidate_calls':0,'model_sha256':sha(r/'models/linear-elastic.json'),'verified_original_sources':sources,'exact_rational_stiffness_column_checks':30,'nu_regimes':regimes,'exact_oblique_covariance_check':True,'paired_sign_reversal':'C*(-de)=-C*de; stress and strain signs change together','algebraic_restart':{'stress_error_Pa':restart_stress_error,'void_error':restart_void_error,'runtime_restart_executed':False},'void_derivative_central_difference_error':void_derivative_error,'bookkeeping':{'composition_error':abs(v-(1+e0)*math.exp(-sum(parts))),'domain_boundary_trace':critical,'negative_e_counterexample_trace':counterexample_trace,'negative_e':negative,'required_behavior':'reject complete increment and retain committed parent; not a physical compaction prediction'},'analytical_report_cases':checks,'historical_freeze_manifest_entries_verified':hash_count,'historical_backend_elastic_pairs':selected,'historical_backend_elastic_point_checks':point_checks,'historical_backend_worst_budget_fraction':worst,'inspected_bindings':seen,'limitations':['Saved data only; no fresh compiled/interface/browser execution.','Independent oracle references use retained net/control inputs, not solver reported strain to construct elastic expected state.','No all-parameter conditioning or finite-rotation qualification.']}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ('inspected_bindings','analytical_report_cases','verified_original_sources','historical_backend_elastic_pairs')},indent=2))
