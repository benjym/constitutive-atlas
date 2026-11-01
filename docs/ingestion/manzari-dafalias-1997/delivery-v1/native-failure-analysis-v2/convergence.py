#!/usr/bin/env python3
import math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;S=math.sqrt(2/3);M=.05
BASE=P.parent/'reference-v1';native=json.load(open('/private/tmp/atlas-predictor-constraints-v1/md-native-report-v3/report.json'))
axis=json.load(open(BASE/'reference-results.json'));interior=json.load(open(BASE/'interior-lode-v1/reference-results.json'))

def step(pn,bn,dt,cs):
 def residual(p,beta):
  psi=.65-(.8-.025*math.log(p/160));gb=2*(2/3.975)/((1+2/3.975)-(1-2/3.975)*cs);gd=2*(.07/4.2)/((1+.07/4.2)-(1-.07/4.2)*cs)
  bb=S*(1.14+gb*3.975*max(-psi,0)-M);bd=S*(1.14+gd*4.2*psi-M)
  b=bb-beta;br=2*S*(1.14+3.975*max(-psi,0)-M)
  assert br>abs(b) and b>0
  h=1200*abs(b)/(br-abs(b));D=2.64*(bd-beta);G=31400*(p/100)**.6
  gamma=(beta-bn)/(h*b)
  return [(p-pn+gamma*G*D)/160,(p*(beta+S*M)-pn*(bn+S*M)-2*G*(dt-gamma))/160],gamma
 p=pn;beta=bn+.001
 for it in range(40):
  r,gamma=residual(p,beta)
  if max(abs(x) for x in r)<1e-13:
   assert gamma>=0
   return p,beta
  dp=1e-4;db=1e-7
  rp,_=residual(p+dp,beta);rb,_=residual(p,beta+db)
  aa=(rp[0]-r[0])/dp;cc=(rp[1]-r[1])/dp;bb=(rb[0]-r[0])/db;dd=(rb[1]-r[1])/db;det=aa*dd-bb*cc
  xp=(-r[0]*dd+bb*r[1])/det;xb=(-aa*r[1]+r[0]*cc)/det
  for k in range(20):
   pp=p+2**-k*xp;bet=beta+2**-k*xb
   if pp<=0:continue
   rr,_=residual(pp,bet)
   if max(abs(x) for x in rr)<max(abs(x) for x in r):p,beta=pp,bet;break
  else:raise ValueError('descent failure')
 raise ValueError('iteration failure')

def main():
 out={'identity':'md1997-source-BE-truncation-study-v1','cases':{},'failures':[]}
 for name,cs,end,ref in [('undrained-dense-compression',1,.02,axis['cases']['undrained-dense-compression']),('dense-cos3theta-+0',0,.01,interior['cases']['dense-cos3theta-+0'])]:
  source={round(abs(s.get('axial_strain',s.get('t',0))),12):s for s in ref['checkpoints']}
  n=[S,-S/2,-S/2,0,0,0] if cs==1 else ref['n_mandel'];yieldcoord=axis['cases']['undrained-dense-compression']['first_yield_abs_axial'] if cs==1 else 0.
  results={}
  for res in [128,512,2048]:
   try:
    if res in [128,512]:controls=[abs(x['coordinate']) for x in native['cases'][name+'-'+str(res)]['points'] if abs(x['coordinate'])<=.002+1e-12]
    else:controls=sorted(set([0.,yieldcoord,.0005,.001,.002]+[i*end/res for i in range(1,res+1) if i*end/res<=.002]))
    p=160.;beta=0.;prev=0.;rows=[]
    for coord in controls[1:]:
     if coord<=yieldcoord+1e-14:prev=coord;continue
     dt=(coord-prev)/S if cs==1 else coord-prev
     p,beta=step(p,beta,dt,cs);prev=coord
     if round(coord,12) not in [.0005,.001,.002]:continue
     sig=[1000*p*((1 if i<3 else 0)+(beta+S*M)*v) for i,v in enumerate(n)];alpha=[beta*v for v in n];sr=source[round(coord,12)]
     row={'coordinate':coord,'sigma_Pa':sig,'alpha':alpha,'ODE_stress_error_Pa':max(abs(a-b) for a,b in zip(sig,sr['sigma_Pa'])),'ODE_alpha_error':max(abs(a-b) for a,b in zip(alpha,sr['alpha']))}
     if res in [128,512]:
      pt=next(x for x in native['cases'][name+'-'+str(res)]['points'] if abs(x['coordinate']-coord)<1e-12)
      row['native_stress_difference_Pa']=max(abs(a-b) for a,b in zip(sig,pt['state'][:6]));row['native_alpha_difference']=max(abs(a-b) for a,b in zip(alpha,pt['state'][7:13]))
      row['native_agreement']=row['native_stress_difference_Pa']<=.1 and row['native_alpha_difference']<=1e-6
     rows.append(row)
    results[str(res)]=rows
   except Exception as ex:out['failures'].append({'case':name,'resolution':res,'error':repr(ex)})
  out['cases'][name]=results
 (P/'convergence-results.json').write_text(json.dumps(out,indent=2)+'\n')
 (P/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file() and f.name!='manifest.json'},indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
