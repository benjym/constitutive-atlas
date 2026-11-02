"""E5 reviewer-owned saved-data checks. Never loads a material binary or writes author evidence."""
import json,hashlib,math,sys,zipfile,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; B=ROOT/'docs/ingestion/perzyna-comsol63'; OUT=Path(__file__).parent
read=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
e4=read(B/'E4-EVIDENCE.json')
for p,h in e4['files'].items():assert sha(ROOT/p)==h,p
receipts=read(B/'source-v1/source-receipts.json')['receipts']
for r in receipts:assert sha(r['path'])==r['sha256']
retention=read(B/'PRIVATE-SOURCE-RETENTION.json')
for r in retention['members']:assert sha(r['retained_path'])==r['sha256']
index=read(B/'asset-provision-v1/INDEX.json');assert sha(ROOT/index['archive']['path'])==index['archive']['sha256']
with zipfile.ZipFile(ROOT/index['archive']['path']) as z:
 assert set(z.namelist())==set(index['files'])
 for p,h in index['files'].items():assert hashlib.sha256(z.read(p)).hexdigest()==h
receipt=read(B/'execution-v1/build-receipt.json')
for key,n in [('module','perzyna.mjs'),('wasm','perzyna.wasm'),('metadata','generated/models.json')]:assert receipt['artifacts'][key]['sha256']==index['files'][n]
for backend in ['native','wasm']:
 pre=read(B/f'execution-v2/actual-v1/{backend}-pre.json');post=read(B/f'execution-v2/actual-v1/{backend}-post.json')
 assert post['pre_receipt_sha256']==sha(B/f'execution-v2/actual-v1/{backend}-pre.json') and post['all_records_unchanged']
 assert 'fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702' in json.dumps(pre)
 for stage in ['configure','build','qualification']:
  operation=read(B/f'execution-v2/actual-v1/{backend}-{stage}.json');assert operation['returncode']==0 and operation['preverified'] and operation['postverified']
  if stage=='build':assert operation['argv'][-4:]==['--target','atlas_perzyna_solver','--parallel','1']
  assert sha(B/f'execution-v2/actual-v1/{backend}-{stage}.log')==operation['log_sha256']
# Tensor algebra written independently here, rather than importing author oracle.
def deviator(x):
 m=sum(x[:3])/3;return [v-m if i<3 else v for i,v in enumerate(x)]
def stress(z,p):
 e=[z[i]-z[i+6] for i in range(6)];d=deviator(e);v=p[0]*sum(e[:3]);return [2*p[1]*d[i]+(v if i<3 else 0) for i in range(6)]
def qvalue(s):return math.sqrt(1.5*sum(x*x for x in deviator(s)))
def exact(z,p,dt,creep):
 s=deviator(stress(z,p));q=qvalue(s);K,G,Y,A,n=p;lam=A*max(q/Y-1,0)**n
 if creep:
  change=[dt*1.5*lam*x/q if q else 0 for x in s];return [z[i]+change[i] for i in range(6)]+[z[i+6]+change[i] for i in range(6)]+[z[12]+lam*dt]
 if q<=Y:return z[:]
 u=q/Y-1;c=3*G*A/Y
 end=u*math.exp(-c*dt) if n==1 else (u**(1-n)+(n-1)*c*dt)**(1/(1-n))
 qend=Y*(1+end);fraction=(1-qend/q)/(2*G)
 return z[:6]+[z[i+6]+fraction*s[i] for i in range(6)]+[z[12]+(q-qend)/(3*G)]
def rk(z,p,rate,dt,N):
 # Integrate stress and equivalent strain using elastic balance in seven coordinates.
 K,G,Y,A,n=p;d=deviator(rate);elastic=[2*G*d[i]+(K*sum(rate[:3]) if i<3 else 0) for i in range(6)]
 def f(x):
  s=deviator(x[:6]);q=qvalue(s);lam=A*max(q/Y-1,0)**n
  factor=3*G*lam/q if q else 0
  return [elastic[i]-factor*s[i] for i in range(6)]+[lam]
 x=stress(z,p)+[z[12]];h=dt/N
 for _ in range(N):
  k1=f(x);k2=f([x[i]+h*k1[i]/2 for i in range(7)]);k3=f([x[i]+h*k2[i]/2 for i in range(7)]);k4=f([x[i]+h*k3[i] for i in range(7)])
  x=[x[i]+h/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]) for i in range(7)]
 ep=[z[i]+rate[i]*dt for i in range(6)];sd=deviator(x[:6]);v=sum(x[:3])/(9*K)
 return ep+[ep[i]-sd[i]/(2*G)-(v if i<3 else 0) for i in range(6)]+[x[6]]
cases=read(B/'execution-v2/cases.json')['cases'];checks={};analytic_points=0;rate_points=0;rkcomparisons=[]
# Existing strict assessor is reused only for schema/transaction gate replay; independent algebra below checks accuracy.
sys.path.insert(0,str(B/'execution-v2'));import study
for backend in ['native','wasm']:
 rows=read(B/f'execution-v2/{backend}-attempt1.json');report=study.assess(cases,rows);assert report==read(B/f'execution-v2/{backend}-attempt1-report.json')
 maxstate=maxstress=maxrate=0
 for j,(case,row) in enumerate(zip(cases,rows)):
  if not case['ok'] or case['id']=='refinement-coarse':continue
  result=json.loads(row['calls'][0]['stdout']);spec=result;p=spec['parameters'];z=spec['initial'];segs=spec['segments']
  allhold=all(all(c['kind']=='hold' for c in seg['controls']) for seg in segs)
  if not allhold:continue
  creep=all(c['quantity']=='stress' for c in segs[0]['controls'])
  for point in result['points']:
   ref=exact(z,p,point['time']-spec['start_time'],creep)
   for a,b in zip(point['state'],ref):assert abs(a-b)<=max(3e-7,2e-5*abs(b));maxstate=max(maxstate,abs(a-b))
   for a,b in zip(point['observables'],stress(ref,p)):assert abs(a-b)<=max(3,2e-5*abs(b));maxstress=max(maxstress,abs(a-b))
   analytic_points+=1
   if creep and point['side']=='left' and point['segment']>=0:
    s=deviator(stress(z,p));q=qvalue(s);lam=p[3]*max(q/p[2]-1,0)**p[4]
    for a,x in zip(point['strain_rate'],s):
     b=1.5*lam*x/q if q else 0;assert abs(a-b)<=max(1e-10,2e-5*abs(b));maxrate=max(maxrate,abs(a-b));rate_points+=1
 checks[backend]={'cases':report['cases'],'state_stress_comparisons':report['numeric_comparisons'],'maximum_analytical_state_error':maxstate,'maximum_analytical_stress_error_Pa':maxstress,'maximum_creep_rate_error_per_s':maxrate,'refinement':{k:report['errors'][k] for k in ['refinement-coarse','refinement-fine']}}
# Independently coded RK4, all 26 loading reference intervals, low/high grids and saved references.
for c in cases:
 if not c['ok']:continue
 spec=c['specification'];segments=spec['segments']
 if not any(any(x['kind']=='rate' for x in s['controls']) for s in segments):continue
 z=spec['initial'];time=spec['start_time'];p=spec['parameters']
 for seg in segments:
  rate=[x.get('value',0) for x in seg['controls']];dt=seg['duration']/seg['samples']
  for _ in range(seg['samples']):
   lo=rk(z,p,rate,dt,8192);hi=rk(z,p,rate,dt,16384);time+=dt
   target=next(r for r in c['references'] if abs(r['time']-time)<1e-12)
   ds=max(abs(a-b) for a,b in zip(lo,hi));de=max(abs(a-b) for a,b in zip(stress(lo,p),stress(hi,p)))
   assert ds<5e-11 and de<.005,(c['id'],ds,de)
   assert max(abs(a-b) for a,b in zip(hi,target['state']))<5e-11
   assert max(abs(a-b) for a,b in zip(stress(hi,p),target['stress']))<.005
   rkcomparisons.append({'case':c['id'],'time':time,'state_grid_error':ds,'stress_grid_error_Pa':de});z=hi
native=read(B/'execution-v2/native-attempt1.json');wasm=read(B/'execution-v2/wasm-attempt1.json')
ignore={'substeps','rejected','iterations','backtracks','error','temporal_error_norm','nonlinear_residual_norm'}
parity_count=0
def same(a,b):
 global parity_count
 if isinstance(a,dict):
  assert set(a)==set(b)
  for k in a:
   if k not in ignore:same(a[k],b[k])
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):same(x,y)
 else:
  assert a==b
  if type(a) in (int,float):parity_count+=1
for a,b in zip(native,wasm):
 assert a['id']==b['id'];same(json.loads(a['calls'][0]['stdout']),json.loads(b['calls'][0]['stdout']))
assert parity_count==15667
result={'passed':True,'exact_physical_parity_comparisons':parity_count,'e4_file_hashes':len(e4['files']),'original_source_hashes':len(receipts),'durable_source_hashes':len(retention['members']),'archive_members_verified':len(index['files']),'analytical_points_both_backends':analytic_points,'solved_creep_rate_components_both_backends':rate_points,'backends':checks,'independent_rk4_comparisons':rkcomparisons}
(OUT/'CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='independent_rk4_comparisons'}))
