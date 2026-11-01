"""Independent source proportional-SPD reduction and candidate endpoint checks.
Decimal references are source differential solutions, not BE/FE integration.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import math,json,sys,hashlib
R=Path(__file__).resolve().parents[5];sys.path.insert(0,str(R))
from atlas.model import load,interpret,defaults
B=Path(__file__).resolve().parent.parent;model=load(B/'model.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
Q=[[F(1,9),F(8,9),F(4,9)],[F(8,9),F(1,9),F(-4,9)],[F(-4,9),F(4,9),F(-7,9)]]
assert all(sum(Q[i][k]*Q[j][k] for k in range(3))==int(i==j) for i in range(3) for j in range(3))
a=[F(11,10),F(1),F(9,10)]
A=[[sum(Q[i][k]*a[k]*Q[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
assert sum(A[i][i] for i in range(3))==3
f=F(27)/math.prod(a);assert f<F(33)
v=[float(A[i][i]) for i in range(3)]+[math.sqrt(2)*float(A[i][j]) for i,j in [(0,1),(1,2),(0,2)]]
refs=[];endpoint=[]
with localcontext() as c:
 c.prec=80
 for label,K,n,over in [('dense',2300,D('.8'),{}),('loose',1600,D('.86'),dict(k1=58,ft=33,A=.39,rf=.97,M=.00068,l=1.17,Kur=1600,n=.86))]:
  p={**defaults(model),**over}
  for amin in [D(1),D('.9')]:
   for p0 in [D(60000),D('1e-6'),D('1e-12'),D('1e-24')]:
    u0=p0/D(101325);crit=-(u0**(1-n))/((1-n)*K*amin**n)
    pressure={str(frac):str(p0*(1-frac)**(1/(1-n))) for frac in [D('.5'),D('.9'),D('.99')]}
    refs.append(dict(set=label,least_shape_eigenvalue=str(amin),initial_coefficient_pressure_Pa=str(p0),critical_proportional_strain=str(crit),source_coefficient_pressure_Pa=pressure))
  for p0 in [60000.,1e-6,1e-12,1e-24]:
   p1=.8*p0;E=K*101325*(.9*p0/101325)**float(n)
   old={'sigma':[p0*x for x in v],'q':p['ft']-float(f),'wp':0.}
   new={'sigma':[p1*x for x in v],'q':p['ft']-float(f),'wp':0.}
   de=[(p1-p0)/E*x for x in v]
   residual=interpret(model,new,old,de,p)
   # Stress residual was preconditioned by least previous pressure/pa.
   norm=max(abs(x)/101325 for x in residual['sigma'].v)
   assert norm<2e-12 and abs(residual['q'])<2e-12 and residual['wp']==0.
   endpoint.append(dict(set=label,initial_coefficient_pressure_Pa=p0,normalized_preconditioned_stress_residual=norm))
result={'id':'REVIEW-lade-domain-control-v1-left-source-reference','model_sha256':sha(B/'model.json'),'rotation_Q':[[str(x) for x in row] for row in Q],'shape_eigenvalues':[str(x) for x in a],'constant_f':str(f),'constant_f_less_than_both_ft':True,'proportional_source_equation':'d(p/pa)/d(epsilon)=Kur*amin**n*(p/pa)**n when S=p*A,de=A*d(epsilon),nu=0,f<ft','source_references_decimal_precision':80,'source_references':refs,'candidate_known_endpoint_checks':endpoint,'limits':['No native execution or candidate advance','Exact continuous source reference differs from discrete FE endpoint; endpoint residual checks explicitly use FE sampling','General3D changing stress direction/plasticity not reduced to scalar']}
Path(__file__).with_name('left-reference-results.json').write_text(json.dumps(result,indent=2)+'\n');print('16 high precision source references;8 rotated SPD candidate endpoint checks pass')
