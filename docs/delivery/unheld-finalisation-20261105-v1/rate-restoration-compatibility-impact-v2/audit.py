"""Read source/JSON only, propose exact additive historical archive and binding data."""
from pathlib import Path
import hashlib,json,re,copy
P=Path(__file__).resolve().parent
W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
S=P.parent/'current17-runtime-source-v1/source'
B=P.parent/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp'
BASE='docs/ingestion/manzari-dafalias-1997/delivery-v1/'
OLD='05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218';NEW='3278b22140ca2057a9a2e415654f5213b8183f398df79a7f5c56628756e8dc99';SOLVER='cpp/include/atlas/solver.hpp'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def pin(p):return dict(path=str(p),sha256=sha(p.read_bytes()),bytes=p.stat().st_size)
def write(n,d):q=P/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(d,indent=2)+'\n')
def source(n):
 if n==SOLVER:return B.read_bytes()
 p=S/n
 return (p if p.is_file() else W/n).read_bytes()
assert sha((S/SOLVER).read_bytes())==OLD and sha(B.read_bytes())==NEW
original_bindings={};proposed={};checks=[]
for category,relative in [('direct',BASE+'direct-profile-compatibility-implementation-v1/bindings.json'),('baseline',BASE+'upstream-interface-compatibility-v1/bindings.json')]:
 d=read(W/relative);original_bindings[category]={'pin':pin(W/relative),'value':d}
 for key,row in d.items():
  changed=[n for n,h in row['source_files'].items() if sha(source(n))!=h]
  active=category=='baseline' or key!='interface2016'
  if active:assert changed==[SOLVER],(category,key,changed)
  updated=copy.deepcopy(row['source_files']);updated[SOLVER]=NEW
  proposed[category+'/'+key]={'predecessor_bindings':relative,'predecessor_row_sha256':sha(json.dumps(row,sort_keys=True,separators=(',',':')).encode()),'old_row_exact':row,'prospective_source_files':updated,'changed_paths':changed,'selected_by_current_builder':active,'old_engine_files_qualification_review_and_gates_preserved':True,'accepted_successor_source_review':None,'operational_current_guard_compatible':False}
  checks.append(category+'/'+key+' only exact solver changes')
write('observed-bindings.json',original_bindings)
write('prospective-bindings.json',{'identity':'rate-restoration-special-profile-bindings-proposal-v1','status':'requires separate exact source-equivalence and implementation review; not current-guard executable','rows':proposed})
# Only new canonical byte proposal: immutable640 solver snapshot. Existing702
# intrinsic alias stays byteexact; no global sidecar entry is invented without a consumer.
archive='catalogue/source-snapshots/'+OLD+'/'+SOLVER;out=P/'proposed'/archive;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((S/SOLVER).read_bytes());assert not (W/archive).exists()
write('source-delta.json',{'files':[{'path':archive,'preimage_sha256':None,'sha256':OLD,'bytes':out.stat().st_size,'proposal':'proposed/'+archive}]})
# Controlled-time proof is a prospective successor, never overwrite accepted proof.
ctname=BASE+'direct-controlled-time-compatibility-v1/proof.json';ct=read(W/ctname);newct=copy.deepcopy(ct)
assert ct['changed']==[{'path':SOLVER,'qualified':'b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e','current':OLD}]
assert SOLVER not in ct['compile_dependency_files'] and ct['solver_reachable'] is False
newct['changed'][0]['current']=NEW
for row in newct['source_inventory']:
 if row['path']==SOLVER:assert row['current']==OLD;row['current']=NEW
write('prospective-controlled-time-proof.json',newct)
write('controlled-time-proof-delta.json',{'predecessor':pin(W/ctname),'successor':pin(P/'prospective-controlled-time-proof.json'),'only_semantic_changes':['changed[0].current','source_inventory[solver].current'],'operational_current_guard_compatible':False,'required':'New exact proof SHA and independently accepted implementation/review. Old proof/review constants remain historical; do not repin them.'})
# Actual quoted include graphs from retained generated sources. No generation.
def closure(start,generated):
 queue=[start];seen={};edges=[]
 while queue:
  p=queue.pop().resolve();label=str(p)
  if label in seen:continue
  if p.is_relative_to(S.resolve()):data=source(p.relative_to(S.resolve()).as_posix())
  else:data=p.read_bytes()
  seen[label]=sha(data)
  for target in re.findall(rb'^\s*#\s*include\s*"([^"]+)"',data,re.M):
   name=target.decode();candidates=[p.parent/name,generated/name,S/'cpp/include'/name,S/'cpp/scalar-functions'/name]
   found=next((q for q in candidates if q.is_file()),None);assert found is not None,(p,name)
   edges.append([label,str(found.resolve())]);queue.append(found)
 return {'files':seen,'edges':edges,'solver_reachable':str((S/SOLVER).resolve()) in seen}
closures={}
for key,path in [('norsand','web/engines/current17-compatible/norsand'),('interface2016','web/engines/current17-baseline-compatible/interface2016'),('maxwell','web/engines/current17-compatible/maxwell'),('controlled-time','web/engines/controlled-time')]:
 g=W/path/'generated';start=S/'cpp/main.cpp' if key=='maxwell' else g/('controlled_time_api.cpp' if key=='controlled-time' else 'path_api.cpp')
 closures[key]=closure(start,g)
 assert closures[key]['solver_reachable']==(key=='maxwell')
 checks.append(key+' actual quoted include graph')
write('include-closures.json',closures)
# Known historical approval alias is already covered. Do not mutate its maps.
history=[]
for name in ['catalogue/source-archive-map.json','catalogue/agent-reviews/source-archive-map.json']:
 d=read(W/name)
 for e in d['entries']:
  if e['original_path']==SOLVER:
   q=W/e['archived_path'];assert sha(q.read_bytes())==e['sha256'];history.append({'map':name,'map_pin':pin(W/name),'entry':e,'archive_exact':True})
assert any(r['entry']['sha256']=='b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e' for r in history)
write('historical-aliases.json',history)
write('checks.json',{'passed':True,'checks':checks,'count':len(checks),'compiled_or_generation_calls':0,'maps_or_shared_source_changed':False})
print(json.dumps({'passed':True,'checks':len(checks),'proposed_canonical_paths':1,'live_guard_families_blocked':4}))
