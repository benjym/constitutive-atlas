"""One-time coordinator-authorized archival installation; source files untouched."""
import hashlib,json,subprocess,sys,tarfile
from pathlib import Path
C=Path(__file__).resolve().parent;B=C.parent/'compact-audit-v1';R=C.parents[3];W=Path('/Users/bmar5496/code/constitutive-atlas');sha=lambda b:hashlib.sha256(b).hexdigest()
def enc(n):return(json.dumps(n,indent=2)+'\n').encode()
def readtar(path):
 with tarfile.open(path,'r:gz')as t:return{m.name:t.extractfile(m).read()for m in t.getmembers()}
def main():
 assert not(C/'receipt.json').exists(),'Create-only installation'
 subprocess.run([sys.executable,'-B',str(B/'audit.py')],check=True)
 p=json.loads((B/'plan.json').read_text());payload=readtar(B/'preservation-plan.tar.gz');own=readtar(B/'preproposal-own-context.tar.gz');remote=p['remote'];copies={};maps={};snapshots={};retained={}
 before_sources={path:sha((R/path).read_bytes())for path in p['source_predecessors']}
 def remote_bytes(path):return subprocess.check_output(['git','-C',str(W),'show',remote+':'+path],stderr=subprocess.DEVNULL)
 def unchanged_doc(path,h):
  target=R/path
  if target.exists():assert sha(target.read_bytes())==h,('changed original document',path);retained[path]=h;return
  options=[own.get('isolated/'+path),own.get('model-workspace/'+path)]
  data=next((x for x in options if x is not None and sha(x)==h),None)
  if data is None:data=remote_bytes(path)
  assert sha(data)==h,('missing exact prerequisite',path);copies[path]=data
 for path,h in p['own_receipt_copy_prerequisites'].items():unchanged_doc(path,h)
 for path,node in p['map_proposals'].items():
  target=R/path;prior=sha(target.read_bytes())if target.exists()else None
  assert prior in(node['isolated_sha256'],node['remote_sha256']),('unexpected map predecessor',path,prior)
  data=payload['proposed-sidecars/'+path];assert sha(data)==node['proposed_sha256'];maps[path]=data;m=json.loads(data)
  for doc,h in m['documents'].items():unchanged_doc(doc,h)
  # Union maps retain all their old archive dependencies, including newly committed ones.
  for e in m['entries']:
   archive=e['archived_path'];assert archive=='catalogue/source-snapshots/'+e['sha256']+'/'+e['original_path']
   target=R/archive
   if target.exists():assert sha(target.read_bytes())==e['sha256'];continue
   data=payload.get('prior-bytes/'+archive)
   if data is None:data=remote_bytes(archive)
   assert sha(data)==e['sha256'],archive;snapshots[archive]=data
 for e in p['canonical_archives']:
  name=e['archived_path'];data=payload['prior-bytes/'+name];assert sha(data)==e['sha256']
  if(R/name).exists():assert(R/name).read_bytes()==data
  else:snapshots[name]=data
 for row in p['required_edges']:unchanged_doc(row['document'],row['document_sha256'])
 # All preconditions were checked before writes; canonical bytes precede map changes.
 for path,data in snapshots.items():
  target=R/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for path,data in copies.items():
  target=R/path;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(data)
 map_changes={}
 for path,data in maps.items():
  target=R/path;old=target.read_bytes()if target.exists()else None
  if old==data:continue
  map_changes[path]={'prior_sha256':sha(old)if old is not None else None,'installed_sha256':sha(data)};target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 assert before_sources=={path:sha((R/path).read_bytes())for path in before_sources},'Shared source changed'
 sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
 checks=[]
 for row in p['required_edges']:checks.append({'document':row['document'],'original_path':row['original_path'],'sha256':row['sha256'],'resolved_path':str(checked_receipt(R,row['document'],row['original_path'],row['sha256']).relative_to(R))})
 result={'identity':'kelvin-origin-ec47-archival-installation-v1','plan_sha256':sha((B/'plan.json').read_bytes()),'audit_manifest_sha256':sha((B/'manifest.json').read_bytes()),'remote':remote,'source_files_unchanged':before_sources,'map_changes':map_changes,'files':{path:sha(data)for path,data in snapshots.items()}|{path:sha(data)for path,data in copies.items()}|{path:sha(data)for path,data in maps.items()},'installed_canonical_snapshots':sorted(snapshots),'copied_original_documents':{path:sha(data)for path,data in copies.items()},'retained_original_documents':retained,'verified_required_edges':checks,'passed':True}
 (C/'receipt.json').write_bytes(enc(result));print('Installed',len(snapshots),'new canonical snapshots;',len(copies),'missing original JSONs;',len(map_changes),'changed maps;',len(checks),'replayed edges')
if __name__=='__main__':main()
