"""Source parsing and manufactured authority injection only, never run engines."""
from pathlib import Path
import json,hashlib,types,sys
P=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');R=P.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def deny(event,args):
 if event.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError('Process/network/native load forbidden')
sys.addaudithook(deny)
for p in [P/'profile_source_compatibility.py',*sorted((P/'proposed').glob('*.py'))]:compile(p.read_text(),str(p),'exec')
m=types.ModuleType('compat_fixture');exec(compile((P/'profile_source_compatibility.py').read_text(),'compat_fixture','exec'),m.__dict__)
original=m.regular
bindings=(P/'bindings.json').read_bytes()
decision={'identity':'current17-direct-profile-compatibility-implementation-review-v1','accepted':True,'proof_manifest_sha256':m.PROOF_SHA,'bindings_sha256':hashlib.sha256(bindings).hexdigest(),'implementation':{n:sha(S/n) for n in m.TOOLS},'reviewer_run':'manufactured-fixture-reviewer-not-an-actual-decision'}
count=0
for profile,directory in [('norsand','norsand-compatible'),('maxwell','maxwell-compatible'),('interface2016','interface-compatible')]:
 def observed(root,name):
  if root==S and name==m.BINDINGS:return bindings
  if root==S and name==m.SOURCE_DECISION:return (R/m.SOURCE_DECISION).read_bytes()
  if root==S and name==m.PROOF:return (R/m.PROOF).read_bytes()
  if root==S and name==m.DECISION:return json.dumps(decision).encode()
  return original(root,name)
 m.regular=observed
 out=m.validate(S,Path('/private/tmp/atlas-md1997-direct-app-v1')/directory,profile);assert out is not None;count+=1
 for key,bad in [('accepted',1),('accepted',1.0),('accepted',False),('bindings_sha256','0'*64),('proof_manifest_sha256','0'*64),('reviewer_run','/root/md1997_final_review'),('implementation',{})]:
  saved=decision[key];decision[key]=bad
  try:m.validate(S,Path('/private/tmp/atlas-md1997-direct-app-v1')/directory,profile)
  except ValueError:count+=1
  else:raise AssertionError((profile,key,bad))
  finally:decision[key]=saved
# Genuine absent decision stays absent: this is the operational fail-closed state.
m.regular=lambda root,name: (bindings if name==m.BINDINGS else (R/m.PROOF).read_bytes() if name==m.PROOF else (R/m.SOURCE_DECISION).read_bytes() if name==m.SOURCE_DECISION else original(root,name))
try:m.validate(S,Path('/private/tmp/atlas-md1997-direct-app-v1/norsand-compatible'),'norsand')
except ValueError:count+=1
else:raise AssertionError('Missing genuine acceptance was admitted')
print(f'PASS {count} source/manufactured checks; no actual accepted review authored; operational route remains blocked')
