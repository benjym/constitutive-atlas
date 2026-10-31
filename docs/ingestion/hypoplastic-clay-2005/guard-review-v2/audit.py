"""Independent bounded v2 guard audit. No compiled invocation or author code."""
import copy,hashlib,json,math,sys
from decimal import Decimal,localcontext
from pathlib import Path

REL='docs/ingestion/hypoplastic-clay-2005/rate-study-v2'
MARGIN=64*math.ulp(1.)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def independent_guard(z):
 with localcontext()as ctx:
  ctx.prec=150;q=[Decimal.from_float(float(x))for x in z[:6]];r=Decimal(2).sqrt();x,y,z,u,v,w=q
  A=[[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]
  scale=max(abs(x)for row in A for x in row)
  if not scale:return {'accepted':False,'zero':True}
  B=[[x/scale for x in row]for row in A];n=sum(x*x for row in B for x in row).sqrt();B=[[x/n for x in row]for row in B]
  m=B[0][0]*B[1][1]-B[0][1]*B[1][0]
  det=B[0][0]*(B[1][1]*B[2][2]-B[1][2]*B[2][1])-B[0][1]*(B[1][0]*B[2][2]-B[1][2]*B[2][0])+B[0][2]*(B[1][0]*B[2][1]-B[1][1]*B[2][0])
  positive=all(B[i][i]>0 for i in range(3));margin=Decimal.from_float(MARGIN)
  return {'accepted':positive and m>margin and det>margin,'spd':positive and m>0 and det>0,'minor':str(m),'det':str(det)}

def api(repo):
 sys.path.insert(0,str(repo))
 from atlas.model import load,defaults,evaluation_environment,prepare_increment
 from atlas.dsl import I,Sym,evaluate,parse
 model=load(repo/REL/'model.json');params=defaults(model)
 def guard(z):
  env={'I':I,'sigma':Sym(tuple(z[:6])),**params}
  try:
   for d in model['derived']:
    if not d['name'].startswith('support_'):break
    env[d['name']]=evaluate(parse(d['expr']),env)
   vals=[env[k]for k in ['support_norm','support_xx','support_yy','support_zz','support_minor2','support_det']]
   return {'accepted':all(math.isfinite(x)for x in vals)and all(evaluate(parse(g),env)for g in model['domain'][:6]),'values':vals}
  except(ArithmeticError,ValueError):return {'accepted':False,'arithmetic_rejection':True}
 def rate(c):
  state={'sigma':list(c['state'][:6]),'e':c['state'][6]};p=params|c['parameters'];saved=copy.deepcopy((state,p,c))
  prepare_increment(model,state,c['increment'],p);env=evaluation_environment(model,state,state,c['increment'],p)
  values=list(env['stress_rate'].v)+[env['e_rate']]
  assert all(type(x)in(int,float)and math.isfinite(x)for x in values)
  assert (state,p,c)==saved
  return values
 return model,guard,rate

def run(repo):
 p=repo/REL;model,guard,rate=api(repo);rows=[]
 # Both leading XY and omitted-in-v1 YZ/XZ shear adversaries, coordinate permutations.
 for factor in (-1.,0.,1e-20,1e-14,1e-12,1e-8,1.,2.):
  for axis in range(3):
   z=[1.,1.,1.,0.,0.,0.,.8];z[axis]=factor
   for scale in (1e-50,1.,1e50):
    q=[x*scale for x in z[:6]]+[.8];ideal=independent_guard(q);actual=guard(q)
    assert actual['accepted']==ideal['accepted'],('diagonal',q,ideal,actual)
    rows.append({'id':f'diagonal-{factor}-{axis}-{scale}','accepted':actual['accepted'],'spd':ideal['spd']})
 for shear in range(3):
  for x in (.5,math.nextafter(1.,0.),1.,math.nextafter(1.,2.),1.01):
   z=[1.,1.,1.,0.,0.,0.,.8];z[3+shear]=math.sqrt(2)*x
   ideal=independent_guard(z);actual=guard(z);assert actual['accepted']==ideal['accepted'],('shear',z,ideal,actual)
   rows.append({'id':f'shear-{shear}-{x}','accepted':actual['accepted'],'spd':ideal['spd']})
 # Exact diagonal normalized determinant lies on either side of the declared margin.
 for factor in (.5,.99,1.01,2.):
  z=[1.,1.,float(MARGIN*2*math.sqrt(2)*factor),0.,0.,0.,.8];a=guard(z);i=independent_guard(z);assert a['accepted']==i['accepted']
  rows.append({'id':f'margin-{factor}','accepted':a['accepted'],'spd':i['spd']})
 finite=[]
 for scale in (1e-300,1e-200,1e-150,1e-50,1.,1e50,1e150,1e200,1e300):
  z=[scale]*3+[0.]*3+[.8];a=guard(z);i=independent_guard(z)
  finite.append({'scale':scale,'ideal_guard':i['accepted'],'operational_guard':a['accepted'],'finite_domain_difference':a['accepted']!=i['accepted']})
 # Source Eq40 isotropic NCL load/unload; plus unloading gives kappa, not a minus-source variant.
 iso=[];params={'phi_c':math.radians(22.6),'lambda_star':.11,'kappa_star':.016,'N':1.375,'r':.4}
 for pressure in (.3,1e5,9247007.657539926):
  e=math.expm1(params['N']-params['lambda_star']*math.log(pressure/1000))
  for v in (-.003,0.,.003):
   c={'parameters':params,'state':[pressure]*3+[0.]*3+[e],'increment':[v/3]*3+[0.]*3};got=rate(c);want=pressure*v/(params['lambda_star']if v>=0 else params['kappa_star']);err=max(abs(x-want)for x in got[:3]);bound=1e-10+2e-12*max(1,abs(want));assert err<=bound
   assert max(abs(x)for x in got[3:6])==0
   iso.append({'p':pressure,'v':v,'expected_p_rate':want,'stress_error':err,'bound':bound})
 support=json.loads((p/'support-inputs.json').read_text())['cases'];reference=json.loads((p/'reference.json').read_text())['cases'];invalid=json.loads((p/'invalid-cases.json').read_text())['cases'];accepted=0
 for c in support:
  assert independent_guard(c['state'])['accepted']is c['expected_accepted'];assert guard(c['state'])['accepted']is c['expected_accepted']
  try:rate(c);success=True
  except(ArithmeticError,ValueError):success=False
  assert success is c['expected_accepted'];accepted+=success
 for c in invalid:
  try:rate(c)
  except(ArithmeticError,ValueError):pass
  else:raise AssertionError('invalid accepted:'+c['id'])
 prior=json.loads((repo/'docs/ingestion/hypoplastic-clay-2005/rate-study-v1/model.json').read_text())
 assert model['equations']==prior['equations'];assert [x for x in model['derived']if not x['name'].startswith('support_')]==prior['derived'];assert model['domain'][6:]==prior['domain']
 assert reference==json.loads((repo/'docs/ingestion/hypoplastic-clay-2005/rate-study-v1/reference.json').read_text())['cases']
 return {'version':'clay2005-v2-independent-guard-audit-0.1','adversarial_guard_cases':rows,'finite_regime_cases':finite,'independent_isotropic_NCL':iso,'frozen_accuracy_count':len(reference),'frozen_support_count':len(support),'frozen_support_accepted_finite_only':accepted,'frozen_support_rejections':len(support)-accepted,'frozen_numeric_invalids':len(invalid),'proposed_raw_rows':1+len(reference)+accepted+2*(len(invalid)+len(support)-accepted),'unchanged_rate_algebra':True,'compiled_execution':False,'admission':False}
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,required=True);a.add_argument('--output',type=Path);a.add_argument('--check',type=Path);args=a.parse_args();result=run(args.repo)
 if args.check:assert result==json.loads(args.check.read_text())
 if args.output:
  if args.output.exists():raise SystemExit('fresh output required')
  args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print('PASS',len(result['adversarial_guard_cases']),'adversarial guards;',result['proposed_raw_rows'],'proposed raw rows/backend')
