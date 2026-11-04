from pathlib import Path
import json,hashlib,types,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;P=Q.parent/'direct-profile-compatibility-implementation-v1';V2=Q.parent/'direct-profile-compatibility-implementation-v2';R=Q.parents[4];S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
h=lambda b:hashlib.sha256(b).hexdigest()
count=0
def ck(x,n):
 global count
 assert x,n
 count+=1
manifest=json.loads((P/'manifest.json').read_bytes());ck(h((P/'manifest.json').read_bytes())=='3e98325f1ec53bb61613376a8b38e112bd9123419c6d02350800aa6f435b1669','manifest')
for n,v in manifest['files'].items():ck(h((P/n).read_bytes())==v,n)
v2=json.loads((V2/'manifest.json').read_bytes());ck(h((V2/'manifest.json').read_bytes())=='7424a178747a2ed57a4efca0af398b9d288fbfbe1a6d2205f1300e5342c3f942','v2 manifest')
for n,v in v2['files'].items():ck(h((V2/n).read_bytes())==v,n)
old=(P/'profile_source_compatibility.py').read_bytes();new=(V2/'profile_source_compatibility.py').read_bytes();addition=b" require(digest(regular(root,SOURCE_DECISION))==SOURCE_DECISION_SHA,'Genuine independent source-equivalence review changed')\n"
ck(new.count(addition)==1 and new.replace(addition,b'')==old,'one-line exact delta')
def deny(e,a):
 if e.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError(e)
sys.addaudithook(deny)
m=types.ModuleType('independent_compatibility_fixture');exec(compile((V2/'profile_source_compatibility.py').read_bytes(),str(V2/'profile_source_compatibility.py'),'exec'),m.__dict__)
rawbindings=(P/'bindings.json').read_bytes();bindings=json.loads(rawbindings);pins=json.loads((V2/'implementation-files.json').read_bytes());decision={'identity':'current17-direct-profile-compatibility-implementation-review-v1','accepted':True,'proof_manifest_sha256':m.PROOF_SHA,'bindings_sha256':h(rawbindings),'implementation':pins,'reviewer_run':'manufactured-independent-fixture-NOT-ACTUAL-ACCEPTANCE'}
regular=m.regular;overrides={};source_decision_reads=[]
def observed(root,name):
 if root==S:
  if name==m.SOURCE_DECISION:
   source_decision_reads.append(name)
   if (str(root),name) in overrides:
    value=overrides[(str(root),name)]
    if value is None:raise ValueError('Independent missing genuine source decision fixture')
    return value
   return (R/m.SOURCE_DECISION).read_bytes()
  if name==m.DECISION:return json.dumps(decision).encode()
  if name==m.BINDINGS:return rawbindings
  if name==m.PROOF:return (R/m.PROOF).read_bytes()
 if (str(root),name) in overrides:return overrides[(str(root),name)]
 return regular(root,name)
m.regular=observed
for label,folder in [('norsand','norsand-compatible'),('maxwell','maxwell-compatible'),('interface2016','interface-compatible')]:
 build=Path('/private/tmp/atlas-md1997-direct-app-v1')/folder
 result=m.validate(S,build,label);ck(result is not None,'genuine source acceptance positive')
 for bad in [None,b'{}']:
  overrides[(str(S),m.SOURCE_DECISION)]=bad
  try:m.validate(S,build,label)
  except ValueError:count+=1
  else:raise AssertionError('missing/corrupt source decision admitted')
  overrides.clear()
 for key,value in [('accepted',1),('accepted',1.0),('accepted',False),('identity','old-identity'),('bindings_sha256','0'*64),('proof_manifest_sha256','0'*64),('implementation',{}),('reviewer_run','/root/md1997_final_review')]:
  old=decision[key];decision[key]=value
  try:m.validate(S,build,label)
  except ValueError:count+=1
  else:raise AssertionError((key,value))
  finally:decision[key]=old
 for name in [*pins, next(iter(bindings[label]['source_files']))]:
  overrides[(str(S),name)]=regular(S,name)+b'\n'
  try:m.validate(S,build,label)
  except ValueError:count+=1
  else:raise AssertionError(('modified implementation/source',name))
  overrides.clear()
 for name in bindings[label]['files']:
  overrides[(str(build),name)]=regular(build,name)+b'\n'
  try:m.validate(S,build,label)
  except ValueError:count+=1
  else:raise AssertionError(('modified retained evidence',label,name))
  overrides.clear()
ck(len(source_decision_reads)>0,'live source-decision pin');ck(not (S/m.DECISION).exists(),'no manufactured actual acceptance installed')
print(json.dumps({'checks':count,'passed':True,'source_decision_read_count':len(source_decision_reads),'profiles_rejecting_missing_or_changed_source_acceptance':list(bindings),'manufactured_decisions_only':True,'builders_or_engines_executed':False},indent=2))
