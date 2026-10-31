"""Independent source-reduced axisymmetric perfect-plastic MC reference.
No Atlas imports, spectral decomposition, Newton solve or candidate evaluation.
"""
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path
import json,sys,hashlib
ZERO=D(0)
def h(x):return D.from_float(float.fromhex(x))
def sincos(x):
 import decimal
 cutoff=D(10)**(-(decimal.getcontext().prec+8));xx=x*x;s=term=x;k=1
 while abs(term)>cutoff:term*= -xx/D((2*k)*(2*k+1));s+=term;k+=1
 c=term=D(1);k=1
 while abs(term)>cutoff:term*= -xx/D((2*k-1)*(2*k));c+=term;k+=1
 return s,c

def parameters(p):
 E,nu,c,phi,psi=[h(p[k])for k in('E','nu','c','phi','psi')];s,cf=sincos(phi);d,cd=sincos(psi)
 assert E>0 and -1<nu<D('.5') and c>0 and 0<s<1 and 0<d<1 and cf>0
 K=E/(3*(1-2*nu));G=E/(2*(1+nu));L=K-2*G/3
 return dict(E=E,nu=nu,c=c,s=s,d=d,cf=cf,K=K,G=G,L=L,h=2*c*cf,apex=-c*cf/s)
def elastic(ea,er,p):return ((p['L']+2*p['G'])*ea+2*p['L']*er,p['L']*ea+(2*p['L']+2*p['G'])*er)
def yield_(a,r,p):return (1-p['s'])*max(a,r)-(1+p['s'])*min(a,r)-p['h']
def flow(branch,p):
 d=p['d'];return (1-d,-(1+d)/2)if branch=='compression'else(-1-d,(1-d)/2)if branch=='extension'else(-2*d/3,-2*d/3)
def return_step(a,r,ea,er,p):
 da,dr=elastic(ea,er,p);at,rt=a+da,r+dr;Ftrial=yield_(at,rt,p)
 if Ftrial<=0:return at,rt,ZERO,'elastic',(at,rt)
 branch='compression'if at>rt else'extension';u,v=flow(branch,p);ca,cr=elastic(u,v,p)
 den=(1-p['s'])*ca-(1+p['s'])*cr if branch=='compression'else(1-p['s'])*cr-(1+p['s'])*ca
 assert den>0;gamma=Ftrial/den;an,rn=at-gamma*ca,rt-gamma*cr
 if (branch=='compression'and an>=rn)or(branch=='extension'and an<=rn):return an,rn,gamma,branch,(at,rt)
 gamma=(p['apex']-(at+2*rt)/3)/(2*p['K']*p['d']);assert gamma>=0
 return p['apex'],p['apex'],gamma,'apex',(at,rt)
def controlled(a,r,du,protocol,rref,p):
 E,nu,K,G,s,d=p['E'],p['nu'],p['K'],p['G'],p['s'],p['d']
 if protocol in(0,2,4):
  ea=du;er=ZERO if protocol==0 else-du/2 if protocol==2 else du
  an,rn,g,b,t=return_step(a,r,ea,er,p);return an,rn,ea,er,g,b,t
 if protocol==1:
  assert r==rref
  lo=((1-s)*rref-p['h'])/(1+s);hi=((1+s)*rref+p['h'])/(1-s)
  trial=a+E*du;an=min(hi,max(lo,trial));ee=(an-a)/E;ep=du-ee
  if trial>hi:b='compression';ratio=-(1+d)/(2*(1-d));g=ep/(1-d)
  elif trial<lo:b='extension';ratio=-(1-d)/(2*(1+d));g=ep/(-1-d)
  else:b='elastic';ratio=ZERO;g=ZERO
  er=-nu*ee+ratio*ep;ea=du;da,dr=elastic(ea,er,p)
  return an,rref,ea,er,g,b,(a+da,r+dr)
 if protocol==3:
  q=a-r;pold=(a+2*r)/3;qn=q+du
  ap=pold+2*qn/3;rp=pold-qn/3
  if yield_(ap,rp,p)<=0:pn=pold;g=ZERO;b='elastic';ea=du/(3*G)
  elif qn>0:
   b='compression';pn=((1-s/3)*qn-p['h'])/(2*s);g=(pn-pold)/(2*K*d);ea=(du+G*(3-d)*g)/(3*G)
  else:
   b='extension';pn=(-(1+s/3)*qn-p['h'])/(2*s);g=(pn-pold)/(2*K*d);ea=(du-G*(3+d)*g)/(3*G)
  assert g>=0;er=-ea/2;an=pn+2*qn/3;rn=pn-qn/3;da,dr=elastic(ea,er,p)
  return an,rn,ea,er,g,b,(a+da,r+dr)
 raise ValueError('unknown protocol')
def encode(x):
 if isinstance(x,D):return format(x,'.80E')if x else'0'
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [encode(v)for v in x]
 return x
def run(data,precision):
 paths=[]
 with localcontext()as ctx:
  ctx.prec=precision
  p=parameters(data['parameters']);initial=list(map(h,data['initial']));assert len(initial)==6 and initial[0]==initial[1]==initial[2]and all(x==0 for x in initial[3:])
  for req in data['paths']:
   assert len(req['control_targets'])==len(req['control_deltas'])
   protocol=req['protocol'];a,r=initial[:2];rref=r;sa=sr=ZERO;plasticvol=ZERO;checks=[];points=[];previous_target=ZERO
   def point(target,b,g):return {'control':target,'state':[a,r,r,ZERO,ZERO,ZERO],'strain':[sa,sr,sr,ZERO,ZERO,ZERO],'q':a-r,'mean_stress':(a+2*r)/3,'pore_pressure':rref-r if protocol in(2,3)else ZERO,'gamma':g,'branch':b,'accumulated_plastic_volumetric_strain':plasticvol}
   points.append(point(ZERO,'initial',ZERO))
   for idx,(target,delta)in enumerate(zip(req['control_targets'],req['control_deltas']),1):
    target,du=h(target),h(delta);ao,ro=a,r;an,rn,ea,er,g,b,(at,rt)=controlled(a,r,du,protocol,rref,p);scale=max(D(1),p['c'],abs(at),abs(rt),abs(an),abs(rn));u,v=flow(b,p);u=ZERO if b=='elastic'else u;v=ZERO if b=='elastic'else v
    if b=='apex':u=((at-an)/g+2*p['L']*p['d'])/(2*p['G']);v=((rt-rn)/g+2*p['L']*p['d'])/(2*p['G'])
    ca,cr=elastic(u,v,p)
    defects={'equilibrium_a':abs(an-(at-g*ca))/scale,'equilibrium_r':abs(rn-(rt-g*cr))/scale,'yield_violation':max(ZERO,yield_(an,rn,p))/scale,'plastic_complementarity':abs(g*yield_(an,rn,p))/max(D(1),abs(g)*scale),'flow_trace':abs(g*(u+2*v+2*p['d']))if b!='elastic'else ZERO,'flow_subgradient_bounds':max(ZERO,u-(1-p['d']),v-(1-p['d']),(-1-p['d'])-u,(-1-p['d'])-v)if b!='elastic'else ZERO}
    if g<0:raise ArithmeticError('negative source multiplier')
    if b=='compression'and an<rn:raise ArithmeticError('compression order')
    if b=='extension'and an>rn:raise ArithmeticError('extension order')
    if protocol==0:defects['zero_lateral_strain']=abs(er)
    if protocol==1:defects['drained_radial_stress']=abs(rn-rref)/scale
    if protocol in(2,3):defects['constant_volume']=abs(ea+2*er)
    if protocol==3:defects['q_control']=abs((an-rn)-(ao-ro)-du)/scale
    else:defects['strain_control']=abs(ea-du)
    if protocol==4:defects['isotropic_stress']=abs(an-rn)/scale;defects['isotropic_strain']=abs(ea-er)
    a,r=an,rn;sa+=ea;sr+=er;plasticvol+=-2*p['d']*g;points.append(point(target,b,g));checks.append({'step':idx,'defects':defects});previous_target=target
   paths.append({'id':req['id'],'protocol':protocol,'points':points,'checks':checks})
 return encode({'identity':'mc-axisymmetric-source-reference-v1','precision':precision,'parameters':p,'paths':paths,'candidate_calls':0,'compiled_observations':0})
if __name__=='__main__':
 data=json.loads(Path(sys.argv[1]).read_bytes());res=run(data,int(sys.argv[2]));Path(sys.argv[3]).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'paths':len(res['paths']),'points':sum(len(p['points'])for p in res['paths']),'precision':res['precision'],'candidate_calls':0}))
