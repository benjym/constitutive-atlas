"""Independent reference-v2 integrity, convergence, analytical and stage-domain audit."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import json, hashlib, sys, importlib.util
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
REF=ROOT/'docs/ingestion/vibe-2026/reference-v2'
V1=REF.parent/'reference-v1'
IDS=['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
expected={'reference-v1':'04dd3a8831e83cada428a38479f72908f8f1ed03ea640df4b4c9826dabf0d079','reference-v2':'bf526d6149fd3e1082ba477c01d455caa8873c850fbbb83594c1b4010c988139','review-numerical-v1':'a9dbb295044607d9c928d3a52b1611f7eadbc82f798b11224c91cec64fcfe535'}
for folder,identity in expected.items():
    p=REF.parent/folder/'manifest.json';assert sha(p)==identity
    manifest=json.loads(p.read_text())
    for item in manifest['files']:
        q=ROOT/item['path'];assert sha(q)==item['sha256'] and q.stat().st_size==item['bytes']
    checks[folder]={'manifest_sha256':identity,'verified_files':len(manifest['files'])}
assert sha(REF/'plan.json')=='6dd5a3b20eabcac10ffe82e0385d72cd37364009133a92c596898d0b322e814d'
def comparison(a,b,at,rt):
    errors=[abs(D(x)-D(y)) for x,y in zip(a,b)]
    ratios=[err/(at+rt*max(abs(D(x)),abs(D(y)))) for x,y,err in zip(a,b,errors)]
    assert all(r<=1 for r in ratios)
    return {'max_absolute_error':str(max(errors)),'max_tolerance_ratio':str(max(ratios))}
histories=[]
with localcontext() as c:
 c.prec=80
 for ident in IDS:
    p=REF/(ident+'.json');reproduced=OUT/'reproduced-reference'/(ident+'.json')
    assert p.read_bytes()==reproduced.read_bytes()
    data=json.loads(p.read_text());assert len(data['runs'])==4 and all(r['status']=='pass' for r in data['runs'])
    runs=[r['result'] for r in data['runs']];assert [(r['partitions'],r['precision']) for r in runs]==[(64,70),(128,70),(256,70),(256,50)]
    pairs={}
    for label,lo,hi in [('coarse',0,1),('partition',1,2),('precision',3,2)]:
        a=runs[lo];b=runs[hi]
        pairs[label]={'stress':comparison(a['final_state'][:6],b['final_state'][:6],D('.01'),D('1e-7')),'scalar':comparison(a['final_state'][6:],b['final_state'][6:],D('1e-9'),D('1e-7')),'observables':comparison([a['endpoint_observables'][k] for k in ['em','eM','S','Sr','OA','re']],[b['endpoint_observables'][k] for k in ['em','eM','S','Sr','OA','re']],D('1e-8'),D('1e-7'))}
    analytical=[]
    for run in runs:
        assert len(run['initial_state'])==len(run['final_state'])==len(run['endpoint_rate'])==8
        e0=D(run['initial_state'][6]);expected_e=e0 if ident=='mechanical_reversal_100' else (1+e0)*(-D('4e-8')*D(100)).exp()-1
        analytical.append(comparison([run['final_state'][6]],[expected_e],D('1e-9'),D('1e-7')))
        assert all(D(x)!=0 for x in run['change'][:6])
        assert D(run['endpoint_suction_Pa'])==(D(10200000) if ident=='coupled_mechanical_THM_100' else D(10000000))
        assert D(run['endpoint_temperature_K'])==(D(296) if ident=='coupled_mechanical_THM_100' else D(294))
        assert [D(x) for x in run['endpoint_mechanical_rate_per_s']]==[D(k)*D('1e-8')*(-1 if ident=='mechanical_reversal_100' else 1) for k in [2,-1,3,-2,1,-3]]
        assert (D(run['change'][7])>0) if ident=='coupled_mechanical_THM_100' else D(run['change'][7])==0
    histories.append({'id':ident,'exact_reproduced_bytes':sha(p),'independently_recomputed_convergence':pairs,'analytical_void_ratio_each_run':analytical})
checks['histories']=histories

# A distinct diagnostic: monitor the original guarded algebra at every RK stage
# of the finest70-digit histories, retaining extrema rather than relying only
# on endpoint admissibility. No source or candidate bytes are changed.
spec=importlib.util.spec_from_file_location('vibe_review_histories',REF/'run_histories.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from oracle import algebra
original_rate=module.rate
domain=[]
for ident in IDS:
    extrema={};calls=0
    def monitored(y,s,T,sd,Td,mech,p,*args,**kwargs):
        global calls
        q=algebra(y,s,T,sd,p);calls+=1
        values={k:q[k] for k in ['pm','pM','em','eM','S','Fm','omega','OA','re','lam','lact','Iv','aden']}
        values.update(suction=s,temperature=T,scan=y[7],B_denominator=1+3*(q['bB']+q['cB']+3*q['cB']*q['dB']))
        for name,value in values.items():
            record=extrema.setdefault(name,[value,value]);record[0]=min(record[0],value);record[1]=max(record[1],value)
        return original_rate(y,s,T,sd,Td,mech,p,*args,**kwargs)
    module.rate=monitored
    result=module.trajectory(ident,256,70)
    assert calls==1025
    retained=json.loads((REF/(ident+'.json')).read_text())['runs'][2]['result']
    assert module.stringify(result)==retained
    assert extrema['OA'][0]>=1 and extrema['eM'][0]>0 and extrema['Iv'][0]>0
    domain.append({'id':ident,'guarded_rate_calls':calls,'minimum_maximum':{k:[str(x) for x in v] for k,v in extrema.items()}})
checks['finest_trajectory_stage_domain_monitor']=domain

# Audit parent-produced Python comparisons as saved evidence. Do not import or
# execute a candidate/backend here; recheck all gates against full Decimal data.
WORK=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
CAND=WORK/'docs/ingestion/vibe-2026/candidate-v1'
model=WORK/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
assert sha(model)=='29d104bf55ec3225030e8710ee342f96b6518bd8a4434e784e455da300d08778'
plan=json.loads((CAND/'mechanical-study-v2-plan.json').read_text())
assert sha(CAND/'mechanical-study-v2-plan.json')=='07133b703addf5bc569db87ff8cdb82eb1343503e2dea9dd6182a2c86948ecd1'
assert plan['model_sha256']==sha(model) and plan['reference_manifest_sha256']==sha(REF/'manifest.json')
assert plan['script_sha256']==sha(CAND/'compare_mechanical_v2.py') and plan['cases']==IDS
old=json.loads((CAND/'mechanical-study-v1-plan.json').read_text())
for key in ['settings','acceptance','cases','comparison','method','model_sha256','time_origin_seconds']:assert old[key]==plan[key]
failure=json.loads((CAND/'mechanical-study-v1-failure.json').read_text())
assert failure['exception']=='FileNotFoundError' and failure['status']=='FAIL before numerical execution'
candidate=[]
obsmap={'em':'micro_void_ratio','eM':'macro_void_ratio','S':'macro_saturation','Sr':'saturation','OA':'overconsolidation','re':'relative_density'}
with localcontext() as c:
 c.prec=80
 for ident in IDS:
    report_path=CAND/('mechanical-study-v2-'+ident+'.json');report=json.loads(report_path.read_text(),parse_float=D)
    original=json.loads((REF/(ident+'.json')).read_text())['runs'][2]['result']
    assert report['status']=='pass' and report['id']==ident
    assert report['plan_sha256']==sha(CAND/'mechanical-study-v2-plan.json') and report['reference_sha256']==sha(REF/(ident+'.json'))
    assert len(report['final_state'])==len(report['expected'])==8
    recalculated={'stress':comparison(report['final_state'][:6],original['final_state'][:6],D('.01'),D('1e-7')),'scalar':comparison(report['final_state'][6:],original['final_state'][6:],D('1e-9'),D('1e-7'))}
    context=report['context'];assert context['time']==111 and context['state']['sigma_net']+ [context['state']['e'],context['state']['a_scan']]==report['final_state']
    assert context['controls']['suction']==D(original['endpoint_suction_Pa']) and context['controls']['temperature']==D(original['endpoint_temperature_K'])
    assert context['control_rates']['strain']==[D(x) for x in original['endpoint_mechanical_rate_per_s']]
    expected_strain=[D(0)]*6 if ident=='mechanical_reversal_100' else [D(x)*100 for x in original['endpoint_mechanical_rate_per_s']]
    control_representation_errors=[str(abs(a-b)) for a,b in zip(context['controls']['strain'],expected_strain)]
    # Diagnostic only: exact decimal endpoints are not promised for binary64 input multiplication.
    assert len(report['diagnostics'])==(2 if ident=='mechanical_reversal_100' else 1)
    assert all(diag['final_error']<=1 for diag in report['diagnostics'])
    assert all(value<=1 for value in report['state_tolerance_ratios']+list(report['observable_tolerance_ratios'].values()))
    # Reports retain observable tolerance ratios rather than raw observables;
    # those reported checks are inspected, not independently recomputed here.
    candidate.append({'id':ident,'control_strain_decimal_representation_errors':control_representation_errors,'report_sha256':sha(report_path),'full_decimal_reference_state_gates':recalculated,'reported_observable_tolerance_ratios':{k:str(v) for k,v in report['observable_tolerance_ratios'].items()},'maximum_reported_tolerance_ratio':str(max(report['state_tolerance_ratios']+list(report['observable_tolerance_ratios'].values())))})
checks['parent_candidate_saved_comparison_audit']={'plan_sha256':sha(CAND/'mechanical-study-v2-plan.json'),'model_sha256':sha(model),'initial_failure_retained':sha(CAND/'mechanical-study-v1-failure.json'),'comparisons':candidate,'limitation':'Candidate integrations were not independently rerun in this review; raw observable values are absent from reports, so observable ratios are inspected reported evidence.'}
(OUT/'audit-v2-results.json').write_text(json.dumps(checks,indent=2)+'\n')
print('PASS: exact12run reproduction, original+priorreview integrity, independent gates/e solution and3075guarded stage calls')
