"""Independent exact axisymmetric perfect-Tresca/Hooke recurrence; standard library only."""
from fractions import Fraction as F
from pathlib import Path
import json
P=Path(__file__).parent

def rational(x):return F.from_float(float(x))
def record(state,strain,control,branch):
 return {'state':[str(x)for x in state],'strain':[str(x)for x in strain],'control':str(control),'branch':branch}
def path(case):
 z=list(map(rational,case['initial']));eps=[F(0)]*6;p_ref,lam,mu,k=map(rational,case['parameters']);K=lam+2*mu/3;E=mu*(3*lam+2*mu)/(lam+mu);w=2*k;protocol=case['protocol'];radial=z[1];q=z[0]-z[1];mean=(z[0]+2*z[1])/3
 rows=[record(z,eps,F(0),'initial')];last=F(0);failure=None;certificates=0
 for step,raw in enumerate(case['controls'][1:],1):
  control=rational(raw);inc=control-last;qold=q;old=z[:];oldmean=mean
  if protocol==3:
   wanted=q+inc
   if abs(wanted)>w:failure=step;break
   da=inc/(3*mu);dl=-da/2;qtrial=wanted;q=wanted;branch='elastic'
  else:
   da=inc
   if protocol==1:
    qelastic=q+E*da;q=min(w,max(-w,qelastic));dl=((q-qold)/(3*K)-da)/2
   else:dl=da if protocol==4 else -da/2 if protocol==2 else F(0)
   qtrial=qold+2*mu*(da-dl)
   q=min(w,max(-w,qtrial));branch='elastic' if q==qtrial else 'plastic-positive' if q==w else 'plastic-negative'
  mean+=K*(da+2*dl)
  z[:6]=[mean+2*q/3,mean-q/3,mean-q/3,F(0),F(0),F(0)]
  dplastic=[(qtrial-q)/(3*mu),-(qtrial-q)/(6*mu),-(qtrial-q)/(6*mu),F(0),F(0),F(0)]
  de=[da,dl,dl,F(0),F(0),F(0)]
  z[6:]=[a+b for a,b in zip(z[6:],dplastic)];eps=[a+b for a,b in zip(eps,de)]
  # Exact source-equation and control certificates; no decimal tolerances.
  assert abs(q)<=w and sum(dplastic[:3])==0
  assert (qtrial-q)*q>=0
  for i in range(6):
   delta=z[i]-old[i];vol=lam*(da+2*dl) if i<3 else F(0)
   assert delta==vol+2*mu*(de[i]-dplastic[i]);certificates+=1
  assert mean-oldmean==K*(da+2*dl)
  if protocol==1:assert z[1]==radial and z[2]==radial
  if protocol in (2,3):assert sum(de[:3])==0
  if protocol==3:assert q-qold==inc
  if protocol==4:assert dplastic==[F(0)]*6
  last=control;rows.append(record(z,eps,control,branch))
 return {'points':rows,'failure_step':failure,'exact_hooke_certificates':certificates}
def generate(inputs):
 return {c['label']:path(c)for c in inputs['cases']if c['kind']in ('success','prefix-failure')}
if __name__=='__main__':
 refs=generate(json.loads((P/'inputs.json').read_text()));(P/'references.json').write_text(json.dumps(refs,indent=2)+'\n');print('exact reference paths',len(refs),'Hooke certificates',sum(v['exact_hooke_certificates']for v in refs.values()))
