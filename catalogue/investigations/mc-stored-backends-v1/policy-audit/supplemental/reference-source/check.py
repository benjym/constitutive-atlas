"""Independent-reference precision/KKT/38-direction checks, standard library only."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,gzip,argparse,hashlib

def load(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def run(inputs,low,high,policy):
 raw=Path(inputs).read_bytes();data=json.loads(raw);a,b=load(low),load(high);gate=load(policy);tol=D(gate['normalized_precision_difference_max']);rtol=D(gate['normalized_internal_residual_max']);failures=[];counts={'numeric_fields':0,'canonical_reference_cases':0,'defined_branch_expressions':0,'direction_vectors':0,'parameter_direction_vectors':0};worst=(D(0),'');internalmax=D(0)
 def fail(path,reason,**kwargs):failures.append(dict(path=path,reason=reason,**kwargs))
 if a['input_sha256']!=hashlib.sha256(raw).hexdigest()or b['input_sha256']!=a['input_sha256']:fail('inputs','hash-mismatch')
 if a['unresolved']or b['unresolved']:fail('cases','generator-unresolved',low=a['unresolved'],high=b['unresolved'])
 if [x['id']for x in a['cases']]!=[x['id']for x in b['cases']]:fail('cases','case-identity-or-order')
 with localcontext()as ctx:
  ctx.prec=220
  def compare(x,y,natural,path):
   nonlocal worst
   x,y=D(x),D(y);natural=abs(natural)or D(1);scale=max(abs(x),abs(y),min(D(1),natural));error=abs(x-y)/scale;counts['numeric_fields']+=1
   if error>worst[0]:worst=(error,path)
   if error>tol:fail(path,'precision-difference',difference=str(error),low=str(x),high=str(y))
  def walk(x,y,natural,path):
   if isinstance(y,dict):
    if not isinstance(x,dict)or set(x)!=set(y):fail(path,'shape');return
    for k in y:
     if k in('internal_checks','directions','parameter_directions','working_precision'):continue
     walk(x[k],y[k],natural,path+'/'+k)
   elif isinstance(y,list):
    if not isinstance(x,list)or len(x)!=len(y):fail(path,'shape');return
    for j,(u,v)in enumerate(zip(x,y)):walk(u,v,natural,path+'/'+str(j))
   elif isinstance(y,str):
    try:D(y)
    except Exception:
     if x!=y:fail(path,'status-or-classification',low=x,high=y)
    else:compare(x,y,natural,path)
   elif x!=y:fail(path,'metadata',low=x,high=y)
  for x,y in zip(a['cases'],b['cases']):
   rid=y['id']
   for interface in('canonical','resolved_coefficients_diagnostic'):
    u,v=x[interface],y[interface];path=rid+'/'+interface
    if u['status']!=v['status']:fail(path,'interface-status');continue
    if v['status']!='reference':continue
    scale=D(v['stress_scale']);walk(u,v,scale,path)
    if interface=='canonical':counts['canonical_reference_cases']+=1
    for level,row in((a['base_precision'],u),(b['base_precision'],v)):
     checks=row['internal_checks']
     for k,val in checks.items():
      if type(val)is bool:
       if not val:fail(path+'/p'+str(level)+'/'+k,'reference-internal-false')
      elif k!='flow_subgradient':
       value=abs(D(val));internalmax=max(internalmax,value)
       if value>rtol:fail(path+'/p'+str(level)+'/'+k,'reference-internal-residual',value=str(value))
    for branch,z in v['branches'].items():
     w=u['branches'][branch];bp=path+'/'+branch
     if z['status']!='defined':continue
     if interface=='canonical':counts['defined_branch_expressions']+=1
     if 'directions'not in z:continue
     if len(z['directions'])!=38 or len(w['directions'])!=38:fail(bp,'38-directions-required');continue
     for j,(du,dv)in enumerate(zip(w['directions'],z['directions'])):
      walk(du,dv,D(v['direction_scales'][j]),bp+'/direction/'+str(j));counts['direction_vectors']+=1
     if set(z['parameter_directions'])!={'E','nu','c','phi','psi'}:fail(bp,'five-parameters-required')
     for name,dv in z['parameter_directions'].items():
      walk(w['parameter_directions'][name],dv,D(v['parameter_direction_scales'][name]),bp+'/parameter/'+name);counts['parameter_direction_vectors']+=1
    # Check the identity current-variable columns independently of stress-return math.
    if interface=='canonical':
     for j,seed in enumerate(data['seeds']):
      current=[D.from_float(float.fromhex(t))for t in seed['current']]
      if any(float.fromhex(t)!=0 for t in seed['parent']+seed['loading']):continue
      for branch,z in v['branches'].items():
       if z['status']!='defined':continue
       dz=z['directions'][j]
       if any(D(t)!=0 for t in dz['returned_atlas'])or list(map(D,dz['residual']))!=current:fail(path+'/'+branch+'/direction/'+str(j),'current-only-identity')
 return {'identity':'mc-stored-reference-internal-check-v1','policy_sha256':hashlib.sha256(Path(policy).read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(raw).hexdigest(),'counts':counts,'maximum_normalized_precision_difference':str(worst[0]),'maximum_difference_path':worst[1],'maximum_internal_normalized_residual':str(internalmax),'failures':failures,'passed':not failures,'compiled_observations':0,'scientific_admission':False,'reference_output_sha256':{str(Path(p).name):hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in(low,high)}}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('low');p.add_argument('high');p.add_argument('policy');a=p.parse_args();r=run(a.inputs,a.low,a.high,a.policy);print(json.dumps(r,indent=2,sort_keys=True));raise SystemExit(0 if r['passed']else 1)
