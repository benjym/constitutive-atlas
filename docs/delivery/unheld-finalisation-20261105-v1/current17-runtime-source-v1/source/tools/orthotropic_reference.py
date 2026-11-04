"""Independent exact-rational compliance solve; no production equations imported."""
from fractions import Fraction as F
import json,random
from pathlib import Path
MODEL='orthotropic-linear-elastic-ogs'
PARAMETERS=[30e6,45e6,60e6,12e6,18e6,15e6,.2,.25,.15]
SETTINGS=[1e-11,1e-6,60,0,1,20]
def rat(x):return F.from_float(x) if isinstance(x,float) else F(x)
def compliance(p):
 a,b,c,g,h,j,n,m,l=map(rat,p);z=F(0)
 return [[1/a,-n/a,-l/a,z,z,z],[-n/a,1/b,-m/b,z,z,z],[-l/a,-m/b,1/c,z,z,z],[z,z,z,1/(2*g),z,z],[z,z,z,z,1/(2*h),z],[z,z,z,z,z,1/(2*j)]]
def solve(A,b):
 a=[list(row)+[v] for row,v in zip(A,b)]
 for k in range(len(a)):
  pivot=next(i for i in range(k,len(a)) if a[i][k]);a[k],a[pivot]=a[pivot],a[k];t=a[k][k];a[k]=[x/t for x in a[k]]
  for i in range(len(a)):
   if i!=k:
    t=a[i][k];a[i]=[x-t*y for x,y in zip(a[i],a[k])]
 return [row[-1] for row in a]
def stiffness(p):
 S=compliance(p);cols=[solve(S,[F(i==j) for i in range(6)]) for j in range(6)]
 return [[float(cols[j][i]) for j in range(6)] for i in range(6)]
def update(p,z,de):return [float(rat(x)+y) for x,y in zip(z,solve(compliance(p),list(map(rat,de))))]
def csv(v):return ','.join(format(x,'.17g') if isinstance(x,(int,float)) else x for x in v)
def case(label,p,z,de,mode='integrate',ok=True,previous=None):
 args=[MODEL,csv(p),csv(z),csv(de),csv(SETTINGS)]
 out=dict(id=label,mode=mode,parameters=p,initial=z,strain=de,ok=ok,call=dict(function='atlas_'+('linearize' if mode=='linearize' else 'integrate')+'_with_settings',types=['string']*5,args=args),argv=['--mode',mode,'--model',MODEL,'--parameters',args[1],'--initial',args[2],'--strain',args[3],'--integration-settings',args[4]])
 if previous:out['previous']=previous
 if ok:
  out['expected_state']=update(p,z,de)
  if mode=='linearize':out['expected_tangent']=stiffness(p)
 return out

def corpus():
 rng=random.Random(20261102);p=PARAMETERS;z=[0]*6;cases=[]
 for j in range(6):
  d=[0]*6;d[j]=.001;cases.append(case('basis-'+str(j),p,z,d))
 for i in range(48):
  q=[rng.uniform(.7,1.4)*x for x in p[:6]]+[rng.uniform(-.12,.24) for _ in range(3)];a=[rng.uniform(-2e5,2e5) for _ in range(6)];d=[rng.uniform(-.004,.004) for _ in range(6)];cases.append(case('general-'+str(i),q,a,d))
 for label,q in [('isotropic',[35e6]*3+[35e6/2.5]*3+[.25]*3),('auxetic',p[:6]+[-.2,-.1,-.15])]:
  for j in range(6):
   d=[0]*6;d[j]=-.001;cases.append(case(label+'-'+str(j),q,[1e5,-3e4,9e4,1234,-2345,3456],d))
 for i,scale in enumerate([.0001,.01,1,100]):
  q=[x*scale for x in p[:6]]+p[6:];cases.append(case('unit-scale-'+str(i),q,[x*scale for x in [1e5,2e5,-1e5,400,500,-600]],[.001,-.0004,.0002,.0007,-.0003,.0008]));cases.append(case('tangent-'+str(i),q,[0]*6,[.001,-.0005,.0002,.0003,-.0002,.0001],mode='linearize'))
 for i in range(6):cases.append(case('zero-'+str(i),p,[rng.uniform(-1e6,1e6) for _ in range(6)],[0]*6))
 load=[.001,-.0002,.0003,.0004,-.0005,.0006]
 paths=[('public',[[*load],[-x for x in load],[0]*6],[0]*6),('history',[[.001,0,0,0,0,0],[0,.001,0,0,0,0],[0,0,0,.001,-.001,.0005],[-.001,-.001,0,-.001,.001,-.0005],[0]*6],[1000,-2000,3000,40,-50,60])]
 full=[.002,-.001,.0005,.0006,-.0007,.0008]
 paths += [('partition-'+str(n),[[x/n for x in full]]*n,[0]*6) for n in [1,2,4]]
 for label,rs,a in paths:
  prev=None
  for i,d in enumerate(rs):
   name=f'{label}-{i}';c=case(name,p,a,d,previous=prev);cases.append(c);a=c['expected_state'];prev=name
 bad=[]
 for j in range(6):
  q=p.copy();q[j]=-1;bad.append(('negative-modulus-'+str(j),q))
 for label,ns in [('negative-pair',[1,.25,.15]),('negative-determinant',[.6,.6,.6]),('indefinite-normal',[0,1,0])]:bad.append((label,p[:6]+ns))
 for label,q in bad:
  cases.append(case(label,q,[1e5,2e5,3e5,400,500,600],[.001]*6,ok=False));cases.append(case('recovery-'+label,p,[1e5,2e5,3e5,400,500,600],[.001,-.0005,0,.0003,0,-.0002]))
 for label,zbad,dbad in [('nonfinite-state',['nan',0,0,0,0,0],[0]*6),('nonfinite-increment',[0]*6,['inf',0,0,0,0,0]),('wrong-state',[0]*5,[0]*6),('wrong-increment',[0]*6,[0]*5)]:
  cases.append(case(label,p,zbad,dbad,ok=False));cases.append(case('recovery-'+label,p,[0]*6,[.001,0,0,0,0,0]))
 return cases

def assess(cases,rows):
 assert len(cases)==len(rows);count=failures=tangents=0
 for c,row in zip(cases,rows):
  d=row['response'];assert c['id']==row['id'];assert d.get('ok') is c['ok'],(c['id'],d)
  if not c['ok']:
   failures+=1
   if 'state' in d:assert d['state']==c['initial'],(c['id'],'rollback')
   continue
  assert d['model']==MODEL and len(d['state'])==6;scale=max(c['parameters'][:6]);budget=5e-10+2e-11*scale
  for a,b in zip(d['state'],c['expected_state']):assert abs(a-b)<=budget,(c['id'],a,b,budget);count+=1
  assert d['parameters']==c['parameters'] and d['strain']==c['strain']
  assert d['diagnostics']['increment_fractions']==[1] and d['diagnostics']['substeps']==1
  if c['mode']=='linearize':
   assert d['tangent_ok'] is True and len(d['state_tangent'])==6
   for a,b in zip(sum(d['state_tangent'],[]),sum(c['expected_tangent'],[])):assert abs(a-b)<=1e-7+2e-10*scale,(c['id'],'tangent',a,b);tangents+=1
 lookup={r['id']:r['response'] for r in rows}
 for n in [2,4]:
  for a,b in zip(lookup[f'partition-{n}-{n-1}']['state'],lookup['partition-1-0']['state']):assert abs(a-b)<=.0012
 return dict(ok=True,cases=len(cases),reference_scalars=count,tangent_scalars=tangents,rejections=failures,partition_counts=[1,2,4])
if __name__=='__main__':
 import sys
 Path(sys.argv[1]).write_text(json.dumps(dict(provenance='Pinned OGS Kelvin compliance solved by independent Fraction Gaussian elimination; no production expressions imported',settings=SETTINGS,state_budget='5e-10 Pa+2e-11*max(Ei,Gi)',tangent_budget='1e-7 Pa+2e-10*max(Ei,Gi)',cases=corpus()),indent=2,allow_nan=False)+'\n');print(len(corpus()),'prospective cases')
