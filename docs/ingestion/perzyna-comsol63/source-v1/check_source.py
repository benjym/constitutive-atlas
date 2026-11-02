"""Source-derived analytical checks, separate from compiled solver agreement."""
import hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
import oracle as o
from atlas.model import load,interpret,observe
from atlas.initialization import initialize_state
m=load(HERE/'candidate.json');checks=[];cases=[]
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)});assert condition,name
for channel in range(6):
 unit=[0.]*6;unit[channel]=1.;sd=o.dev(unit);q=o.equivalent(sd);N=[x/q for x in sd]
 for ratio in [0.,.5,1.,1.001,2.,-2.]:
  for n in [1.,1.5,2.,3.,8.]:
   p=o.P[:];p[4]=n;z=[ratio*p[2]/(2*p[1])*v for v in N]+[0.]*7
   named={'eps':z[:6],'eps_vp':z[6:12],'alpha':z[12]};params=dict(zip(m['parameters'],p))
   r=interpret(m,named,params,o.ZERO,time=0.);sig=list(observe(m,named,o.ZERO,params,time=0.)['stress'].v)
   # Independent pairwise diagonal/shear invariant, not dev/norm composition.
   q=math.sqrt(((sig[0]-sig[1])**2+(sig[1]-sig[2])**2+(sig[2]-sig[0])**2)/2+1.5*math.fsum(v*v for v in sig[3:]))
   lam=p[3]*max(q/p[2]-1.,0.)**n
   actual=list(r['eps_vp'].v)+[r['alpha']]
   h=1e-5;a=o.relaxation(z,h,p);b=o.relaxation(z,h/2,p)
   derivative=[2*(y-v)/(h/2)-(x-v)/h for v,x,y in zip(z,a,b)][6:]
   case=f'ch{channel}-ratio{ratio:g}-n{n:g}'
   check(case+'-exact-derivative',max(abs(a-b) for a,b in zip(actual,derivative))<2e-9)
   check(case+'-dissipation',abs(math.fsum(s*v for s,v in zip(sig,actual[:6]))-q*lam)<1e-7)
   check(case+'-traceless',abs(math.fsum(actual[:3]))<1e-13)
   x=o.relaxation(z,.7,p);y=o.relaxation(x,.4,p);end=o.relaxation(z,1.1,p)
   check(case+'-semigroup',max(abs(a-b) for a,b in zip(y,end))<2e-14)
   check(case+'-nondecreasing-alpha',end[12]>=z[12])
   c=o.creep(z,1.1,p);check(case+'-fixed-creep-stress',max(abs(a-b) for a,b in zip(o.stress(c,p),sig))<1e-7)
   cases.append({'id':case,'parameters':p,'initial':z,'duration':1.1,'relaxation':{'state':end,'stress':o.stress(end,p)},'creep':{'state':c,'stress':o.stress(c,p)}})
# Admissibility checks include mandatory explicit state, no impossible accumulated history.
params=dict(zip(m['parameters'],o.P));valid={'eps':o.Z[:6],'eps_vp':[0.]*6,'alpha':0.}
check('explicit-overstress-initialization',initialize_state(m,valid,params,time=0.,loading=o.ZERO)['initial']==o.Z)
for label,bad in [('missing-history',{'eps':o.Z[:6],'alpha':0.}),('negative-alpha',{**valid,'alpha':-1.}),('volumetric-vp',{**valid,'eps_vp':[.01,0,0,0,0,0]}),('unrealizable-alpha',{**valid,'eps_vp':[.01,-.005,-.005,0,0,0]})]:
 try:initialize_state(m,bad,params,time=0.,loading=o.ZERO)
 except (ValueError,KeyError):check(label+'-reject',True)
 else:check(label+'-reject',False)
R=[[0.,-1.,0.],[.8,0.,-.6],[.6,0.,.8]]
rot=o.rotate_state(o.Z,R);expected=o.rotate_state(o.relaxation(o.Z,2.),R)
check('passive-rotation-relaxation',max(abs(a-b) for a,b in zip(o.relaxation(rot,2.),expected))<1e-14)
for r in json.loads((HERE/'source-receipts.json').read_text())['receipts']:
 check('source-bytes-'+Path(r['path']).name,hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'])
(HERE/'analytical-references.json').write_text(json.dumps({'identity':'perzyna-source-analytical-v1','independent_of_compiled_solver':True,'cases':cases},indent=2)+'\n')
(HERE/'SOURCE-CHECKS.json').write_text(json.dumps({'passed':all(x['passed'] for x in checks),'analytical_cases':len(cases),'checks':checks,'compiled_execution':False},indent=2)+'\n')
print(json.dumps({'passed':True,'cases':len(cases),'checks':len(checks),'compiled_execution':False}))
