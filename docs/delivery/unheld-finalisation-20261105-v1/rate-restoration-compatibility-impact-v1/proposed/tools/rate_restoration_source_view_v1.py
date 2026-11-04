"""Exact reviewed historical view for retained special-profile packaging only.

The actual current source and implementation are checked independently before
returning an immutable predecessor byte view to an unchanged historical guard.
No qualification receipt, old decision or source map is rewritten.
"""
from pathlib import Path
import hashlib,json
PACKET='docs/delivery/unheld-finalisation-20261105-v1/rate-restoration-compatibility-impact-v1/'
PROOF=PACKET+'proof.json'
REVIEW='docs/delivery/unheld-finalisation-20261105-v1/rate-restoration-compatibility-impact-review-v1/decision.json'
SOURCE='cpp/include/atlas/solver.hpp'
OLD='05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218'
NEW='0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc'
IMPLEMENTATION={'tools/rate_restoration_source_view_v1.py','tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py','tools/build_controlled_time_web.py'}
def digest(b):return hashlib.sha256(b).hexdigest()
def require(value,message):
 if not value:raise ValueError(message)
def load(raw):
 def pairs(rows):
  result={}
  for key,value in rows:
   require(key not in result,'Duplicate source-view JSON key');result[key]=value
  return result
 def bad(value):raise ValueError('Nonfinite source-view JSON')
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
def regular(root,name):
 name=Path(name);require(name.parts and not name.is_absolute() and '..' not in name.parts,'Unsafe source-view path')
 p=root
 for part in name.parts:
  p=p/part;require(not p.is_symlink(),'Symlink source-view path')
 require(p.is_file() and p.resolve().is_relative_to(root.resolve()),'Missing source-view file '+str(name))
 return p.read_bytes()
def authority(root):
 root=Path(root);raw=regular(root,PROOF);proof=load(raw);review=load(regular(root,REVIEW))
 require(set(review)=={'identity','decision','author_run','reviewer_run','unresolved_blockers','proof_sha256','implementation'},'Closed source-view review schema')
 require(review['identity']=='rate-restoration-special-profile-source-view-review-v1' and review['decision']=='accepted','Independent source-view acceptance required')
 require(review.get('author_run')=='/root/baseline_migration' and isinstance(review.get('reviewer_run'),str) and review['reviewer_run'].strip() and review['reviewer_run']!=review['author_run'],'Distinct independent source-view reviewer required')
 require(review['unresolved_blockers']==[] and review['proof_sha256']==digest(raw),'Source-view proof changed or blocked')
 require(set(review['implementation'])==IMPLEMENTATION==set(proof['implementation']),'Exact source-view implementation membership')
 for name,h in review['implementation'].items():require(h==proof['implementation'][name]==digest(regular(root,name)),'Source-view implementation changed '+name)
 require(proof['identity']=='rate-restoration-special-profile-source-view-proof-v1' and proof['ordinary_runtime_qualification_transferred'] is False,'Source-view scope changed')
 require(proof['source_delta']=={'path':SOURCE,'predecessor_sha256':OLD,'current_sha256':NEW},'Exact source-view scientific source delta required')
 require(digest(regular(root,SOURCE))==NEW,'Source-view current solver differs')
 expected={SOURCE,*IMPLEMENTATION-{'tools/rate_restoration_source_view_v1.py'}}
 require(set(proof['aliases'])==expected,'Exact historical alias set required')
 for name,row in proof['aliases'].items():
  require(set(row)=={'predecessor_sha256','current_sha256','archive'},'Closed historical alias row')
  require(row['archive']=='catalogue/source-snapshots/'+row['predecessor_sha256']+'/'+name,'Nonintrinsic historical source archive')
  require(digest(regular(root,name))==row['current_sha256'] and digest(regular(root,row['archive']))==row['predecessor_sha256'],'Historical source view bytes changed '+name)
 require(proof['aliases'][SOURCE]['predecessor_sha256']==OLD and proof['aliases'][SOURCE]['current_sha256']==NEW,'Solver alias changed')
 for name,h in proof['ancestors'].items():require(digest(regular(root,name))==h,'Historical compatibility authority changed '+name)
 return proof

def historical_bytes(root,name,current):
 """Never aliases arbitrary bytes: only the exact independently reviewed vector."""
 if name not in IMPLEMENTATION|{SOURCE}:return current
 proof=authority(root)
 if name not in proof['aliases']:return current
 row=proof['aliases'][name];require(digest(current)==row['current_sha256'],'Read source differs from reviewed current bytes')
 return regular(Path(root),row['archive'])
