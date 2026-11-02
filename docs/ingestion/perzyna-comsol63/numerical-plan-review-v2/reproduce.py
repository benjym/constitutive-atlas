"""Read-only v1 freeze audit and independent complete-output counterexample."""
import sys,json,hashlib,math,copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'execution-v2';ROOT=HERE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((BASE/'FREEZE.json').read_text());assert sha(BASE/'FREEZE.json')=='7dcc4a01a3408dba2cd49258e52e904f8cfa822c365eacce5dd4c1def753bd64'
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
# Existing inputs must remain byte-identical across the prospective correction.
v1=HERE.parent/'execution-v1';unchanged=['cases.json','reference-convergence.json','oracle.py','prepare.py','expected-catalogue.json','collect_wasm.mjs','parity.py','run_operation.py']
for name in unchanged:assert (BASE/name).read_bytes()==(v1/name).read_bytes(),name
prior=json.loads((v1/'FREEZE.json').read_text())
for name,h in prior['files'].items():
 if '/execution-v1/' not in name:assert f['files'].get(name)==h,name
assert prior['external_files']==f['external_files']
assert 'tools/record_cmake_profile_build_v2.py' in f['files']
mutations=[]
def reject(rowid,index,component,value,label):
 clone=copy.deepcopy(rows);row=next(r for r in clone if r['id']==rowid);r=json.loads(row['calls'][0]['stdout']);r['points'][index]['strain_rate'][component]=value
 for call in row['calls']:call['stdout']=json.dumps(r)
 try:study.assess(cases,clone)
 except AssertionError as e:mutations.append({'case':rowid,'point':index,'component':component,'label':label,'rejected':True,'reason':str(e)})
 else:raise AssertionError('Accepted corrupted creep rate '+rowid)
for row in rows:
 r=json.loads(row['calls'][0]['stdout'])
 if not r.get('ok'):continue
 source=next(c for c in cases if c['id']==row['id']);controls=source['specification']['segments'][0]['controls']
 if not all(c['quantity']=='stress' and c['kind']=='hold' for c in controls):continue
 for i,point in enumerate(r['points']):
  if point['segment']<0 or point['side']!='left':continue
  for j,rate in enumerate(point['strain_rate']):
   reject(row['id'],i,j,1e20,'v1-extreme-rate-counterexample')
   if abs(rate)>1e-8:reject(row['id'],i,j,0.,'zero-rate')
   reject(row['id'],i,j,rate+max(1e-10,2e-5*abs(rate))*1.05,'just-outside-frozen-gate')
# Reproduce each originally generated low/high stress-space reference grid without
# executing prepare.py or modifying its sealed evidence.
import oracle
comparisons=[]
for c in cases:
 if not c['ok'] or c.get('restart_from'):continue
 s=c['specification']
 if not any(ctrl['kind']=='rate' for segment in s['segments'] for ctrl in segment['controls']):continue
 current=list(s['initial']);t=0.
 for segment in s['segments']:
  for sample in range(segment['samples']):
   dt=segment['duration']/segment['samples'];t+=dt;rates=[x.get('value',0.) for x in segment['controls']]
   lo=oracle.stress_space_history(current,[(dt,rates)],s['parameters'],8192)[0]
   hi=oracle.stress_space_history(current,[(dt,rates)],s['parameters'],16384)[0]
   ds=max(abs(a-b) for a,b in zip(lo['state'],hi['state']));dq=max(abs(a-b) for a,b in zip(lo['stress'],hi['stress']))
   expected=next(r for r in c['references'] if abs(r['time']-t)<1e-12)
   assert ds<5e-11 and dq<.005,(c['id'],ds,dq)
   assert max(abs(a-b) for a,b in zip(hi['state'],expected['state']))<1e-14
   assert max(abs(a-b) for a,b in zip(hi['stress'],expected['stress']))<1e-6
   saved=next(r for r in conv['comparisons'] if r['case']==c['id'] and abs(r['time']-t)<1e-12)
   assert ds==saved['state_error'] and dq==saved['stress_error_Pa'],(c['id'],ds,dq,saved)
   comparisons.append({'case':c['id'],'time':t,'state_error':ds,'stress_error_Pa':dq,'reproduced':True});current=hi['state']
assert len(comparisons)==26
# Reverify immutable inputs after all Python/mock work.
for path,h in f['files'].items():assert sha(ROOT/path)==h,path
for path,h in f['external_files'].items():assert sha(Path(path))==h,path
out={'identity':'perzyna-numerical-plan-v2-independent-review','freeze_sha256':sha(BASE/'FREEZE.json'),'source_pins_pre_post_verified':len(f['files']),'external_pins_pre_post_verified':len(f['external_files']),'cases':len(cases),'unchanged_v1_files':unchanged,'baseline_synthetic_passed':baseline['passed'],'rate_mutations_rejected':len(mutations),'mutations':mutations,'reference_comparisons_reproduced':comparisons,'compiled_or_material_calls':0,'decision':'ACCEPT'}
(HERE/'CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['mutations','reference_comparisons_reproduced']}))
