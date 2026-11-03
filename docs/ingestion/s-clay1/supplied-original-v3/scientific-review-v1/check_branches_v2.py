"""Reviewer source/candidate rotational corner algebra, no material solve."""
from pathlib import Path
import json,math
from atlas.model import load,evaluation_environment,interpret
O=Path(__file__).resolve().parent.parent;m=load(O/'candidate/s-clay1.json');base={f['name']:f['initial'] for f in m['state']};checks=0;rows=[]
for eta,a in [(.6,.42),(1.1,.42),(1.3,.42),(.42,.42),(0.,0.),(-.6,-.42)]:
 p=10000.;M=1.1;q=eta*p;pm=p+(q-a*p)**2/((M*M-a*a)*p)
 z={**base,'sigma':[p+2*q/3,p-q/3,p-q/3,0,0,0],'fabric':[2*a/3,-a/3,-a/3,0,0,0],'pm':pm,'gamma':.001}
 for beta,mu in [(.67,20.),(0.,20.),(.67,0.)]:
  params={k:f['default'] for k,f in m['parameters'].items()};params.update(beta=beta,mu=mu)
  e=evaluation_environment(m,z,z,[0]*6,params);res=interpret(m,z,z,[0]*6,params)
  pv=e['plastic_volume'];pd=e['plastic_shear']
  # Signed triaxial scalar q-alpha*p; A6 uses its magnitude.
  fvolume=2*M*M*p-2*a*q-(M*M-a*a)*pm
  fv=.001*fvolume/20000.;fd=.001*abs(2*(q-a*p))/20000.
  expected=mu*((.75*eta-a)*max(fv,0)+beta*(eta/3-a)*fd)
  actual=res['fabric'].v
  assert abs(pv-fv)<1e-15 and abs(pd-fd)<1e-15
  assert max(abs(x-y) for x,y in zip(actual,[-2*expected/3,expected/3,expected/3,0,0,0]))<1e-14
  checks+=3
  if mu==0:assert all(x==0 for x in actual);checks+=1
  if eta==a:assert abs(pd)<1e-15;checks+=1
  if eta==a==0:assert pd==0;checks+=1
  rows.append({'eta':eta,'alpha':a,'beta':beta,'mu':mu,'plastic_volume':pv,'plastic_shear':pd})
print(json.dumps({'ok':True,'checks':checks,'rows':rows,'scope':'source/candidate residual algebra including positive/zero/negative volume, zero shift, beta0 and mu0; no material trajectory'},indent=2))
