"""Source-derived scalar BE estimator diagnosis and saved-output reads, no engine calls."""
from pathlib import Path
import hashlib,json,math
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];EX=OUT.parent/'execution-v2';sha=lambda b:hashlib.sha256(b).hexdigest();raw=(EX/'native-attempt1.json').read_bytes();rows=json.loads(raw);(OUT/'native-partial-snapshot.json').write_bytes(raw);cases=json.loads((EX/'cases.json').read_text())['cases'];G=1e7;Y=1e5;eta=2e7;a=3*G/eta
# Independent closed form for initially active inward rates; one elastic crossing interval.
def exact(z0,d,T):
 b=2*G*d;sign=1 if z0>0 else -1;ss=sign*Y+b/a;exit_time=-math.log((sign*Y-ss)/(z0-ss))/a
 assert 0<exit_time<T and sign*b<0
 alpha1=sign*(b*exit_time-(sign*Y-z0))/(3*G);remaining=T-exit_time;elastic_width=2*Y/abs(b)
 if remaining<=elastic_width:zend=sign*Y+b*remaining;alpha2=0.
 else:
  active=remaining-elastic_width;other=-sign;ss2=other*Y+b/a;zend=ss2+(other*Y-ss2)*math.exp(-a*active);alpha2=other*(b*active-(zend-other*Y))/(3*G)
 return dict(z=zend,alpha=alpha1+alpha2,first_exit_time=exit_time,initial_active_alpha=alpha1)
# Exact scalar BE solve, independently eliminates plastic strain from the source law.
def adaptive(z0,d,T):
 b=2*G*d;aliases=[];n=0;N=[2/3,-1/3,-1/3,0,0,0]
 def step(x,h):
  z,beta,alpha=x;trial=z+b*h
  end=trial if abs(trial)<=Y else (trial+a*h*(1 if trial>=0 else -1)*Y)/(1+a*h)
  db=(trial-end)/(3*G);return end,beta+db,alpha+abs(db)
 def recurse(x,t,h,depth=0):
  nonlocal n
  assert depth<=40
  full=step(x,h);half=step(x,h/2);two=step(half,h/2)
  comparisons=[(1.5*N[i]*full[1],1.5*N[i]*two[1],1.5*N[i]*x[1]) for i in range(6)]+[(full[2],two[2],x[2])]
  error=max(abs(f-v)/(1e-12+1e-9*max(abs(initial),abs(v))) for f,v,initial in comparisons)
  if error<=1:
   n+=2
   if abs(x[0])>Y and abs(full[0])<=Y and abs(half[0])<=Y and abs(two[0])<=Y and full[1:]==x[1:] and two[1:]==x[1:]:aliases.append(dict(t=t,duration=h,initial=x,full=full,first_half=half,two_half=two,error=error))
   return two
  halfx=recurse(x,t,h/2,depth+1);return recurse(halfx,t+h/2,h/2,depth+1)
 final=recurse((z0,0.,0.),0.,T);return dict(final_z=final[0],final_alpha=final[2],accepted_halfsteps=n,inactive_endpoint_aliases=aliases)
results=[]
for ident,z0,d in [('radial-channel-0-z200000-d-0.012',200000.,-.012),('radial-channel-0-z-200000-d0.003',-200000.,.003)]:
 c=next(x for x in cases if x['id']==ident);saved=next(x for x in rows if x['id']==ident);r=json.loads(saved['calls'][0]['stdout']);pt=r['points'][-1];truth=exact(z0,d,2.);ref=c['references'][-1];reference_z=1.5*ref['stress'][0];assert abs(truth['z']-reference_z)<1e-8 and abs(truth['alpha']-ref['state'][12])<1e-15
 scalar=adaptive(z0,d,2.);results.append(dict(id=ident,independent_exact=truth,reference_z=reference_z,saved_z=1.5*pt['observables'][0],saved_alpha=pt['state'][12],saved_substeps=pt['substeps'],scalar_adaptive=scalar))
report=dict(identity='independent-be-crossing-diagnosis-v1',compiled_calls=0,source_native_file_snapshot_sha256=sha(raw),snapshot_rows=len(rows),partial_collection=True,cases=results)
(OUT/'DIAGNOSTICS.json').write_text(json.dumps(report,indent=2)+'\n');paths=[EX/'PLAN.md',EX/'cases.json',EX/'study.py',EX/'freeze-v1.json',ROOT/'cpp/include/atlas/schedule.hpp',ROOT/'cpp/include/atlas/time.hpp',OUT.parent/'source-v1/analytical-references.json'];(OUT/'BINDINGS.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',observed_growing_native_source=str((EX/'native-attempt1.json').relative_to(ROOT)),observed_snapshot_sha256=sha(raw),files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}),indent=2)+'\n');print(json.dumps(report,indent=2))
