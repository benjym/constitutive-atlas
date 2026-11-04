from pathlib import Path
import json,hashlib,types,sys
Q=Path(__file__).resolve().parent;P=Q.parent/'direct-profile-release-paths-v1';S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');R=Q.parents[4]
read=lambda p:json.loads(p.read_bytes());h=lambda b:hashlib.sha256(b).hexdigest()
count=0
def ck(x,label):
 global count
 assert x,label
 count+=1
m=read(P/'manifest.json');ck(h((P/'manifest.json').read_bytes())=='ea44623f719b562680cf6a32530c77d34e9b348f357da0d9db6132b6f99001cf','subject')
for n,v in m['files'].items():ck(h((P/n).read_bytes())==v,n)
assets=read(P/'asset-map.json');bindings=read(Q.parent/'direct-profile-compatibility-implementation-v1/bindings.json');total=0;size=0
for label,row in assets.items():
 src=Path(row['source']);dst=S/row['destination'];want=row['files'];bind=bindings[label]
 for directory in [src,dst]:
  ck({p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}==set(want),('membership',label,str(directory)))
  for name,v in want.items():
   b=(directory/name).read_bytes();ck(h(b)==v['sha256'] and len(b)==v['bytes'],('bytes',label,name))
 ck(set(want)==set(bind['files'])|{'source-compatibility.json'},('accepted membership',label))
 for name,v in bind['files'].items():ck(want[name]['sha256']==v,('accepted artifact',label,name))
 ck(read(dst/'source-compatibility.json')==bind,('binding marker',label))
 total+=len(want);size+=sum(v['bytes'] for v in want.values())
ck(total==29 and size==2833685,'totals')
substitutions=[('docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine','web/engines/current17-compatible/norsand'),('docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine','web/engines/current17-compatible/maxwell'),('docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine','web/engines/current17-compatible/interface2016')]
for name in ['tools/build_web.py','.github/workflows/pages.yml']:
 old=(P/'before'/name).read_bytes();new=(P/'proposed'/name).read_bytes();reverse=new
 for before,after in substitutions:
  ck(old.count(before.encode())==1 and new.count(after.encode())==1,('one fixed substitution',name,after));reverse=reverse.replace(after.encode(),before.encode())
 ck(reverse==old,('all other controls unchanged',name));ck((S/name).read_bytes()==new,('candidate exact',name))
# Validate the exact accepted helper against each new repository path with genuine installed decision.
def deny(e,a):
 if e.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError(e)
sys.addaudithook(deny);sys.dont_write_bytecode=True
helper=S/'tools/profile_source_compatibility.py';module=types.ModuleType('independent_release_helper');exec(compile(helper.read_bytes(),str(helper),'exec'),module.__dict__)
decision=read(R/module.DECISION);ck(decision['accepted'] is True,'genuine decision')
for name,digest in decision['implementation'].items():ck(h((S/name).read_bytes())==digest,('accepted implementation',name))
for label,row in assets.items():ck(module.validate(S,S/row['destination'],label) is not None,('genuine helper acceptance',label))
print(json.dumps({'passed':True,'checks':count,'files':total,'bytes':size,'helper_actual_genuine_source_only_positive':3,'compiled_or_model_or_build_calls':0},indent=2))
