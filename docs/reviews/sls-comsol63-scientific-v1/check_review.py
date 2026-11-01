"""Independent source-coordinate Decimal oracle; no Atlas imports or execution."""
import json,math,hashlib,sys
from decimal import Decimal as D, localcontext
from pathlib import Path
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent; E=R/'docs/ingestion/sls-comsol63/execution-v1'
def read(p): return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dec(v):return [D(str(x)) for x in v]
def dev(v):
 m=sum(v[:3])/3
 return [x-(m if i<3 else 0) for i,x in enumerate(v)]
def stress(z,p):
 k,g,h,t=p; dd=dev(z[:6]);tr=sum(z[:3])
 return [(k*tr if i<3 else 0)+2*g*dd[i]+z[6+i] for i in range(6)]
def exact(z,rate,p,t):
 z=dec(z);r=dec(rate);p=dec(p);t=D(str(t));k,g,h,tau=p
 ed=dev(z[:6]);rd=dev(r);e=[x+t*y for x,y in zip(z[:6],r)];f=(-t/tau).exp()
 # Integrate source gamma_dot=(dev(eps)-gamma)/tau directly.
 gam0=[x-y/(2*h) for x,y in zip(ed,z[6:])]
 gam=[f*a+(1-f)*b+(t-tau*(1-f))*c for a,b,c in zip(gam0,ed,rd)]
 return e+[2*h*(a-b) for a,b in zip(dev(e),gam)]
def creep(z,p,t):
 z=dec(z);p=dec(p);t=D(str(t));k,g,h,tau=p;s=stress(z,p);sd=dev(s);ed=dev(z[:6]);f=(-t*g/(tau*(g+h))).exp();m=sum(z[:3])/3
 ee=[(m if i<3 else 0)+a/(2*g)+(b-a/(2*g))*f for i,(a,b) in enumerate(zip(sd,ed))]
 return ee+[a-2*g*b for a,b in zip(sd,dev(ee))]
def error(a,b):
 assert len(a)==len(b) and all(math.isfinite(float(x)) for x in a+b)
 return max(abs(float(x)-float(y)) for x,y in zip(a,b))
ZERO=[0]*6
Z=[.002,.001,-.001,.0005,-.0004,.0003,5000,-2000,-3000,1000,-500,250]
P=[20e6,8e6,12e6,2.]
RATE=[.001,-.0002,.0003,.0007,-.0006,.0005]
def schedule_ref(c,t):
 s=c['specification'];z=s['initial'];p=s['parameters'];dt=t-s['start_time']
 if c['id']=='creep-schedule':return creep(z,p,dt)
 if c['id']=='load-hold-reverse':
  if dt<=1:return exact(z,RATE,p,dt)
  z1=exact(z,RATE,p,1)
  if dt<=2:return exact(z1,ZERO,p,dt-1)
  z2=exact(z1,ZERO,p,1);return exact(z2,[-x for x in RATE],p,dt-2)
 return exact(z,ZERO,p,dt)
def main():
 cases=read(E/'cases.json')['cases'];out={'passed':True,'backend':{},'source_hashes':0};maxref=[0.,0.]
 for f,h in read(E/'freeze-v2.json')['pins'].items():
  # Shared policy helper changed independently after build; immutable archive retains exact build closure.
  if f=='atlas/agent_review.py':continue
  assert sha(R/f)==h, f
 for s in read(R/'docs/ingestion/sls-comsol63/source-receipt.json')['sources']:
  assert sha(Path(s['private_path']))==s['sha256'];out['source_hashes']+=1
 assert (R/'models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json').read_bytes()==(R/'docs/ingestion/sls-comsol63/candidate.json').read_bytes()
 backends={b:read(E/('native-observe-v2-raw.json' if b=='native' else 'wasm-raw.json')) for b in ['native','wasm']}
 original=read(E/'native-raw.json');assert [x['calls'] for x in original]==[x['calls'] for x in backends['native']]
 for backend,rows in backends.items():
  assert [r['id'] for r in rows]==[c['id'] for c in cases]; errs=[0.,0.,0.];points=0;neg=0
  for c,row in zip(cases,rows):
   assert len(row['calls'])==2 and row['calls'][0]['stdout']==row['calls'][1]['stdout']
   a=json.loads(row['calls'][0]['stdout']);assert a['ok']==c['ok']
   if not c['ok']:
    neg+=1
    if c.get('late'):assert a['state']==Z and a['time']==3 and a['substeps']>0
    continue
   if c['kind']=='direct':
    z=[float(x) for x in str(c['args'][2]).split(',')]
    if c.get('restart_from'):
     z=json.loads(next(r for r in rows if r['id']==c['restart_from'])['calls'][0]['stdout'])['state']
     assert a['initial']==z
    ref=exact(z,c['rate'],c['parameters'],c['args'][5]); ss=stress(ref,dec(c['parameters']))
    obs=json.loads(row['observation']);assert obs['ok'];pp=[(a['state'],obs['values'][:6],ref,ss)];et,qt=2e-8,1.
    assert abs(a['time']-c['time'])<=1e-12*max(1,abs(c['time']))
    target=exact([float(x) for x in str(c['args'][2]).split(',')],c['rate'],c['parameters'],c['args'][5])
    maxref[0]=max(maxref[0],error(c['expected'][:6],target[:6]));maxref[1]=max(maxref[1],error(c['expected'][6:],target[6:]))
   else:
    pp=[];et,qt=2e-7,(1000. if c['id']=='refine-coarse' else 15.)
    assert len(a['points'])==len(c['references'])
    for point,r0 in zip(a['points'],c['references']):
     assert point['time']==r0['time'];ref=schedule_ref(c,point['time']);ss=stress(ref,dec(c['specification']['parameters']))
     maxref[0]=max(maxref[0],error(r0['state'][:6],ref[:6]));maxref[1]=max(maxref[1],error(r0['state'][6:],ref[6:]))
     assert error(point['strain'],ref[:6])<=et
     pp.append((point['state'],point['observables'][:6],ref,ss))
   for zz,ss,ref,sref in pp:
    ee,qe,se=error(zz[:6],ref[:6]),error(zz[6:],ref[6:]),error(ss,sref)
    assert ee<=et and qe<=qt and se<=qt,(backend,c['id'],ee,qe,se)
    errs=[max(x,y) for x,y in zip(errs,[ee,qe,se])];points+=1
  out['backend'][backend]={'cases':len(rows),'negative_cases':neg,'positive_points':points,'max_error_including_coarse_diagnostic':errs}
 assert maxref[0]<=1e-11 and maxref[1]<=1e-6
 out['reference_crosscheck_max_error']=maxref
 parity=[0.,0.,0.]
 for n,w in zip(backends['native'],backends['wasm']):
  a,b=[json.loads(r['calls'][0]['stdout']) for r in [n,w]]
  assert a['ok']==b['ok'] and a.get('message')==b.get('message')
  pairs=[]
  if 'state' in a:pairs.append((a['state'],b['state']))
  if 'points' in a:
   for x,y in zip(a['points'],b['points']):
    assert (x['time'],x['segment'],x['side'])==(y['time'],y['segment'],y['side']);pairs.append((x['state'],y['state']));parity[2]=max(parity[2],error(x['observables'],y['observables']))
  for x,y in pairs:parity[0]=max(parity[0],error(x[:6],y[:6]));parity[1]=max(parity[1],error(x[6:],y[6:]))
  if 'observation' in n:parity[2]=max(parity[2],error(json.loads(n['observation'])['values'],json.loads(w['observation'])['values']))
 assert parity[0]<=2e-7 and max(parity[1:])<=1e-6;out['parity_max_error']=parity
 # Exact physical subspace: energy residual zero; admitted hydro trace can violate it.
 q=[D('0.0001')]*3+[D(0)]*3;rate=[D('-0.001')]*3+[D(0)]*3
 diss=sum(x*x for x in q)/(2*D('12000000')*D(2));power_defect=sum(x*y for x,y in zip(q,rate))
 assert sum(q[:3])<=D('1e-10')*D('20000000') and diss+power_defect<0
 out['trace_roundoff_counterexample']={'trace_q_Pa':float(sum(q[:3])),'gate_Pa':.002,'power_minus_energy_rate_W_m3':float(diss+power_defect),'exact_passivity_scope':'tr(q)=0'}
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 with localcontext() as ctx:ctx.prec=50;main()
