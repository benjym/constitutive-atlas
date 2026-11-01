"""Distinct smooth strict-domain reference; original reference packet unchanged."""
from pathlib import Path
from decimal import localcontext,Decimal as Q
import json
from reference import history,compliance,residual,q
B=Path(__file__).resolve().parent
p=json.loads((B/'references.json').read_text())['cases'][0]['parameters'];cases=[]
for label,h in [('primary',70000.),('unload_reload',200000.)]:
 current=history([180000,140000,100000,16000,-9000,12000],h);previous=history([150000,120000,100000,4000,3000,-2000],h)
 with localcontext() as c:
  c.prec=160;de=list(map(float,compliance(current,previous,p)[0]));sweeps=[]
  for exponent in (12,16,20,24):
   columns=[]
   for j in range(20):
    scale=100000. if j<14 else 1.;step=q(2)**(-exponent)*q(scale);plus=[list(map(q,x)) for x in [current,previous,de]];minus=[x[:] for x in plus];block=0 if j<7 else 1 if j<14 else 2;index=j if j<7 else j-7 if j<14 else j-14;plus[block][index]+=step;minus[block][index]-=step
    rp=residual(*plus,p);rm=residual(*minus,p);columns.append([str((x-y)/(2*step)*q(scale)/Q(100000)) for x,y in zip(rp,rm)])
   sweeps.append(dict(exponent=exponent,columns=columns))
  cases.append(dict(id=label,current=current,previous=previous,de=de,parameters=p,sweeps=sweeps))
(B/'smooth-v2.json').write_text(json.dumps({'identity':'duncan-smooth-strict-domain-v2','derivatives':cases},indent=2)+'\n')
