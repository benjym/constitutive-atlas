"""Read-only frozen-input audit and known-endpoint algebra; no material advance."""
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction
import json,hashlib,math,sys
HERE=Path(__file__).resolve().parent;B=HERE.parent;R=HERE.parents[4];sys.path.insert(0,str(R))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((B/'prospective-freeze.json').read_text())
for row in freeze['files']:assert sha(R/row['path'])==row['sha256'],row['path']
from atlas.model import load,interpret,defaults
m=load(B/'model.json');old=load(B.parent/'domain-control-v1/model.json')
a=json.loads((B/'model.json').read_text());b=json.loads((B.parent/'domain-control-v1/model.json').read_text())
for key in ['parameters','state','residual','formulation','inputs']:
 if key in a or key in b:assert a.get(key)==b.get(key),key
assert (B/'path_error_control.hpp').read_bytes()==(B.parent/'domain-control-v1/path_error_control.hpp').read_bytes()
proof=[]
with localcontext() as c:
 c.prec=80
 for n in [D('.8'),D('.86')]:
  for v in [D('.999'),D('.9'),D('.5'),D('.01'),D('1e-6')]:
   length=(1-v)/(((1+v)/2)**n);exact=(1-v**(1-n))/(1-n)
   assert 0<length<exact
   proof.append(dict(n=str(n),v=str(v),ratio=str(length/exact)))
Q=[[Fraction(x,9) for x in row] for row in [[1,8,4],[8,1,-4],[-4,4,-7]]]
A=[[sum(Q[i][k]*[Fraction(11,10),1,Fraction(9,10)][k]*Q[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
direction=[float(A[i][i]) for i in range(3)]+[math.sqrt(2)*float(A[i][j]) for i,j in [(0,1),(1,2),(0,2)]]
checks=[]
for label,over in [('dense',{}),('loose',dict(k1=58,ft=33,A=.39,rf=.97,M=.00068,l=1.17,Kur=1600,n=.86))]:
 p={**defaults(m),**over}
 for p0 in [60000.,1e-6,1e-12,1e-24]:
  p1=.8*p0;E=p['Kur']*p['pa']*(.9*(p0+p1)/(2*p['pa']))**p['n']
  previous=dict(sigma=[p0*x for x in direction],q=p['ft']-300/11,wp=0.)
  endpoint=dict(sigma=[p1*x for x in direction],q=p['ft']-300/11,wp=0.)
  residual=interpret(m,endpoint,previous,[(p1-p0)/E*x for x in direction],p)
  err=max(abs(x)/p['pa'] for x in residual['sigma'].v)
  assert err<2e-12 and abs(residual['q'])<2e-12 and residual['wp']==0
  checks.append(dict(set=label,p0=p0,scaled_stress_residual=err))
result=dict(id='REVIEW-lade-midpoint-v4-prospective',freeze_sha256=sha(B/'prospective-freeze.json'),closed_files=len(freeze['files']),model_sha256=sha(B/'model.json'),same_generic_controller=True,midpoint_inequalities=proof,known_rotated_endpoints=checks,limits=['Python algebra/interpreter only; no nonlinear advance or compiled execution','No numerical qualification, general3D event theorem or E5 approval'])
(HERE/'prospective-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(closed_files=len(freeze['files']),inequalities=len(proof),known_endpoints=len(checks),freeze_sha256=result['freeze_sha256'])))
