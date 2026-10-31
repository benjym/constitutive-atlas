"""Centered fixed-branch value differences versus analytic refs; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,gzip,argparse,hashlib
import generate as g

def load(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def values(parameters,current,parent,loading,precision):
 E,nu,c,phi,psi=[parameters[k]for k in('E','nu','c','phi','psi')];K=E/(3*(1-2*nu));G=E/(2*(1+nu));s,cf=g.sincos(phi);d,cd=g.sincos(psi)
 p=dict(E=E,nu=nu,c=c,K=K,G=G,sf=s,sd=d,cf=cf,cd=cd);a=g.cart(g.lintrial(parent,loading,K,G));v,_=g.sp.root_cubic(a,precision)
 ps={i:g.sp.project(a,v,i)for i in range(3)if all(v[i]!=v[j]for j in range(3)if i!=j)};law=g.law(p);_,roots,_,_,_=g.classify(v,p,law);out={}
 for branch in('elastic','face','left','right','apex'):
  b=g.branch_result(branch,v,p,law,roots,ps,{}, {},[],[])
  if b['status']!='defined':continue
  returned=[-x for x in g.mandel(a if branch=='elastic'else b['matrix'])]
  out[branch]={'returned_atlas':returned,'residual':[x-y for x,y in zip(current,returned)]}
 return out

def main(inputs,reference,policy):
 data=load(inputs);refs={r['id']:r['canonical']for r in load(reference)['cases']};policy=load(policy);failures=[];worst=(D(0),'');checks=0;linearitychecks=0;apexchecks=0;mixedchecks=0;rows=[]
 ids=['certificate/face/dense','certificate/left/dense','certificate/right/dense','certificate/apex_interior/dense','certificate/left_repeated_trial/diagonal','certificate/right_repeated_trial/diagonal','certificate/left_repeated_trial/dense','certificate/right_repeated_trial/dense','certificate/face_to_left_boundary/dense','certificate/left_to_apex_boundary/dense','certificate/hydrostatic_apex/dense','coincident/0/0']
 cases={r['id']:r for r in data['cases']}
 with localcontext()as ctx:
  ctx.prec=policy['precision'];tol=D(policy['error_gate'])
  for rid in ids:
   c=cases[rid];ref=refs[rid];p={k:g.fd(g.frac(v))for k,v in c['parameters'].items()};current=list(map(g.fd,g.vec(c['current'])));parent=list(map(g.fd,g.vec(c['parent'])));loading=list(map(g.fd,g.vec(c['loading'])))
   targets=[('column'+str(j),j,None)for j in policy['columns']]+[(name,None,name)for name in policy['parameters']]
   for label,j,name in targets:
    for step_s in policy['centered_relative_steps']:
     h=D(step_s)*(max(D(1),abs(p[name]))if name else D(1));sides=[]
     for sign in(-1,1):
      pp=p.copy();cv=current.copy();pv=parent.copy();lv=loading.copy()
      if name:pp[name]+=sign*h
      else:
       seed=data['seeds'][j]
       for key,v in(('current',cv),('parent',pv),('loading',lv)):
        ds=list(map(g.fd,g.vec(seed[key])))
        for k in range(6):v[k]+=sign*h*ds[k]
      sides.append(values(pp,cv,pv,lv,policy['precision']))
     rowchecks=0;rowworst=D(0)
     for branch,b in ref['branches'].items():
      if b['status']!='defined':continue
      if any(branch not in side for side in sides):failures.append({'path':rid+'/'+branch+'/'+label,'reason':'perturbed-fixed-branch-undefined'});continue
      expected=b['parameter_directions'][name]if name else b['directions'][j]
      for channel in('returned_atlas','residual'):
       for k,raw in enumerate(expected[channel]):
        target=D(raw);observed=(sides[1][branch][channel][k]-sides[0][branch][channel][k])/(2*h);err=abs(observed-target)/max(D(1),abs(target));checks+=1;rowchecks+=1;rowworst=max(rowworst,err);path=rid+'/'+branch+'/'+label+'/'+step_s+'/'+channel+'/'+str(k)
        if err>worst[0]:worst=(err,path)
        if err>tol:failures.append({'path':path,'error':str(err),'fd':str(observed),'reference':raw})
     rows.append({'case':rid,'direction':label,'step':step_s,'checks':rowchecks,'maximum_normalized_error':str(rowworst)})
  # All38 columns must equal the linear combination of the18 independent bases.
  basis={}
  for j,s in enumerate(data['seeds']):
   v=[float.fromhex(x)for key in('current','parent','loading')for x in s[key]]
   if v.count(1.)==1 and v.count(0.)==17:basis[v.index(1.)]=j
  assert set(basis)==set(range(18))
  for rid,ref in refs.items():
   for branch,b in ref['branches'].items():
    if b['status']!='defined':continue
    for j,s in enumerate(data['seeds']):
     weights=[D.from_float(float.fromhex(x))for key in('current','parent','loading')for x in s[key]]
     for channel in('returned_atlas','residual'):
      for k in range(6):
       terms=[w*D(b['directions'][basis[i]][channel][k])for i,w in enumerate(weights)];expected=sum(terms);actual=D(b['directions'][j][channel][k]);scale=max(sum(map(abs,terms)),abs(actual),D('1e-100000'));error=abs(actual-expected)/scale;linearitychecks+=1
       if error>tol:failures.append({'path':rid+'/'+branch+'/linearity/'+str(j)+'/'+channel+'/'+str(k),'error':str(error)})
    # Exact apex stress sensitivity identities at the physical stored parameters.
    if branch=='apex':
     p=ref['coefficients'];c,s,cf=map(D,(p['c'],p['sf'],p['cf']))
     expected={'E':D(0),'nu':D(0),'psi':D(0),'c':-cf/s,'phi':c/(s*s)}
     for name,want in expected.items():
      for k,raw in enumerate(b['parameter_directions'][name]['returned_atlas']):
       target=want if k<3 else D(0);actual=D(raw);error=abs(actual-target)/max(D(1),abs(target));apexchecks+=1
       if error>tol:failures.append({'path':rid+'/apex/parameter-identity/'+name+'/'+str(k),'error':str(error)})
  for rid,want in [('mixed-scale-middle/large',D(1)),('mixed-scale-middle/extreme',D(1)),('mixed-scale-middle/tiny',D.from_float(float.fromhex(cases['mixed-scale-middle/tiny']['loading'][1]))*-2)]:
   r=refs[rid];assert r['selected_branch']=='face'
   for channel in('eigenvalues',):
    actual=D(r[channel][1]);error=abs(actual-want)/(abs(want)or D(1));mixedchecks+=1
    if error>D('1e-70'):failures.append({'path':rid+'/exact-middle','error':str(error)})
   # Lame0: source middle survives the face return exactly; Atlas reverses sign.
   actual=D(r['branches']['face']['returned_atlas'][1]);error=abs(actual+want)/(abs(want)or D(1));mixedchecks+=1
   if error>D('1e-70'):failures.append({'path':rid+'/returned-middle','error':str(error)})
 result={'identity':'mc-fixed-branch-reference-derivative-self-check-v1','policy_sha256':hashlib.sha256(Path(policy_path).read_bytes()).hexdigest(),'fixed_branch_cases':len(ids),'finite_difference_component_checks':checks,'linearity_component_checks':linearitychecks,'apex_parameter_identity_checks':apexchecks,'mixed_scale_middle_checks':mixedchecks,'maximum_normalized_fd_error':str(worst[0]),'maximum_error_path':worst[1],'rows':rows,'failures':failures,'passed':not failures,'compiled_observations':0,'candidate_calls':0}
 print(json.dumps(result,indent=2,sort_keys=True));return result['passed']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('reference');p.add_argument('policy');a=p.parse_args();policy_path=a.policy;raise SystemExit(0 if main(a.inputs,a.reference,a.policy)else 1)
