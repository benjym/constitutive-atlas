"""Read-only exact current-main metadata composition; no shared checkout staging."""
from pathlib import Path
import subprocess,json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PUB='31ba67e465c1086cdadf29006750f0827e9fc1f5'
OWN='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
BASE='106a9cf8c327c9c262a97eb86aa04dae3f6cadb8'
HEAD='feba9188376939a727fe8e69ba62cc3ca6ae73ca'
INDEX='342d4733f48857ecbab58e12c1e40fe8e1a40a0f22fae718bc89a9d9175b5b23'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def tree(ref):
 out={}
 for row in git('ls-tree','-r','-z',ref).split(b'\0'):
  if row:
   meta,n=row.split(b'\t',1);m,k,o=meta.decode().split();assert k=='blob';out[n.decode()]=(m,o)
 return out
def blob(ref,n):return git('show',ref+':'+n)
def oid(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 assert git('rev-parse','HEAD').decode().strip()==HEAD and sha((ROOT/'.git/index').read_bytes())==INDEX
 pub,own,base=tree(PUB),tree(OWN),tree(BASE)
 desired=dict(own);remote_changes={n:v for n,v in pub.items() if base.get(n)!=v}
 assert len(remote_changes)==100 and set(base)<=set(pub)
 shared={'IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md'}
 entries={};preserved=[];skipped=[]
 def put(n,data,mode,source):
  entries[n]={'path':n,'mode':mode,'sha256':sha(data),'bytes':len(data),**source};desired[n]=(mode,oid(data))
 for n,meta in remote_changes.items():
  if n in shared:
   a,b,c=blob(BASE,n),blob(PUB,n),blob(OWN,n)
   assert b.startswith(a),n
   data=c+b[len(a):];target=HERE/'composed'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   put(n,data,meta[0],{'local_source':str(target.relative_to(ROOT))})
  else:desired[n]=meta
  preserved.append(n)
 # Select only own new retained files. Never replace an existing committed identity.
 packet=ROOT/'docs/ingestion/hypoplastic-interface-2016'
 for f in sorted(packet.rglob('*')):
  if not f.is_file() or f.is_symlink() or HERE in f.parents:continue
  n=str(f.relative_to(ROOT));data=f.read_bytes()
  if n in desired:
   if desired[n][1]!=oid(data):skipped.append(n)
   continue
  put(n,data,'100644',{'local_source':n})
 for name in ['README.md','create_commit.py','prepare_plan.py','DELIVERY-SUPPLEMENT.md']:
  f=HERE/name;put(str(f.relative_to(ROOT)),f.read_bytes(),'100644',{'local_source':str(f.relative_to(ROOT))})
 # All other changes are selected from the qualified committed application, never checkout.
 for n,meta in sorted(desired.items()):
  if pub.get(n)==meta:entries.pop(n,None);continue
  if n not in entries:
   assert own.get(n)==meta,n
   put(n,blob(OWN,n),meta[0],{'git_source':OWN+':'+n})
 assert set(pub)<=set(desired),'No deletion permitted'
 assert all(desired[n]==v for n,v in own.items() if not(n in shared or n.startswith('docs/ingestion/'))),'Application/science/CI changed'
 assert all(desired[n]==pub[n] for n in preserved if n not in shared)
 plan={'published':PUB,'own':OWN,'common_base':BASE,'root_head':HEAD,'root_index_sha256':INDEX,'ref':'refs/heads/delivery/interface2016-release-v4','scope':'Qualified application exact; new owned evidence plus current published metadata only; current CI/live remain pending','entries':[entries[n] for n in sorted(entries)]}
 (HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 proof={'status':'source-only composition prepared','remote_changes':len(remote_changes),'preserved_remote_paths':preserved,'qualified_application_unchanged':True,'new_or_changed_paths':len(entries),'skipped_dirty_existing_evidence':skipped,'plan_sha256':sha((HERE/'plan.json').read_bytes()),'root_head_unchanged':HEAD,'root_index_unchanged':INDEX,'new_parent_revision_requires_CI_upload_live_verification':True}
 (HERE/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
