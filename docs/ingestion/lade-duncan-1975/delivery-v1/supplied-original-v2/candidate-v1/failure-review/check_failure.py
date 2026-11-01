"""Read-only independent Python challenge of retained native reentry diagnosis.

No compiler/build/compiled execution; no root packet writes. Reads immutable
candidate/native results and reproduces only existing interpreter preparation.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[7]))
from atlas.model import load, defaults, evaluation_environment, prepare_increment, interpret
from atlas.dsl import parse,evaluate
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
model=load(BASE/'model.json'); assert h(BASE/'model.json')=='5d02250d99a70bf0dbb0783e098ccb8738544b5e04de876f0d295057036ec8c1'
study=json.loads((BASE/'native-triaxial-results.json').read_text());diagnostic=json.loads((BASE/'native-onset-diagnostic-v1.json').read_text())
raw_checks=[]
for row in study['requests']:
    p=Path(row['raw_path']); assert h(p)==row['raw_sha256']
    d=json.loads(p.read_text()); assert d['ok']==row['ok']
    raw_checks.append({'path':str(p),'sha256':h(p),'ok':d['ok']})
assert len(raw_checks)==24 and sum(r['ok'] for r in raw_checks)==7 and study['passed'] is False
snap=json.loads((BASE/'native-source-manifest.json').read_text());assert all(h(x['path'])==x['sha256'] for x in snap['files'])
records=[]
for case in diagnostic['cases']:
    row=next(r for r in study['requests'] if r['set']==case['set'] and r['target']==case['target'] and r['steps']==1600)
    raw=json.loads(Path(row['raw_path']).read_text()); point=raw['points'][-1]; flat=point['state']
    state={'sigma':flat[:6],'h':flat[6],'wp':flat[7]};assert state==case['last_state']
    p=dict(zip(model['parameters'],raw['parameters']))
    before=copy.deepcopy(state); env=evaluation_environment(model,state,state,[0]*6,p)
    init={expr:evaluate(parse(expr),env) for expr in model['initial_checks']}
    residuals=interpret(model,state,state,[0]*6,p)
    residual_norm=max(abs(v)/({'sigma':p['pa'],'h':p['ft'],'wp':p['pa']}[name])
                      for name,x in residuals.items() for v in (x.v if hasattr(x,'v') else [x]))
    try:
        prepare_increment(model,state,[0]*6,p)
        outcome='accepted'
    except Exception as exc:
        outcome=type(exc).__name__+': '+str(exc)
    assert outcome=='ValueError: inadmissible parent state' and state==before
    assert init=={'h>=f':False} and state['h']-env['f']==case['h_minus_f']
    records.append({'set':case['set'],'target':case['target'],'control':point['control'],
        'native_last_increment_scaled_error':point['error'],'native_residual_tolerance':raw['integration_settings']['residual_tolerance'],
        'last_increment_within_residual_tolerance':point['error']<raw['integration_settings']['residual_tolerance'],
        'f':env['f'],'h':state['h'],'h_minus_f':state['h']-env['f'],
        'initial_checks':init,'zero_prepare':outcome,'state_preserved_on_rejection':state==before,
        'zero_residual_scaled_norm':residual_norm,'zero_dwp_Pa':env['dwp']})
# Fixed-pressure triaxial active maximum: f(r)=(r+2)^3/r.
# Convex f makes all nonzero finite Newton-tangent history updates infeasible
# for strict h>=f enforced at every trial. Fractions preserve the exact witness.
def f(r):return (r+2)**3/r
r=F(3); hr=f(r); fp=2*r+6-8/r**2
convex=[]
for j in range(12):
    dr=F(1,2**j); trial_h=hr+fp*dr; defect=trial_h-f(r+dr)
    assert defect<0
    convex.append({'dyadic_backtrack':j,'delta_r':str(dr),'h_minus_f_exact':str(defect)})
# Exact arithmetic proof by cases of proposed new history carrier, not candidatev1.
carrier=[]
for hn,fc in [(F(40),F(45)),(F(45),F(42)),(F(40),F(27))]:
    q=max(hn-fc,F(0));decoded=max(F(40),fc+max(q,F(0)))
    assert decoded==max(hn,fc)
    carrier.append({'Hn':str(hn),'f_current':str(fc),'exact_solution_q':str(q),'decoded_H':str(decoded)})
# Noncanonical signed carrier represents zero gap but raw carrier equation
# changes under zero input, a prospective full-state hold issue to test.
q=F(-1,1000);fc=F(45);hn=max(F(40),fc+max(q,F(0)));q_target=max(hn-fc,F(0))
assert hn==45 and q_target==0 and q_target!=q
result={'id':'REVIEW-lade-duncan-native-failure-v1-python-challenge',
 'candidate_sha256':h(BASE/'model.json'),'native_requests':len(raw_checks),'native_successful':sum(r['ok'] for r in raw_checks),'frozen_study_passed':study['passed'],
 'native_source_snapshot_hashes':'all '+str(len(snap['files']))+' match','raw_native_bindings':raw_checks,
 'reentry_probes':records,'strict_all_trial_history_constraint_counterexample':{'r':str(r),'h':str(hr),'df_dr':str(fp),'f_second_derivative':'2+16/r^3 >0 for r>0','backtracks':convex},
 'new_carrier_algebra_only':{'cases':carrier,'signed_zero_gap_hold_witness':{'f':'45','ft':'40','q':str(q),'decoded_H':str(hn),'zero_increment_q_target':str(q_target)},'status':'exact reparameterization assessment only; no changed candidate or accepted numerical study'},
 'conclusion':'All six finest plastic-case retained last states pass ordinary model domain/evaluation but violate exact parent initial_check h>=f and reject zero preparation. Native residual convergence does not imply reentry validity. Strict all-trial solution constraint alone can reject all tangent steps. Explicit decoded carrier is algebraically defensible for a new identity but requires unchanged finite-path, history, full-state hold/restart gates.',
 'limits':['No compiled artifact executed','No native trajectory replay or new numerical qualification','No root evidence changed','No E5 approval']}
if __name__=='__main__':
    (HERE/'failure-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='raw_native_bindings'},indent=2))
