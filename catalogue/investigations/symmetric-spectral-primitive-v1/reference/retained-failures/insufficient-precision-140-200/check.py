"""Independent-reference convergence/residual checks; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,hashlib
P=Path(__file__).resolve().parent
POLICY={'identity':'Decimal-reference-internal-adequacy-v1','normalized_precision_difference_max':'1e-60','normalized_internal_residual_max':'1e-60','meaning':'Reference construction check only, not candidate acceptance or exact interval certification','normalization':'eigenvalues and pair values by maxabs eigenvalue (1 for zero tensor); projector by 1; directional eigenvalue and pair derivative by max Cartesian seed norm (1 for zero seed); projector derivative by max(1,maxabs highprecision derivative)'}

def run():
 a=json.loads((P/'reference-p140.json').read_text());b=json.loads((P/'reference-p200.json').read_text());assert not a['unresolved']and not b['unresolved'];assert a['seeds_mandel_hex']==b['seeds_mandel_hex'];count=0;worst=(D(0),'');failures=[]
 with localcontext() as c:
  c.prec=220
  def compare(x,y,scale,path):
   nonlocal count,worst
   e=abs(D(x)-D(y))/scale;count+=1
   if e>worst[0]:worst=(e,path)
   if e>D(POLICY['normalized_precision_difference_max']):failures.append({'path':path,'difference':str(e)})
  seeds=[]
  for h in b['seeds_mandel_hex']:
   v=[D.from_float(float.fromhex(x))for x in h];seed=max(abs(x)for x in v)or D(1);seeds.append(seed)
  for ca,cb in zip(a['cases'],b['cases']):
   assert ca['input']==cb['input'];x=ca['reference'];y=cb['reference'];tag=ca['input']['id'];scale=max(abs(D(v))for v in y['eigenvalues'])or D(1)
   for j in range(3):compare(x['eigenvalues'][j],y['eigenvalues'][j],scale,tag+'/eigenvalue/'+str(j))
   for k in ('max','mid','min'):
    u=x['selected'][k];v=y['selected'][k];assert u['status']==v['status']
    if v['status']!='isolated':continue
    for r in range(3):
     for s in range(3):compare(u['projector'][r][s],v['projector'][r][s],D(1),tag+'/'+k+'/P')
    for j,(du,dv)in enumerate(zip(u['directions'],v['directions'])):
     compare(du['eigenvalue'],dv['eigenvalue'],seeds[j],tag+'/'+k+'/Dlambda/'+str(j));ds=max(D(1),*(abs(D(z))for row in dv['projector']for z in row))
     for r in range(3):
      for s in range(3):compare(du['projector'][r][s],dv['projector'][r][s],ds,tag+'/'+k+'/DP/'+str(j))
   for k in ('upper','lower'):
    u=x['pair_sums'][k];v=y['pair_sums'][k];assert u['status']==v['status'];compare(u['value'],v['value'],scale,tag+'/'+k+'/sum')
    for j,(du,dv)in enumerate(zip(u.get('directions',[]),v.get('directions',[]))):compare(du,dv,seeds[j],tag+'/'+k+'/Dsum/'+str(j))
  residual={str(v['precision']):str(max(D(c['reference']['maximum_internal_normalized_residual'])for c in v['cases']))for v in(a,b)}
  for precision,value in residual.items():
   if D(value)>D(POLICY['normalized_internal_residual_max']):failures.append({'precision':precision,'internal_residual':value})
 return {'policy':POLICY,'cases':len(b['cases']),'columns':len(seeds),'numeric_fields_compared':count,'maximum_normalized_difference':str(worst[0]),'maximum_difference_path':worst[1],'maximum_internal_residual':residual,'failures':failures,'source_sha256':{f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in('generate.py','reference-p140.json','reference-p200.json')},'limits':'Precision agreement and polynomial identities are not rigorous root intervals or candidate correctness.'}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
