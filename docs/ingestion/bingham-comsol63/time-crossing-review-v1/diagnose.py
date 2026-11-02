"""Independent scalar midpoint-stage arithmetic and saved-output audit; no engine calls."""
from pathlib import Path
import hashlib,json,math
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];EX=OUT.parent/'execution-v1';cases=json.loads((EX/'cases.json').read_text())['cases'];rows=json.loads((EX/'native-attempt1.json').read_text());assert len(rows)==len(cases)==136
fail=[];success=0;repeats=0;schedules=[]
for c,row in zip(cases,rows):
 assert c['id']==row['id'];assert len(row['calls'])==2;assert row['calls'][0]['stdout']==row['calls'][1]['stdout'];repeats+=2
 r=json.loads(row['calls'][0]['stdout']);assert r['ok']==c['ok']
 if c['ok'] and c['kind']=='direct' and not c.get('restart_from'):
  success+=1;obs=json.loads(row['observation']);zs=[abs(x-y)/max(3e-7,2e-5*abs(y)) for x,y in zip(r['state'],c['expected'])];ss=[abs(x-y)/max(3,2e-5*abs(y)) for x,y in zip(obs['values'],c['expected_stress'])]
  if max(zs+ss)>1:fail.append(dict(id=c['id'],maximum_state_budget_ratio=max(zs),maximum_stress_budget_ratio=max(ss),substeps=r['substeps'],temporal_error_norm=r['temporal_error_norm']))
 if c['ok'] and c['kind']=='schedule':
  maxerr=0
  for pt in r['points']:
   ref=next(x for x in c['references'] if abs(x['time']-pt['time'])<1e-12);coarse=c['id']=='refinement-coarse';zf=.001 if coarse else 3e-7;sf=1000 if coarse else 3
   maxerr=max(maxerr,*[abs(x-y)/max(zf,2e-5*abs(y)) for x,y in zip(pt['state'],ref['state'])],*[abs(x-y)/max(sf,2e-5*abs(y)) for x,y in zip(pt['observables'],ref['stress'])])
  schedules.append(dict(id=c['id'],maximum_physical_budget_ratio=maxerr))
# Scalar radial-coordinate ODE derived directly from source, not imported DSL/oracle.
G=1e7;Y=1e5;eta=2e7;d=.003;force=2*G*d
stages=[]
def rhs(z):return force-3*G/eta*(1 if z>=0 else -1)*max(abs(z)-Y,0)
def midpoint(z,h):
 mid=z+.5*h*rhs(z);v=z+h*rhs(mid);stages.append(dict(initial_z=z,duration=h,midpoint_z=mid,midpoint_lambda=max(abs(mid)-Y,0)/eta,endpoint_z=v));return v
aliases=[]
for z0 in [0.,-200000.]:
 stages=[];full=midpoint(z0,2.);half=midpoint(z0,1.);two=midpoint(half,1.);aliases.append(dict(z0=z0,full=full,two_half=two,defect=two-full,stages=list(stages)))
t_y=Y/force;active=2-t_y;q_exact=Y+force/(3*G/eta)*(1-math.exp(-3*G/eta*active));alpha=(force*2-q_exact)/(3*G)
result=dict(compiled_execution=False,saved_rows=len(rows),identical_repeated_calls=repeats,nonrestart_successful_direct_requests=success,failed_direct_physical_budgets=len(fail),failures=fail,scheduled_physical_diagnostics=schedules,scalar_aliases=aliases,first_case_exact=dict(yield_time_since_start=t_y,endpoint_q_Pa=q_exact,endpoint_alpha=alpha,elastic_endpoint_q_Pa=force*2))
(OUT/'DIAGNOSTICS.json').write_text(json.dumps(result,indent=2)+'\n');paths=[EX/'native-attempt1.json',EX/'native-qualification-attempt1-status.json',EX/'native-attempt1-component-diagnostics.json',EX/'cases.json',EX/'study.py',EX/'oracle.py',EX/'build-inputs-v1.json',EX/'frozen-source-archive-v1/INDEX.json',OUT.parent/'source-v1/analytical-references.json',OUT.parent/'source-v1/source-receipts.json',ROOT/'cpp/include/atlas/time.hpp',ROOT/'cpp/include/atlas/schedule.hpp'];(OUT/'INPUT-BINDING.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',scope='DIAG-bingham-time-crossing-v1',files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n');print(json.dumps({k:result[k] for k in ['saved_rows','identical_repeated_calls','failed_direct_physical_budgets','first_case_exact','scheduled_physical_diagnostics']},indent=2))
