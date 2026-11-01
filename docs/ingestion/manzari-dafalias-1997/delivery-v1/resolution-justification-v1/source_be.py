#!/usr/bin/env python3
"""Independent scalar original-1997 backward Euler on fixed coaxial paths.
No production evaluator, compiler, interpreter or compiled artifact imports.
"""
import math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;BASE=P.parent;S=math.sqrt(2/3);M=.05

def coefficients(p,e,cs,beta):
 if p<=0:raise ValueError('pressure')
 psi=e-(.8-.025*math.log(p/160))
 gb=2*(2/3.975)/((1+2/3.975)-(1-2/3.975)*cs)
 gd=2*(.07/4.2)/((1+.07/4.2)-(1-.07/4.2)*cs)
 bb=S*(1.14+gb*3.975*max(-psi,0)-M);bd=S*(1.14+gd*4.2*psi-M)
 b=bb-beta;br=2*S*(1.14+3.975*max(-psi,0)-M)
 if br<=abs(b):raise ValueError('hardening distance')
 h=1200*abs(b)/(br-abs(b));D=2.64*(bd-beta)
 if psi>0 and D<0:D=0
 return 31400*(p/100)**.6,D,h,b,br-abs(b)

def newton(f,x,steps):
 for it in range(50):
  r,extra=f(x);err=max(abs(v) for v in r)
  if err<1e-13:
   assert err<=1e-11
   return x,extra,err,it
  jac=[[0.]*3 for _ in range(3)]
  for j,h in enumerate(steps):
   xx=x.copy();xx[j]+=h;rr,_=f(xx)
   for i in range(3):jac[i][j]=(rr[i]-r[i])/h
  mat=[row+[-v] for row,v in zip(jac,r)]
  for k in range(3):
   pivot=max(range(k,3),key=lambda i:abs(mat[i][k]));mat[k],mat[pivot]=mat[pivot],mat[k]
   if abs(mat[k][k])<1e-20:raise ValueError('singular source Newton')
   for i in range(k+1,3):
    fac=mat[i][k]/mat[k][k]
    for j in range(k,4):mat[i][j]-=fac*mat[k][j]
  delta=[0.]*3
  for i in range(2,-1,-1):delta[i]=(mat[i][3]-sum(mat[i][j]*delta[j] for j in range(i+1,3)))/mat[i][i]
  for k in range(20):
   xx=[v+2**-k*d for v,d in zip(x,delta)]
   try:rr,_=f(xx)
   except (ValueError,OverflowError):continue
   if max(abs(v) for v in rr)<err:x=xx;break
  else:raise ValueError('source Newton descent')
 raise ValueError('source Newton limit')

def isochoric(pn,sn,bn,e,dt,cs):
 G=31400*(pn/100)**.6;elastic_s=sn+2*G*dt
 if elastic_s/pn-bn<=S*M+1e-15:return pn,elastic_s,bn,0.,0.,0
 def f(x):
  p,beta,gamma=x;K,D,h,b,margin=coefficients(p,e,cs,beta)
  return [(p-pn+gamma*K*D)/160,(p*(beta+S*M)-sn-2*K*(dt-gamma))/160,beta-bn-gamma*h*b],(margin,gamma)
 x,extra,err,it=newton(f,[pn,bn+100*dt,dt*.5],[1e-4,1e-7,1e-8]);p,beta,gamma=x
 if gamma<0:raise ValueError('negative gamma')
 return p,p*(beta+S*M),beta,extra[0],err,it

def drained(pn,an,en,a,e0,z):
 qn=3*(pn-160);pe=pn
 for _ in range(20):
  K=31400*(pe/100)**.6;f=4*(pe-pn)/(3*K)-a;df=4/(3*K)*(1-.6*(pe-pn)/pe);pe-=f/df
 qe=3*(pe-160)
 if z*(qe/pe-an)<=M+1e-15:
  v=(pe-pn)/(31400*(pe/100)**.6)
  return pe,an,en-(1+e0)*v,v,0.,0.,0
 def f(x):
  p,e,gamma=x;q=3*(p-160);alpha=q/p-z*M;beta=S*z*alpha
  K,D,h,b,margin=coefficients(p,e,z,beta)
  v=(p-pn)/K+gamma*D
  axial=(p-pn)/(3*K)+(q-qn)/(3*K)+gamma*(z*S+D/3)
  return [axial-a,e-en+(1+e0)*v,alpha-an-gamma*h*(z*(beta+b)/S-alpha)],(alpha,v,margin)
 x,extra,err,it=newton(f,[pe,en,abs(a)],[1e-4,1e-7,1e-8]);p,e,gamma=x;alpha,v,margin=extra
 if gamma<0:raise ValueError('negative gamma')
 return p,alpha,e,v,margin,err,it

def check(row,cp,axis):
 ss=max(abs(a-b)/(100+.01*max(1000,abs(b))) for a,b in zip(row['sigma_Pa'],cp['sigma_Pa']))
 aa=max(abs(a-b)/.002 for a,b in zip(row['alpha'],cp['alpha']))
 ee=abs(row['e']-cp['e'])/.0002
 rr=abs(row['radial_strain']-cp['radial_strain'])/.0002 if axis else 0
 return {'stress':ss,'alpha':aa,'e':ee,'radial':rr,'worst':max(ss,aa,ee,rr),'passed':max(ss,aa,ee,rr)<=1}

def main():
 path=BASE/'resolution-study-v4/requests.json';plan=json.loads(path.read_text())
 assert hashlib.sha256(path.read_bytes()).hexdigest()=='dc02829df6c1e1b3500781bb5c3c7dc6728897a64b2cd50bd56ef60d99a89d10'
 out={'identity':'md1997-independent-crosspath-BE-2048-4096-v1','requests_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':{},'failures':[],'refinement':[]}
 for c in plan['cases']:
  if c['group'] not in ['axis','interior']:continue
  cid=c['id'];axis=c['group']=='axis';isdrained=axis and c['protocol']==1
  controls=c['controls'] if axis else c['coordinates'];cpmap={cp.get('axial_strain',cp.get('t')):cp for cp in c['checkpoints']}
  z=1 if controls[-1]>0 else -1;e0=c['initial'][6];e=e0;p=160.;beta=0.;rad=0.;prev=0.;alpha=0.
  if axis:n=[z*S,-z*S/2,-z*S/2,0,0,0];cs=z;s=0.
  else:n=c['direction'];cs=math.sqrt(6)*sumvalcube(n);s=p*S*M
  rows=[];maxerr=0.;minmargin=math.inf;maxiterations=0
  def save(coord):
   sig=[1000*((p if i<3 else 0)+s*v) for i,v in enumerate(n)]
   row={'coordinate':coord,'p_Pa':p*1000,'sigma_Pa':sig,'alpha':[beta*v for v in n],'e':e}
   if axis:row['radial_strain']=rad
   row['source_error']=check(row,cpmap[coord],axis);rows.append(row)
  if 0. in cpmap:save(0.)
  try:
   for coord in controls[1:]:
    dc=coord-prev
    if isdrained:
     p,alpha,e,v,margin,err,it=drained(p,alpha,e,dc,e0,z);s=z*S*3*(p-160);beta=S*z*alpha;rad+=(v-dc)/2
    else:
     dt=z*dc/S if axis else dc;p,s,beta,margin,err,it=isochoric(p,s,beta,e,dt,cs)
     if axis:rad-=dc/2
    maxerr=max(maxerr,err);maxiterations=max(maxiterations,it)
    if margin>0:minmargin=min(minmargin,margin)
    prev=coord
    if coord in cpmap:save(coord)
   out['cases'][cid]={'completed':True,'checkpoints':rows,'max_local_residual':maxerr,'min_hardening_margin':minmargin,'max_Newton_iterations':maxiterations,'source_gates_passed':all(r['source_error']['passed'] for r in rows)}
  except Exception as ex:
   fail={'case':cid,'coordinate':coord,'error':repr(ex),'last_coordinate':prev};out['failures'].append(fail);out['cases'][cid]={'completed':False,'checkpoints':rows,'failure':fail}
 for cid,c in out['cases'].items():
  if not cid.endswith('-4096'):continue
  coarse=out['cases'].get(cid[:-5]+'-2048',{});cm={r['coordinate']:r for r in coarse.get('checkpoints',[])}
  for r in c['checkpoints']:
   coord=r['coordinate']
   if coord==0:continue
   f=r['source_error']['worst'];co=cm.get(coord,{}).get('source_error',{}).get('worst',math.inf)
   out['refinement'].append({'case':cid,'coordinate':coord,'fine':f,'coarse':co if math.isfinite(co) else None,'passed':math.isfinite(co) and (f<co or max(f,co)<1e-5)})
 out['completed_cases']=sum(c['completed'] for c in out['cases'].values());out['source_gate_failures']=[{'case':cid,'coordinate':r['coordinate'],**r['source_error']} for cid,c in out['cases'].items() for r in c['checkpoints'] if not r['source_error']['passed']]
 out['passed']=out['completed_cases']==28 and not out['failures'] and not out['source_gate_failures'] and all(r['passed'] for r in out['refinement'])
 (P/'results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'passed':out['passed'],'completed_cases':out['completed_cases'],'root_failures':out['failures'],'source_gate_failures':out['source_gate_failures'],'refinement_failures':[r for r in out['refinement'] if not r['passed']]},indent=2))

def sumvalcube(n):
 x,y,z,u,v,w=n;xy=u/math.sqrt(2);yz=v/math.sqrt(2);xz=w/math.sqrt(2)
 return x**3+y**3+z**3+3*((x+y)*xy**2+(y+z)*yz**2+(x+z)*xz**2)+6*xy*yz*xz
if __name__=='__main__':main()
