"""Independent Cartesian Decimal continuous oracle; no Atlas/DSL/author imports."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import argparse,gzip,json
ZERO=D(0);ONE=D(1)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),ZERO)
def tr(a):return a[0]+a[4]+a[8]
def dev(a):
 p=tr(a)/3;return [x-(p if i in (0,4,8)else 0)for i,x in enumerate(a)]
def square(a):return [sum((a[3*i+k]*a[3*k+j]for k in range(3)),ZERO)for i in range(3)for j in range(3)]
def parameters(raw):return {k:D(v)for k,v in raw.items()}
def elastic(p,e,k):
 G=k['G0']*k['p_at']*(D('2.97')-e)**2/(1+e)*(p/k['p_at']).sqrt()
 return G,2*(1+k['nu'])/(3*(1-2*k['nu']))*G
class Unsupported(ValueError):pass

def rates(y,v,e,k,diagnostic=False):
 s,a,z=y[:9],y[9:18],y[18:];p=tr(s)/3
 if p<=0 or not 0<e<D('2.97')or 1-k['ch']*e<=0:raise Unsupported('pressure/void domain')
 r=[x/p for x in dev(s)];w=[x-b for x,b in zip(r,a)];norm=dot(w,w).sqrt()
 if norm==0:raise Unsupported('undefined normal')
 n=[x/norm for x in w];n2=square(n);cube=dot(n,n2);c3=D(6).sqrt()*cube
 g=2*k['c']/((1+k['c'])-(1-k['c'])*c3)
 psi=e-k['e0']+k['lambda_c']*(p/k['p_at'])**k['xi'];root=(D(2)/3).sqrt()
 ab=root*(g*k['M']*(-k['nb']*psi).exp()-k['m'])
 ad=root*(g*k['M']*(k['nd']*psi).exp()-k['m'])
 b=[ab*x-y for x,y in zip(n,a)];Ad=k['A0']*(1+max(ZERO,dot(z,n)))
 dil=Ad*(ad-dot(a,n));B=1+D('1.5')*(1-k['c'])/k['c']*g*c3
 C=3*(D(3)/2).sqrt()*(1-k['c'])/k['c']*g
 flow=[B*x-C*(q-(ONE/3 if i in(0,4,8)else 0))for i,(x,q)in enumerate(zip(n,n2))]
 distance=dot(a,n) # fixed zero anchor; no event/reset rule
 if distance<0:raise Unsupported('negative fixed-memory distance')
 G,K=elastic(p,e,k);b0=k['G0']*k['h0']*(1-k['ch']*e)/(p/k['p_at']).sqrt()
 Hbar=D(2)/3*p*b0*dot(b,n);E=2*G*(B-C*cube)-K*dil*dot(n,r)
 denom=Hbar+distance*E
 if (distance==0 and Hbar<=0)or denom==0:raise Unsupported('singular hardening/loading')
 loading=2*G*dot(n,v) # trace(v)=0, so the disputed Eq20 K term vanishes
 q=max(ZERO,loading/denom);L=distance*q
 ds=[2*G*x-L*(2*G*f+(K*dil if i in(0,4,8)else 0))for i,(x,f)in enumerate(zip(v,flow))]
 da=[D(2)/3*b0*q*x for x in b]
 dz=[-k['cz']*max(ZERO,-L*dil)*(k['zmax']*x+y)for x,y in zip(n,z)]
 if diagnostic:return {'p':p,'yield_Pa':p*(norm-root*k['m']),'distance':distance,'Hbar':Hbar,'denominator':denom,'dilatancy':dil,'plastic_loading':L,'c3':c3}
 return ds+da+dz
# Dormand-Prince 5(4), exact rational tableau; numerical choice is separate from law.
A=[[],[(1,5)],[(3,40),(9,40)],[(44,45),(-56,15),(32,9)],[(19372,6561),(-25360,2187),(64448,6561),(-212,729)],[(9017,3168),(-355,33),(46732,5247),(49,176),(-5103,18656)],[(35,384),(0,1),(500,1113),(125,192),(-2187,6784),(11,84)]]
B5=[(35,384),(0,1),(500,1113),(125,192),(-2187,6784),(11,84),(0,1)]
B4=[(5179,57600),(0,1),(7571,16695),(393,640),(-92097,339200),(187,2100),(1,40)]
def rk(y,h,fn):
 ks=[]
 for row in A:
  yy=[yi+h*sum((D(n)/d*ks[j][i]for j,(n,d)in enumerate(row)),ZERO)for i,yi in enumerate(y)]
  ks.append(fn(yy))
 def combination(b):return [yi+h*sum((D(n)/d*ks[j][i]for j,(n,d)in enumerate(b)),ZERO)for i,yi in enumerate(y)]
 return combination(B5),combination(B4)
def mandel(a):return [a[i]for i in[0,4,8]]+[D(2).sqrt()*a[i]for i in[1,5,2]]
def formatted(x):
 with localcontext()as ctx:ctx.prec=35;return str(+x)
def run(case,raw,precision,tol):
 with localcontext()as ctx:
  ctx.prec=precision;k=parameters(raw);p0=D(case['pressure_Pa']);e=D(case['void_ratio']);v=list(map(D,case['direction_cartesian']))
  assert tr(v)==0 and v[1]==v[3]and v[2]==v[6]and v[5]==v[7]
  G,_=elastic(p0,e,k);entry=p0*(D(2)/3).sqrt()*k['m']/(2*G*dot(v,v).sqrt());end=D(case['end_parameter'])
  initial=[p0 if i in(0,4,8)else ZERO for i in range(9)]+[ZERO]*18
  y=[x+2*G*entry*v[i]for i,x in enumerate(initial[:9])]+[ZERO]*18;t=entry
  fn=lambda y:rates(y,v,e,k);h=(end-entry)/100;scales=[p0]*9+[ONE]*18
  accepted=rejected=0;samples=[];tol=D(tol)
  def sample(t,y,kind):
   d=rates(y,v,e,k,True)if kind!='initial'else {'p':p0,'yield_Pa':-(D(2)/3).sqrt()*p0*k['m'],'distance':ZERO,'Hbar':ZERO,'denominator':ZERO,'dilatancy':ZERO,'plastic_loading':ZERO,'c3':ZERO}
   state=mandel(y[:9])+[e]+mandel(y[9:18])+mandel(y[18:])+[ZERO]*6
   d.update(alpha_trace=tr(y[9:18]),fabric_trace=tr(y[18:]),stress_asymmetry=max(abs(y[3*i+j]-y[3*j+i])for i in range(3)for j in range(3)))
   return {'parameter':formatted(t),'kind':kind,'state':list(map(formatted,state)),'strain':list(map(formatted,mandel([t*x for x in v]))),'diagnostics':{n:formatted(x)for n,x in d.items()}}
  samples.extend([sample(ZERO,initial,'initial'),sample(entry,y,'first_yield')])
  for j in range(1,17):
   target=entry+(end-entry)*j/16
   while t<target:
    if accepted+rejected>=20000:raise Unsupported('reference attempt budget')
    h=min(h,target-t)
    if h<D('1e-30'):raise Unsupported('reference minimum step')
    try:
     high,low=rk(y,h,fn);error=max(abs(a-b)/s for a,b,s in zip(high,low,scales));rates(high,v,e,k)
    except Unsupported:
     rejected+=1;h/=2;continue
    if error>tol:rejected+=1;h*=max(D('.1'),D('.9')*(tol/error)**D('.2'));continue
    t+=h;y=high;accepted+=1
    h*=2 if error==0 else min(D(2),max(D('.2'),D('.9')*(tol/error)**D('.2')))
   samples.append(sample(t,y,'plastic'))
  return {'id':case['id'],'precision':precision,'local_tolerance':str(tol),'accepted':accepted,'rejected':rejected,'samples':samples}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--precision',type=int,required=True);ap.add_argument('--tolerance',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 here=Path(__file__).resolve().parent;inputs=json.loads((here/'inputs.json').read_text());rows=[]
 for c in inputs['cases']:
  try:r=run(c,inputs['parameters'],args.precision,args.tolerance);r['status']='generated'
  except Exception as exc:r={'id':c['id'],'status':'failed','exception':repr(exc)}
  rows.append(r);print(c['id'],r['status'],r.get('accepted'),flush=True)
 result={'kind':'independent-continuous-reference','precision':args.precision,'local_tolerance':args.tolerance,'cases':rows}
 with args.output.open('xb')as f:
  f.write(gzip.compress((json.dumps(result,indent=2)+'\n').encode(),mtime=0))
 if any(r['status']=='failed'for r in rows):raise SystemExit(2)
if __name__=='__main__':main()
