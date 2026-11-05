"""Optional exact-source equivalence route; original qualification bytes stay historical."""
import hashlib,json,math
from pathlib import Path
BASE='docs/ingestion/manzari-dafalias-1997/delivery-v1/'
BINDINGS=BASE+'direct-profile-compatibility-implementation-v1/bindings.json'
DECISION=BASE+'direct-profile-compatibility-implementation-review-v1/decision.json'
SOURCE_DECISION=BASE+'direct-profile-compatibility-review-v1/decision.json'
SOURCE_DECISION_SHA='f14c5480632bb11a8ae67e558e8bc7abe3382832b50bb6aa11a9e12d895401fd'
PROOF=BASE+'direct-profile-compatibility-v1/manifest.json'
TOOLS=('tools/profile_source_compatibility.py','tools/build_controlled_path_web.py','tools/build_maxwell_laboratory.py','tools/build_interface2016_web.py')
PROOF_SHA='e156545f0e04bf9f9e29fa93afd99086444e2e94d53e7d9186952a5f686f6abf'
def digest(data):return hashlib.sha256(data).hexdigest()
def require(value,message):
 if not value:raise ValueError(message)
def load(data):
 def pairs(rows):
  d={}
  for k,v in rows:
   require(k not in d,'Duplicate compatibility JSON key');d[k]=v
  return d
 def bad(value):raise ValueError('Non-finite compatibility JSON')
 return json.loads(data,object_pairs_hook=pairs,parse_constant=bad)
def regular(root,name):
 p=Path(name);require(not p.is_absolute() and '..' not in p.parts,'Unsafe compatibility path')
 f=root/p;require(not f.is_symlink() and f.is_file() and f.resolve().is_relative_to(root.resolve()),'Missing/unsafe compatibility file '+name)
 from tools.rate_restoration_source_view_v2 import historical_bytes
 return historical_bytes(root,name,f.read_bytes())
def namespace(root):
 names=set()
 for directory,suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp'}),('schemas',{'.json'})]:
  for p in (root/directory).rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and (p.suffix in suffixes or directory=='cpp' and p.is_relative_to(root/'cpp/scalar-functions')):names.add(p.relative_to(root).as_posix())
 return names

def validate(root,build,profile):
 root,build=Path(root),Path(build)
 if not (build/'source-compatibility.json').exists():return None
 raw=regular(build,'source-compatibility.json');row=load(raw)
 bindings_raw=regular(root,BINDINGS);bindings=load(bindings_raw)
 require(set(bindings)=={'norsand','maxwell','interface2016'} and profile in bindings and row==bindings[profile],'Exact staged compatibility binding differs')
 require(digest(regular(root,SOURCE_DECISION))==SOURCE_DECISION_SHA,'Genuine independent source-equivalence review changed')
 decision_raw=regular(root,DECISION);decision=load(decision_raw)
 require(set(decision)=={'identity','accepted','proof_manifest_sha256','bindings_sha256','implementation','reviewer_run'},'Closed compatibility decision schema required')
 require(decision['identity']=='current17-direct-profile-compatibility-implementation-review-v1' and decision['accepted'] is True,'Independent compatibility acceptance required')
 require(isinstance(decision['reviewer_run'],str) and decision['reviewer_run'].strip() and decision['reviewer_run']!='/root/md1997_final_review','Separate reviewer identity required')
 require(decision['proof_manifest_sha256']==PROOF_SHA==digest(regular(root,PROOF))==row['proof_manifest_sha256'],'Source proof changed')
 require(decision['bindings_sha256']==digest(bindings_raw),'Accepted compatibility binding changed')
 require(isinstance(decision['implementation'],dict) and set(decision['implementation'])==set(TOOLS),'Exact packaging implementation approval required')
 for n,h in decision['implementation'].items():require(digest(regular(root,n))==h,'Packaging compatibility implementation changed '+n)
 sources=row['source_files'];require(namespace(root)=={n for n in sources if n.startswith(('atlas/','cpp/','schemas/'))},'Complete compatibility source namespace changed')
 for n,h in sources.items():require(digest(regular(root,n))==h,'Compatibility source changed '+n)
 found={p.relative_to(build).as_posix() for p in build.rglob('*') if p.is_file()}
 require(found==set(row['files'])|{'source-compatibility.json'},'Exact retained engine membership changed')
 for n,h in row['files'].items():require(digest(regular(build,n))==h,'Retained engine/evidence changed '+n)
 qraw=regular(build,row['qualification']);rraw=regular(build,row['review']);q=load(qraw);review=load(rraw)
 require(row['identity']=='current17-dedicated-profile-compatibility-v1' and row['profile']==profile and q['model']==row['model'],'Compatibility profile/model differs')
 require(q['status']=='passed' and review['status']=='accepted' and q['binding']==review['binding']==row['old_binding'] and q['gates']==row['gates']==review['gates'],'Original accepted qualification/binding/gates changed')
 require(isinstance(q.get('implementation_run'),str) and q['implementation_run'].strip() and isinstance(review.get('reviewer_run'),str) and review['reviewer_run'].strip() and q['implementation_run']!=review['reviewer_run'],'Original independent review missing')
 pin=q['independent_review'];require(pin['path']==row['review'] and pin['sha256']==digest(rraw),'Original review pin differs')
 for n,h in row.get('retained_repository_evidence',{}).items():require(digest(regular(root,n))==h,'Original interface command/result evidence changed '+n)
 return dict(qualification=q,qualification_bytes=qraw,review_bytes=rraw,sources=sources,compatibility_bytes=raw,decision_bytes=decision_raw)

def copy_evidence(checked,engine):
 if checked is not None:
  (engine/'source-compatibility.json').write_bytes(checked['compatibility_bytes'])
  (engine/'source-compatibility-review.json').write_bytes(checked['decision_bytes'])
