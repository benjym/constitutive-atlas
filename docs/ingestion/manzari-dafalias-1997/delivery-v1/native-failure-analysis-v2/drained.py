#!/usr/bin/env python3
import math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;S=math.sqrt(2/3)
R=json.load(open('/private/tmp/atlas-predictor-constraints-v1/md-native-report-v3/report.json'))
SRC=json.load(open(P.parent/'reference-v1/reference-results.json'))['cases']['drained-dense-compression']

def step(pn,an,en,a):
 qn=3*(pn-160)
 # Elastic constant lateral stress predictor (end-point pressure modulus).
 pe=pn
 for _ in range(15):
  K=31400*(pe/100)**.6
  f=4*(pe-pn)/(3*K)-a;d=4/(3*K)*(1-.6*(pe-pn)/pe)
  pe-=f/d
 ae=3*(pe-160)/pe-.05
 if ae<=an:
  v=(pe-pn)/(31400*(pe/100)**.6)
  return pe,an,en-1.65*v,0.,v
 def f(p,e):
  q=3*(p-160);alpha=q/p-.05;psi=e-(.8-.025*math.log(p/160));B=1.14+3.975*max(-psi,0)-.05;Bd=1.14+4.2*psi-.05
  bn=S*(B-alpha);br=2*S*B;h=1200*abs(bn)/(br-abs(bn));D=2.64*S*(Bd-alpha)
  if psi>0 and D<0:D=0
  gamma=(alpha-an)/(h*(B-alpha));K=31400*(p/100)**.6
  v=(p-pn)/K+gamma*D
  axial=(p-pn)/(3*K)+(q-qn)/(3*K)+gamma*(S+D/3)
  return [(axial-a),e-en+1.65*v],(alpha,gamma,v,br-abs(bn))
 p=pe;e=en
 for it in range(50):
  r,extra=f(p,e)
  if max(abs(x) for x in r)<1e-14:
   alpha,gamma,v,margin=extra;assert gamma>=-1e-15 and margin>0 and p>0
   return p,alpha,e,gamma,v
  dp=1e-4;de=1e-7;rp,_=f(p+dp,e);re,_=f(p,e+de)
  aa=(rp[0]-r[0])/dp;cc=(rp[1]-r[1])/dp;bb=(re[0]-r[0])/de;dd=(re[1]-r[1])/de;det=aa*dd-bb*cc
  xp=(-r[0]*dd+bb*r[1])/det;xe=(-aa*r[1]+r[0]*cc)/det
  p+=xp;e+=xe
 raise ValueError('Newton limit')

def main():
 out={'identity':'md1997-source-drained-BE-volume-v1','resolutions':{},'failures':[]}
 targets={round(abs(x['axial_strain']),12):x for x in SRC['checkpoints']}
 for res in [512,2048,8192]:
  try:
   native=R['cases']['drained-dense-compression-512']
   if res==512:controls=[abs(x['coordinate']) for x in native['points']]
   else:controls=sorted(set([0.,SRC['first_yield_abs_axial']]+[abs(x['axial_strain']) for x in SRC['checkpoints']]+[i*.02/res for i in range(1,res+1)]))
   p=160.;alpha=0.;e=.65;prev=0.;vol=0.;rows=[]
   for coord in controls[1:]:
    p,alpha,e,gamma,v=step(p,alpha,e,coord-prev);prev=coord;vol+=v
    if round(coord,12) not in [.0005,.001,.002,.005,.01,.02]:continue
    q=3*(p-160);sigma=[1000*(p+2*q/3),160000.,160000.,0,0,0];al=[2*alpha/3,-alpha/3,-alpha/3,0,0,0];source=targets[round(coord,12)]
    row={'coordinate':coord,'sigma_Pa':sigma,'alpha':al,'e':e,'void_closure_error':e-(.65-1.65*vol),'ODE_stress_error_Pa':max(abs(a-b) for a,b in zip(sigma,source['sigma_Pa'])),'ODE_alpha_error':max(abs(a-b) for a,b in zip(al,source['alpha'])),'ODE_e_error':abs(e-source['e'])}
    if res==512:
     n=next(x for x in native['points'] if abs(x['coordinate']-coord)<1e-12)
     row.update({'native_stress_difference_Pa':max(abs(a-b) for a,b in zip(sigma,n['state'][:6])),'native_alpha_difference':max(abs(a-b) for a,b in zip(al,n['state'][7:13])),'native_e_difference':abs(e-n['state'][6]),'native_fixed_e0_void_closure_error':n['state'][6]-(.65-1.65*sum(n['strain'][:3]))})
    rows.append(row)
   out['resolutions'][str(res)]=rows
  except Exception as ex:out['failures'].append({'resolution':res,'error':repr(ex),'coordinate':coord,'previous_p':p,'previous_alpha':alpha,'previous_e':e})
 (P/'drained-results.json').write_text(json.dumps(out,indent=2)+'\n')
 (P/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'},indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
