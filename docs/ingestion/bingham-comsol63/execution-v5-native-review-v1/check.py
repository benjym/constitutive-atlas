"""Saved native data, exact source/artifact and independent scalar/RK4 checks only."""
from pathlib import Path
import hashlib,json,math,sys,datetime,zipfile
R=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;P=OUT.parent/'execution-v5';A=R/'docs/investigations/physical-time-v2-profile-v1/actual-native-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H=lambda b:hashlib.sha256(b).hexdigest()
for n,h in {'native-attempt1.json':'95ca533e8c41f17440eebcadca4510a97a2a2ff19b3a53eb20bd89c246d49e6a','native-attempt1-report.json':'51d368278958e86244adb2ec075186cd0652d1eb4de83ef55a4a7404c97c118f','actual-post-native-attempt1.json':'8a0078faa983b7ba5c3757cd41cb758730a02e8af5ce142f019653473e7ad555'}.items():assert sha(P/n)==h,n
pre=json.loads((P/'actual-pre-native-attempt1.json').read_text());assert len(pre['files'])==237
for n,h in pre['files'].items():assert sha(Path(n))==h,n
art=json.loads((P/'native-build-artifacts-v1.json').read_text());assert len(art['files'])==15
for n,h in art['files'].items():assert sha(R/n)==h,n
supp=json.loads((P/'native-linked-build-provenance-v1.json').read_text());assert len(supp['files'])==37 and supp['completed_case_rows_at_capture']==28
for n,v in supp['files'].items():assert sha(R/n)==v['sha256'],n
post=json.loads((P/'actual-post-native-attempt1.json').read_text());assert post['passed'] and post['errors']==[]
for n,v in post['inventories'].items():assert sha(P/n)==v['sha256'],n
for n,h in post['outputs'].items():assert sha(P/n)==h,n
status=json.loads((P/'native-attempt1-status.json').read_text());assert status['returncode']==0 and status['preflight_sha256']==sha(P/'actual-pre-native-attempt1.json');assert status['log_sha256']==sha(P/'native-attempt1.log')
assert pre['utc']<status['start']<supp['utc']<status['end']<post['utc']
assert sha(Path(pre['binary']['path']))==pre['binary']['sha256']==post['binary']['sha256']=='18ed54a1cd4a6a6035895a673bf7506bc28695f38c71217eeba1a5ef2985100d'
for n in ['bingham-configure','bingham-build','bingham-describe']:
 b=json.loads((A/(n+'.json')).read_text());assert b['preverified'] and b['postverified'] and b['returncode']==0;assert sha(A/(n+'.log'))==b['log_sha256']
 if n=='bingham-build':assert b['argv'][-4:]==['--target','atlas_bingham_solver','--parallel','1']
# Header proof reconstructed from actual dependency, independently of helper summary.
dep=next(R/n for n in art['files'] if n.endswith('.o.d'));headers={str(Path(x).resolve()) for x in dep.read_text().replace('\\\n',' ').split() if x.endswith('/atlas/schedule.hpp')};assert headers=={str(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp')}
assert sha(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp')=='fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702'
flags=(R/'build-bingham-native/CMakeFiles/atlas_bingham_solver.dir/flags.make').read_text();assert flags.index('runtimes/physical-time-v2/include')<flags.index('cpp/include') and '-ffp-contract=off' in flags
assert json.loads((A/'bingham-describe.log').read_text())==json.loads((R/'build-bingham-native/generated/models.json').read_text())==json.loads((P/'expected-catalogue.json').read_text())
index=json.loads((P/'frozen-source-archive-v1/INDEX.json').read_text());assert sha(R/index['archive']['path'])==index['archive']['sha256']=='e092bad2e673d52addda6a98ebfdfb2e3f649c5c5f85b636efa7f54814c91e6e'
with zipfile.ZipFile(R/index['archive']['path']) as z:
 assert set(z.namelist())==set(index['files'])
 for n,v in index['files'].items():assert H(z.read(n))==v['sha256'] and len(z.read(n))==v['size'] and sha(R/n)==v['sha256'],n
sys.path.insert(0,str(P));import study,oracle
cases=json.loads((P/'cases.json').read_text())['cases'];rows=json.loads((P/'native-attempt1.json').read_text());assessment=study.assess(cases,rows);assert assessment==json.loads((P/'native-attempt1-report.json').read_text());assert assessment['numeric_comparisons']==7771
(OUT/'reproduced-assessment.json').write_text(json.dumps(assessment,indent=2)+'\n')
# Distinct analytic radial propagation, using events and source stress balance.
def radial(z,d,T,Y=1e5,G=1e7,eta=2e7):
 a=3*G/eta;b=2*G*d;alpha=0.;left=T
 for _ in range(8):
  if left<=1e-15:return z,alpha
  sign=1 if z>=0 else -1
  if abs(z)>Y or (abs(z)==Y and sign*b>0):
   steady=sign*Y+b/a;h=left
   if sign*b<0:
    hit=-math.log((sign*Y-steady)/(z-steady))/a
    if 0<hit<h:h=hit
   end=steady+(z-steady)*math.exp(-a*h);alpha+=sign*(b*h-(end-z))/(3*G);z=sign*Y if h<left else end;left-=h
  elif b:
   target=math.copysign(Y,b);h=(target-z)/b
   if h>=left:return z+b*left,alpha
   z=target;left-=h
  else:return z,alpha
 raise AssertionError('event count')
referr=[0.,0.]
for c in cases[:108]:
 ch=int(c['id'].split('-')[2]);z0=float(c['id'].split('-z')[1].split('-d')[0]);d=float(c['id'].split('-d')[1]);spec=c['specification'];T=spec['segments'][0]['duration'];zend,alpha=radial(z0,d,T)
 N=[0.]*6
 if ch<3:N[:3]=[-1/3]*3;N[ch]=2/3
 else:N[ch]=math.sqrt(2/3)
 initial=spec['initial'];eps=[x+T*N[j]*d for j,x in enumerate(initial[:6])];vp=[eps[j]-N[j]*zend/(2e7) for j in range(6)];expected=eps+vp+[alpha];ref=c['references'][-1]
 es=max(abs(x-y) for x,y in zip(expected,ref['state']));ep=max(abs(N[j]*zend-ref['stress'][j]) for j in range(6));assert es<1e-12 and ep<1e-7,(c['id'],es,ep);referr=[max(referr[0],es),max(referr[1],ep)]
# Rerun only independent source-space RK4 references; never a production engine.
rk=[]
for name in ['public-rate','noncoaxial-history']:
 c=next(c for c in cases if c['id']==name);spec=c['specification'];segments=[(s['duration']/s['samples'],[v.get('value',0) for v in s['controls']]) for s in spec['segments'] for _ in range(s['samples'])];lo=oracle.stress_space_history(spec['initial'],segments,steps=8192);hi=oracle.stress_space_history(spec['initial'],segments,steps=16384)
 es=max(abs(x-y) for u,v in zip(lo,hi) for x,y in zip(u['state'],v['state']));ep=max(abs(x-y) for u,v in zip(lo,hi) for x,y in zip(u['stress'],v['stress']));assert es<1e-12 and ep<1e-5
 for got,ref in zip(hi,c['references'][1:]):assert max(abs(x-y) for x,y in zip(got['state'],ref['state']))<1e-12 and max(abs(x-y) for x,y in zip(got['stress'],ref['stress']))<1e-5
 rk.append({'id':name,'state_grid_difference':es,'stress_grid_difference':ep})
special={}
for name in ['radial-channel-3-z100000-d-0.012','radial-channel-4-z100000-d-0.012','radial-channel-5-z100000-d-0.012','refinement-coarse','refinement-fine','actual-state-restart','late-budget-rollback']:
 row=next(r for r in rows if r['id']==name);v=json.loads(row['calls'][0]['stdout']);special[name]={'ok':v['ok'],'points':len(v['points']),'last_alpha':v['points'][-1]['state'][12],'last_time':v['points'][-1]['time'],'errors':assessment['errors'].get(name)}
result={'decision':'accepted actual native v5 bounded study','cases':136,'calls':272,'numeric_comparisons':7771,'pre_pins':237,'pre_artifact_pins':15,'during_collection_supplement_pins':37,'source_archive_files':len(index['files']),'independent_radial_reference_max_state_error':referr[0],'independent_radial_reference_max_stress_error':referr[1],'independent_RK4_rechecks':rk,'special_cases':special,'compiled_calls_by_reviewer':0,'material_calls_by_reviewer':0}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
