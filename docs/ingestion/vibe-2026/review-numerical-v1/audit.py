"""Independent review checks; read originals, write only this review directory."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, sys

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
WORK=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for folder in ['source-v2','reference-v1']:
    p=ROOT/'docs/ingestion/vibe-2026'/folder/'manifest.json'
    m=json.loads(p.read_text())
    for row in m['files']:
        q=ROOT/row['path'];assert sha(q)==row['sha256'];assert q.stat().st_size==row['bytes']
    checks[folder]={'manifest_sha256':sha(p),'verified_files':len(m['files'])}
receipt=json.loads((ROOT/'docs/ingestion/vibe-2026/source-v2/source-receipt.json').read_text())
for row in receipt['private_artifacts']+[receipt['user_original']]:
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
checks['private_source_artifacts']=10
ref=ROOT/'docs/ingestion/vibe-2026/reference-v1'
assert (ref/'point-results.json').read_bytes()==(OUT/'reproduced-reference/point-results.json').read_bytes()
checks['point_reference_exact_bytes']=True
trajectory_checks=[]
for ident in ['near_hold_1000','near_hold_3600','dry_hold_1000','mixed_ramp_100','hydraulic_reversal_100']:
    a=json.loads((ref/(ident+'.json')).read_text());b=json.loads((OUT/'reproduced-reference'/(ident+'.json')).read_text())
    del a['runtime_seconds'];del b['runtime_seconds'];assert a==b
    trajectory_checks.append({'id':ident,'all_numeric_contents_exact':True,'partition_convergence':a['partition_convergence'],'precision_convergence':a['precision_convergence']})
checks['trajectory_reproductions']=trajectory_checks

# Independent rational checks of rank-one inverse: A9 is a linear action,
# not a scalar subtraction from a fourth-order tensor.
identity_cases=0
for b,c,d in [(F(-2,7),F(3,11),F(4,13)),(F(0),F(0),F(0)),(F(1,10),F(-3,10),F(2,9))]:
    q=b+c+3*c*d;den=1+3*q;assert den
    for v in [(F(2),F(-3),F(4),F(5),F(-6),F(7)),(F(1),)*3+(F(0),)*3]:
        tr=sum(v[:3]);B=[x+q*tr if i<3 else x for i,x in enumerate(v)]
        inv=[x-q/den*sum(B[:3]) if i<3 else x for i,x in enumerate(B)]
        assert inv==list(v);identity_cases+=6
checks['rational_B_inverse_components']=identity_cases

# Derive A30's stable form directly by exact Cartesian invariants for
# symmetric sigma=-pI+z, trace(z)=0, including nonzero shear.
stable_cases=0
for p in [F(7),F(1000),F(10000000)]:
 for a,b,c,d,e in [(1,-2,3,-4,5),(-3,2,-1,5,-2),(0,0,0,0,0)]:
    z=[[F(a),F(c),F(e)],[F(c),F(b),F(d)],[F(e),F(d),F(-a-b)]]
    sig=[[z[i][j]-(p if i==j else 0) for j in range(3)] for i in range(3)]
    def det(A):return sum(A[0][j]*(A[1][(j+1)%3]*A[2][(j+2)%3]-A[1][(j+2)%3]*A[2][(j+1)%3]) for j in range(3))
    tr=sum(sig[i][i] for i in range(3));sq=sum(x*x for row in sig for x in row)
    I2=(sq-tr*tr)/2;I3=det(sig);zsq=sum(x*x for row in z for x in row)
    assert (9*I3+tr*I2)/(I3+tr*I2)==(3*p*zsq+9*det(z))/(8*p**3-p*zsq+det(z));stable_cases+=1
checks['rational_Fm_cases']=stable_cases

sys.path.insert(0,str(ref))
from oracle import D, localcontext, params, initial, algebra, rate, ZERO, DomainError, stringify
with localcontext() as ctx:
    ctx.prec=100;p=params();y,s,T=initial(p)
    # Full A12 direction, rather than the undefined Lode coordinate alone,
    # approaches isotropy from several unrelated deviatoric directions.
    approach=[]
    for direction in [[2,-1,-1,3,-2,1],[-1,2,-1,-1,4,-3],[1,1,-2,0,0,0]]:
        errors=[]
        for eps in ['1','.001','.000001']:
            yy=[x+D(eps)*D(v) for x,v in zip(y,direction+[0,0])]
            q=algebra(yy,s,T,ZERO,p);target=-1/D(3).sqrt()
            errors.append(max(abs(q['direction'][i][j]-(target if i==j else ZERO)) for i in range(3) for j in range(3)))
        assert errors[2]<errors[1]<errors[0]
        approach.append({'deviatoric_direction':direction,'maximum_direction_errors':errors})
    checks['hydrostatic_full_direction_approach']=stringify(approach)
    # Independent exact-state refusal corpus, then immediate valid reuse.
    invalid=[]
    for label in ['zero_suction','negative_suction','negative_macrovoid','Iv_nonpositive','scan_below_zero','scan_above_one','nonpositive_micro_pressure']:
        yy=list(y);ss=s;tt=T
        if label=='zero_suction':ss=ZERO
        if label=='negative_suction':ss=D(-1)
        if label=='negative_macrovoid':yy[6]=D('.1')
        if label=='Iv_nonpositive':tt=D(100)
        if label=='scan_below_zero':yy[7]=D('-.01')
        if label=='scan_above_one':yy[7]=D('1.01')
        if label=='nonpositive_micro_pressure':yy[:3]=[-2*s]*3
        try:rate(yy,ss,tt,ZERO,ZERO,[ZERO]*6,p)
        except (DomainError,ArithmeticError) as e:invalid.append({'id':label,'reason':str(e)})
        else:raise AssertionError('invalid state accepted')
    rate(y,s,T,ZERO,ZERO,[ZERO]*6,p)
    checks['reference_invalid_refusals_and_valid_reuse']=invalid

sys.path.insert(0,str(WORK))
from atlas.model import validate
from atlas.controlled_time import evaluate_stage
model_path=WORK/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
m=json.loads(model_path.read_text());validate(m)
candidate=WORK/'docs/ingestion/vibe-2026/candidate-v1'
old_path=candidate/'preimages/59141dce52d116e31b5663146c4356022ac93ae85403534110b7faad288de725-vibe-2026-explicit-appendix-a.json'
old=json.loads(old_path.read_text())
assert sha(old_path)=='59141dce52d116e31b5663146c4356022ac93ae85403534110b7faad288de725'
assert old['domain'].count('OA>0')==1 and m['domain'].count('OA>=1')==1
restricted=json.loads(json.dumps(old));restricted['domain'][restricted['domain'].index('OA>0')]='OA>=1'
assert restricted==m
checks['candidate']={'model_sha256':sha(model_path),'revision2_sha256':sha(old_path),'only_revision3_difference':'OA>0 replaced by OA>=1'}
param={k:v['default'] for k,v in m['parameters'].items()}
point=json.loads((ref/'point-results.json').read_text())['cases'][1]['reference']
base=list(map(float,point['initial_state']))
controls={'strain':[0.]*6,'suction':float(point['suction_Pa']),'temperature':float(point['temperature_K'])}
rates={'strain':[0.]*6,'suction':0.,'temperature':0.}
def state(y):return {'sigma_net':y[:6],'e':y[6],'a_scan':y[7]}
refusals=[]
for label in ['zero_suction','negative_suction','negative_macrovoid','Iv_nonpositive','scan_below_zero','scan_above_one','nonpositive_micro_pressure']:
    yy=list(base);cc=json.loads(json.dumps(controls))
    if label=='zero_suction':cc['suction']=0.
    if label=='negative_suction':cc['suction']=-1.
    if label=='negative_macrovoid':yy[6]=.1
    if label=='Iv_nonpositive':cc['temperature']=100.
    if label=='scan_below_zero':yy[7]=-.01
    if label=='scan_above_one':yy[7]=1.01
    if label=='nonpositive_micro_pressure':yy[:3]=[-2*cc['suction']]*3
    before=json.loads(json.dumps([yy,cc,param,rates]))
    try:evaluate_stage(m,state(yy),param,11.,cc,rates)
    except (ValueError,ArithmeticError,TypeError) as e:refusals.append({'id':label,'exception':type(e).__name__,'reason':str(e)})
    else:raise AssertionError('candidate accepted invalid state')
    assert [yy,cc,param,rates]==before
    evaluate_stage(m,state(base),param,11.,controls,rates)
checks['candidate_invalid_refusals_inputs_unchanged_valid_reuse']=refusals
outside=list(base);outside[:3]=[x*1.02 for x in base[:3]]
_,observables,_=evaluate_stage(old,state(outside),param,11.,controls,rates)
assert 0<observables['overconsolidation']<1
try:evaluate_stage(m,state(outside),param,11.,controls,rates)
except ValueError:pass
else:raise AssertionError('revision3 still admits outside-ASBS witness')
checks['resolved_domain_witness']={'OA':observables['overconsolidation'],'revision2':'accepted','revision3':'refused'}
with localcontext() as ctx:
    ctx.prec=80;dy,ds,dT=initial(params(),dry=True)
    try:algebra(dy,ds,D(200),ZERO,params())
    except DomainError as e:assert str(e)=='Iv nonpositive'
    else:raise AssertionError('viscosity boundary not refused')
from atlas.controlled_time import inputs_at
from atlas.dsl import I, Sym, evaluate, parse
dry_state=state(list(map(float,dy)));dry_controls={'strain':[0.]*6,'suction':float(ds),'temperature':200.}
env={'I':I,**param,**inputs_at(m,11.,dry_controls,rates)}
for field in m['state']:
    value=dry_state[field['name']];env[field['name']]=Sym(tuple(value)) if field['shape']=='sym' else value
for field in m['derived']:env[field['name']]=evaluate(parse(field['expr']),env)
failed=[predicate for predicate in m['domain'] if not evaluate(parse(predicate),env)]
assert failed==['Iv>0']
checks['isolated_negative_viscosity_witness']={'temperature_K':200,'suction_Pa':float(ds),'state':dry_state,'Iv':env['Iv'],'only_failed_candidate_predicate':failed,'reference_reason':'Iv nonpositive'}

(OUT/'audit-results.json').write_text(json.dumps(checks,indent=2)+'\n')
print('all integrity, exact numerical reproduction, rational identity and hydrostatic approach checks pass')
