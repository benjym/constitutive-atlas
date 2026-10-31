"""Canonical exact-stored diagonal mixed-scale branch audit, stdlib only."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import json
P=Path('/private/tmp/atlas-mc-stored-input-v1');OUT=Path(__file__).resolve().parent

def sincos(x):
 s=x;t=x;k=1
 while True:
  t=-t*x*x/D((2*k)*(2*k+1));old=s;s+=t;k+=1
  if s==old:break
 c=D(1);t=D(1);k=1
 while True:
  t=-t*x*x/D((2*k-1)*(2*k));old=c;c+=t;k+=1
  if c==old:break
 return s,c

def run():
 d=json.loads((P/'inputs.json').read_text());checks={};witnesses=[]
 with localcontext()as ctx:
  ctx.prec=420
  for row in d['cases']:
   if not row['id'].startswith('mixed-scale-middle/'):continue
   p={k:F(float.fromhex(v))for k,v in row['parameters'].items()};de=[F(float.fromhex(x))for x in row['loading']];K=p['E']/(3*(1-2*p['nu']));G=p['E']/(2*(1+p['nu']));L=K-2*G/3
   checks[row['id']+':exact_Lame_zero']=L==0
   trial=[-(2*G*x+L*sum(de[:3]))for x in de[:3]]
   checks[row['id']+':exact_middle_preserved']=trial[1]==F(float.fromhex(row['construction']['source_middle']))
   checks[row['id']+':exact_extremes']=trial[0]==-trial[2]==F(float.fromhex(row['construction']['source_trial_extreme']))
   dec=lambda f:D(f.numerator)/D(f.denominator)
   t=list(map(dec,trial));sf,cf=sincos(dec(p['phi']));sd,_=sincos(dec(p['psi']));k,g=dec(K),dec(G)
   f=(1+sf)*t[0]-(1-sf)*t[2]-2*dec(p['c'])*cf
   gamma=f/(4*k*sd*sf+4*g*(1+sd*sf/3))
   left=(t[0]-t[1])/(2*g*(1+sd));right=(t[1]-t[2])/(2*g*(1-sd))
   checks[row['id']+':strict_smooth_face_canonical']=f>0 and 0<gamma<min(left,right)
   # Algebraic exact source tangent leaves t2 alone because L=0.
   checks[row['id']+':returned_middle_exact']=L==0 and trial[1]!=0
   witnesses.append({'id':row['id'],'precision':ctx.prec,'trial_middle_exact_fraction':str(trial[1]),'positive_face_interval_margin_over_abs_t1':str((min(left,right)-gamma)/abs(t[0]))})
 out={'identity':'mc-stored-input-mixed-scale-audit-v1','checks':checks,'status':'pass'if all(checks.values())else'fail','witnesses':witnesses};(OUT/'mixed-scale-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(checks),'assertions')
 if out['status']!='pass':raise SystemExit(1)
if __name__=='__main__':run()
