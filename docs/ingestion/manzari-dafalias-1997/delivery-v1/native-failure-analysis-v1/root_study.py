#!/usr/bin/env python3
import math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;S=math.sqrt(2/3);m=.05;p0=160.;x0=S*m

def coeff(p,beta):
 psi=.65-(.8-.025*math.log(p/160))
 gb=2*(2/3.975)/(1+2/3.975);gd=2*(.07/4.2)/(1+.07/4.2)
 bb=S*(1.14+gb*3.975*max(-psi,0)-m)
 bd=S*(1.14+gd*4.2*psi-m)
 b=bb-beta;br=2*S*(1.14+3.975*max(-psi,0)-m)
 assert br>abs(b) and b>0
 h=1200*abs(b)/(br-abs(b));D=2.64*(bd-beta)
 if psi>0 and D<0:D=0
 G=31400*(p/100)**.6
 gamma=beta/(h*b)
 return gamma,G,D,h,b,br

def pressure(beta):
 def f(p):
  gamma,K,D,*_=coeff(p,beta)
  return p-p0+gamma*K*D
 lo,hi=1.,160.;flo,fhi=f(lo),f(hi)
 assert flo<=0<=fhi,(beta,flo,fhi)
 for _ in range(100):
  mid=(lo+hi)/2
  if f(mid)>0:hi=mid
  else:lo=mid
 return (lo+hi)/2

def stressroot(beta,t):
 p=pressure(beta);gamma,G,D,h,b,br=coeff(p,beta)
 return p*(beta+x0)-p0*x0-2*G*(t-gamma)

def main():
 r={'identity':'md1997-source-BE-local-root-v1','cases':[],'failures':[]}
 for div in [1,2,16384]:
  t=.01/128/div
  try:
   lo,hi=0.,.1;fl,fh=stressroot(lo,t),stressroot(hi,t)
   assert fl<0<fh
   bracket={'beta':[lo,hi],'stress_residual_kPa':[fl,fh]}
   for _ in range(100):
    mid=(lo+hi)/2
    if stressroot(mid,t)>0:hi=mid
    else:lo=mid
   beta=(lo+hi)/2;p=pressure(beta);gamma,G,D,h,b,br=coeff(p,beta)
   residual=[(p-p0+gamma*G*D)/160,(p*(beta+x0)-p0*x0-2*G*(t-gamma))/160,beta-gamma*h*b]
   assert max(abs(x) for x in residual)<=1e-11
   assert p>0 and gamma>=0 and br>abs(b)
   # The gamma=0 elastic predictor solves its mechanical equations, but violates yield.
   predictor_x=x0+2*(31400*(160/100)**.6)*t/160
   yield_scaled=160*(predictor_x-x0)/160
   r['cases'].append({'subdivision':div,'strain_amplitude':t,'bracket':bracket,'p_Pa':p*1000,'beta':beta,'gamma':gamma,'D':D,'bref_minus_abs_b':br-abs(b),'normalized_residual':residual,'yield_error':0.,'elastic_predictor_yield_scaled':yield_scaled,'predictor_violates_1e8_solution_constraint':yield_scaled>1e-8})
  except Exception as ex:r['failures'].append({'subdivision':div,'error':repr(ex)})
 r['passed']=len(r['cases'])==3 and not r['failures']
 (P/'results.json').write_text(json.dumps(r,indent=2)+'\n')
 (P/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'},indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
