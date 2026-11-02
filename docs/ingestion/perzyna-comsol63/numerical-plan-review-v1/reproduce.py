"""Read-only v1 freeze audit and independent complete-output counterexample."""
import sys,json,hashlib,math,copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'execution-v1';ROOT=HERE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((BASE/'FREEZE.json').read_text());assert sha(BASE/'FREEZE.json')=='48455810b86348658266e0f16459c9ddd96df8af1b763630b54c30bfef929817'
for path,h in f['files'].items():assert sha(ROOT/path)==h,path
for path,h in f['external_files'].items():assert sha(Path(path))==h,path
spec=importlib.util.spec_from_file_location('perzyna_v1_reviewed_study',BASE/'study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
cases=json.loads((BASE/'cases.json').read_text())['cases'];assert len(cases)==107 and len({c['id'] for c in cases})==107
conv=json.loads((BASE/'reference-convergence.json').read_text());assert conv['passed'] and len(conv['comparisons'])==26 and all(c['state_error']<5e-11 and c['stress_error_Pa']<.005 for c in conv['comparisons'])
catalogue=json.loads((BASE/'expected-catalogue.json').read_text())['sha256']
# Independently make result fixtures. Source data supply state/stress references;
# we supply schema/topology and exact constant-stress creep solved rates.
def creep_rate(stress,p):
 mean=sum(stress[:3])/3;s=[v-(mean if j<3 else 0) for j,v in enumerate(stress)];q=math.sqrt(1.5*sum(v*v for v in s));lam=p[3]*max(q/p[2]-1,0)**p[4]
 return [1.5*lam*v/q if q else 0. for v in s]
rows=[]
for src in cases:
 c=study.resolve(src,rows);s=c['specification']
 if not c['ok'] and c.get('parse_failure'):
  r={'ok':False,'message':'v0.3 requires explicit state; initial literals are examples only' if c['id']=='missing-state' else 'parameter length, bounds or finiteness invalid'}
 else:
  message='' if c['ok'] else 'schedule solve failed in segment budget-exhaustion; last committed sample retained' if c.get('late') else 'invalid segment duration, identity or sample budget' if 'duration' in c['id'] else 'inadmissible initial state or outputs'
  r=dict(ok=c['ok'],schema_version='0.2',units='SI',model=study.MODEL,catalogue_hash=catalogue,message=message,**{k:s[k] for k in ['start_time','parameters','initial','initial_strain','initial_strain_rate','segments']},solver={**s['solver'],'maximum_depth':40},points=[])
  if c['ok'] or c.get('late'):
   topology=[(s['start_time'],-1,'left')];start=s['start_time']
   for seg,part in enumerate(s['segments']):
    end=start+part['duration'];topology.append((start,seg,'right'))
    for j in range(1,part['samples']+1):topology.append((end if j==part['samples'] else start+part['duration']*j/part['samples'],seg,'left'))
    start=end
   if c.get('late'):topology=topology[:4]
   for i,(t,seg,side) in enumerate(topology):
    ref=next(x for x in c['references'] if abs(x['time']-t)<1e-12)
    rate=list(s['initial_strain_rate']) if seg<0 else [None if side=='right' and ctrl['quantity']=='stress' else creep_rate(ref['stress'],s['parameters'])[j] if ctrl['quantity']=='stress' else ctrl.get('value',0.) if ctrl['kind']=='rate' else 0. for j,ctrl in enumerate(s['segments'][seg]['controls'])]
    z=list(ref['state']);sig=list(ref['stress'])
    if c['id']=='refinement-coarse' and i==len(topology)-1:z[0]+=1e-5;sig[0]+=10.
    r['points'].append(dict(time=t,segment=seg,side=side,state=z,strain=z[:6],strain_rate=rate,observables=sig,iterations=int(side=='left' and seg>=0),substeps=2*int(side=='left' and seg>=0),rejected=0,temporal_error_norm=0.,nonlinear_residual_norm=0.))
 raw=json.dumps(r);rows.append(dict(id=c['id'],request={k:c[k] for k in ['call','types','args','argv']},calls=[dict(returncode=0 if c['ok'] else 1,stdout=raw,stderr='') for _ in range(2)]))
baseline=study.assess(cases,rows);assert baseline['passed']
mutation=copy.deepcopy(rows);row=next(r for r in mutation if r['id']=='public-creep');result=json.loads(row['calls'][0]['stdout']);original=[];replacement=[]
for p in result['points']:
 if p['segment']>=0 and p['side']=='left':
  original.append(p['strain_rate']);p['strain_rate']=[1e20,-1e20,1e20,-1e20,1e20,-1e20];replacement.append(p['strain_rate'])
for call in row['calls']:call['stdout']=json.dumps(result)
accepted=study.assess(cases,mutation);assert accepted['passed']
output={'identity':'perzyna-numerical-plan-v1-independent-review','freeze_sha256':sha(BASE/'FREEZE.json'),'source_pins_verified':len(f['files']),'external_pins_verified':len(f['external_files']),'cases':len(cases),'saved_convergence_comparisons_audited':len(conv['comparisons']),'convergence_recomputed':False,'baseline_synthetic_passed':baseline['passed'],'counterexample_case':'public-creep','correct_solved_rates':original,'replacement_rates':replacement,'corrupt_complete_output_accepted':accepted['passed'],'compiled_or_material_calls':0,'decision':'CORRECTIONS REQUIRED'}
(HERE/'CHECKS.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
