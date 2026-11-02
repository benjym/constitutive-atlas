"""Independent E5 saved-evidence checks. Never builds, imports a module or calls an engine."""
import hashlib,importlib.util,json,math,pathlib,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[4];B=ROOT/'docs/ingestion/bingham-comsol63';OUT=pathlib.Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
receipt=read(B/'execution-v1/build-receipt.json');assert len(receipt['evidence'])==53
pins=[]
for role,v in receipt['evidence'].items():
 p=ROOT/v['path'];assert p.is_file() and h(p)==v['sha256'],(role,p);pins.append({'role':role,**v})
private=read(B/'source-v1/source-receipts.json')['receipts'];assert all(h(pathlib.Path(v['private_path']))==v['sha256'] for v in private)
archives=[]
for folder,name in [('asset-provision-v1','qualified-assets.zip'),('execution-v5/frozen-source-archive-v1','source.zip')]:
 index=read(B/folder/'INDEX.json');assert h(B/folder/name)==index['archive']['sha256']
 with zipfile.ZipFile(B/folder/name) as z:
  assert len(z.namelist())==len(set(z.namelist()))==len(index['files'])
  for member,v in index['files'].items():
   expected=v if isinstance(v,str) else v['sha256'];assert hashlib.sha256(z.read(member)).hexdigest()==expected
  archives.append({'path':folder+'/'+name,'members':len(z.namelist())})
# A separately implemented exact event solution for radial stress y, using source
# tensor reduction. Unlike build_packet.py this obtains direction by projection
# from each recorded initial strain/rate and uses equilibrium/crossing logic.
def advance(y,b,T,G,Y,eta):
 k=3*G/eta;t=0.;a=0.;events=0
 while t<T:
  remaining=T-t;active=abs(y)>Y or (abs(y)==Y and y*b>0)
  if not active:
   hit=(math.copysign(Y,b)-y)/b if b else math.inf
   dt=min(remaining,hit if hit>1e-14 else remaining)
   y+=b*dt;t+=dt
   if dt<remaining:y=math.copysign(Y,b)
  else:
   sign=math.copysign(1,y);eq=sign*Y+b/k
   ratio=(sign*Y-eq)/(y-eq) if y!=eq else -1
   hit=-math.log(ratio)/k if 0<ratio<1 else math.inf
   dt=min(remaining,hit);old=y;y=eq+(y-eq)*math.exp(-k*dt)
   a+=sign*(b*dt-(y-old))/(3*G);t+=dt
   if dt<remaining:y=sign*Y
  events+=1;assert events<8
 return y,a
refs=read(B/'source-v1/analytical-references.json')['cases'];rows={x['id']:x for x in read(B/'execution-v5/native-attempt1.json')};worstref=0.;worstactual=0.;worststress=0.
for c in refs:
 G=c['parameters']['G'];Y=c['parameters']['sigma_y'];eta=c['parameters']['eta'];e=c['initial'][:6];d=c['strain_rate']
 v=e if sum(x*x for x in e)>0 else d
 if not any(v):N=[2/3,-1/3,-1/3,0,0,0]
 else:
  factor=math.sqrt((2/3)/sum(x*x for x in v));N=[x*factor for x in v]
 dot=lambda x,y:math.fsum(a*b for a,b in zip(x,y));y0=2*G*dot(e,N)/(2/3);b=2*G*dot(d,N)/(2/3)
 if abs(abs(y0)-Y)<1e-8:y0=math.copysign(Y,y0) # eliminate projection roundoff at exact yield
 y,a=advance(y0,b,c['duration'],G,Y,eta)
 eps=[x+c['duration']*v for x,v in zip(e,d)];state=eps+[eps[i]-y*N[i]/(2*G) for i in range(6)]+[a];sig=[y*x for x in N]
 worstref=max(worstref,max(abs(x-v) for x,v in zip(state,c['expected'])))
 assert all(abs(x-v)<2e-14 for x,v in zip(state,c['expected'])),c['id']
 assert all(abs(x-v)<2e-7 for x,v in zip(sig,c['expected_stress'])),c['id']
 actual=readout=json.loads(rows['radial-'+c['id']]['calls'][0]['stdout'])['points'][-1]
 for x,v in zip(actual['state'],state):assert abs(x-v)<=max(3e-7,2e-5*abs(v))
 for x,v in zip(actual['observables'],sig):assert abs(x-v)<=max(3,2e-5*abs(v))
 worstactual=max(worstactual,max(abs(x-v) for x,v in zip(actual['state'],state)));worststress=max(worststress,max(abs(x-v) for x,v in zip(actual['observables'],sig)))
# Pure saved-result assessor and parity re-execution, never collect().
sys.path.insert(0,str(B/'execution-v5'))
import study,parity
cases=read(B/'execution-v5/cases.json')['cases'];reports={}
for backend in ['native','wasm']:
 report=study.assess(cases,read(B/f'execution-v5/{backend}-attempt1.json'))
 assert report==read(B/f'execution-v5/{backend}-attempt1-report.json');reports[backend]={k:report[k] for k in ['passed','cases','raw_calls','numeric_comparisons']}
parity_result=parity.main(B/'execution-v5/native-attempt1.json',B/'execution-v5/wasm-attempt1.json')
assert parity_result==read(B/'execution-v5/native-wasm-parity-v1.json')
actual_root=pathlib.Path('/private/tmp/atlas-time-profile-v2');build_count=0;dependencies=[]
for backend in ['native','wasm']:
 for label in ['build-artifacts-v1','linked-build-provenance-v1']:
  inv=read(B/f'execution-v5/{backend}-{label}.json')
  for relative,v in inv['files'].items():
   expected=v if isinstance(v,str) else v['sha256'];assert h(actual_root/relative)==expected;build_count+=1
   if relative.endswith('main.cpp.o.d'):
    dep=(actual_root/relative).read_text().replace('\\\n',' ')
    assert '/runtimes/physical-time-v2/include/atlas/schedule.hpp' in dep
    assert '/cpp/include/atlas/schedule.hpp' not in dep;dependencies.append(relative)
assert len(dependencies)==2
from atlas.model import load
load(ROOT/receipt['evidence']['definition']['path'])
depbase=B/'current-engine-equivalence-v1';depindex=read(depbase/'qualified-packaging-v1/INDEX.json')
assert h(ROOT/depindex['archive'])==depindex['archive_sha256']
with zipfile.ZipFile(ROOT/depindex['archive']) as archive:
 assert set(archive.namelist())==set(depindex['files'])
 for member,pin in depindex['files'].items():assert hashlib.sha256(archive.read(member)).hexdigest()==pin
source_deltas={}
for engine,filename in [('maxwell','maxwell-prior-source.json'),('norsand','norsand-prior-source.json')]:
 prior=read(depbase/filename);prior=prior.get('files',prior)
 delta={name:{'old':pin,'current':h(ROOT/name)} for name,pin in prior.items() if h(ROOT/name)!=pin}
 assert set(delta)=={'atlas/measurement_units.py'}
 assert delta['atlas/measurement_units.py']=={'old':'00e8b82bd4ef8f6815b82854855096107114c528871e0b081499f580925e5f12','current':'9e3dd3c586c46206a783a972f29b8ae2d959865ef7d14a5dfab45a9e6e18a132'}
 source_deltas[engine]={'members':len(prior),'delta':delta}
result={'dependency_source_deltas':source_deltas,'dependency_archive_members':len(depindex['files']),'saved_parity':parity_result,'actual_build_members_rechecked':build_count,'main_dependency_files':dependencies,'passed':True,'private_receipts_verified':len(private),'qualified_role_pins':pins,'archives':archives,'independent_radial_cases':len(refs),'radial_reference_max_state_difference':worstref,'radial_actual_max_state_error':worstactual,'radial_actual_max_stress_error_Pa':worststress,'saved_assessments':reports,'limitations':'Saved-result analysis only; no new engine execution. Exact finite study only.'}
(OUT/'CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='qualified_role_pins'},indent=2))
