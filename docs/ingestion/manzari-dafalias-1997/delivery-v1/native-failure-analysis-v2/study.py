#!/usr/bin/env python3
import json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;S=math.sqrt(2/3)

def main():
 cs=json.loads((P/'case-snapshot.json').read_text());c=cs['drained-dense-compression-128'];pt=c['points'][-1];z=pt['state']
 pn=sum(z[:3])/3000;qn=(z[0]-z[1])/1000;an=z[7]-z[8];en=z[6]
 a=.00234375-pt['coordinate'];ref=160.
 def residual(p,alpha,b):
  v=a+2*b;e=en-1.65*v;psi=e-(.8-.025*math.log(p/160))
  B=1.14+3.975*max(-psi,0)-.05;Bd=1.14+4.2*psi-.05
  bn=S*(B-alpha);br=2*S*B;h=1200*abs(bn)/(br-abs(bn));D=2.64*S*(Bd-alpha)
  if psi>0 and D<0:D=0
  gamma=(alpha-an)/(h*(B-alpha));G=31400*(p/100)**.6
  q=p*(alpha+.05)
  return [(p-pn-G*v+gamma*G*D)/160,(q-qn-2*G*(a-b)+math.sqrt(6)*G*gamma)/160],{'p':p,'q':q,'alpha':alpha,'gamma':gamma,'e':e,'margin':br-abs(bn),'radial_stress_kPa':p-q/3}
 def solve(b):
  p=pn;alpha=an+.02
  for it in range(60):
   r,out=residual(p,alpha,b)
   if max(abs(x) for x in r)<1e-13:
    assert out['gamma']>=0 and out['margin']>0 and p>0
    return {**out,'iterations':it,'residual':r}
   dp=1e-4;da=1e-7
   rp,_=residual(p+dp,alpha,b);ra,_=residual(p,alpha+da,b)
   j00=(rp[0]-r[0])/dp;j10=(rp[1]-r[1])/dp;j01=(ra[0]-r[0])/da;j11=(ra[1]-r[1])/da
   det=j00*j11-j01*j10
   xp=(-r[0]*j11+j01*r[1])/det;xa=(-j00*r[1]+r[0]*j10)/det
   accepted=False
   for k in range(20):
    f=2**-k;pp=p+f*xp;aa=alpha+f*xa
    if pp<=0:continue
    rr,_=residual(pp,aa,b)
    if max(abs(x) for x in rr)<max(abs(x) for x in r):p=pp;alpha=aa;accepted=True;break
   if not accepted:raise ValueError('sourceNewtondescentfailed')
  raise ValueError('sourceNewtonlimit')
 result={'identity':'md1997-corrected-runtime-source-diagnostic-v2','initial':{'p_kPa':pn,'q_kPa':qn,'alpha_scalar':an,'e':en,'axial_increment':a},'control_iterations':[],'failures':[]}
 try:
  b=-.2*a;h=max(1e-9,abs(a)*1e-3)
  for it in range(30):
   root=solve(b);r=root['radial_stress_kPa']-ref
   entry={'iteration':it,'radial_increment':b,'source_BE_root':root,'control_residual_Pa':r*1000}
   result['control_iterations'].append(entry)
   if abs(r)*1000<.0016:break
   pert=solve(b+h);deriv=(pert['radial_stress_kPa']-root['radial_stress_kPa'])/h
   entry['derivative_kPa_per_strain']=deriv;entry['perturbation_BE_root']=pert
   cor=-r/deriv
   for k in range(11):
    bb=b+2**-k*cor;test=solve(bb)
    if abs(test['radial_stress_kPa']-ref)<abs(r):b=bb;break
   else:raise ValueError('outerdescentfailed')
  else:raise ValueError('outeriterationlimit')
  result['passed']=True
 except Exception as ex:result['failures'].append(repr(ex));result['passed']=False
 (P/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 (P/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'},indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
