"""Verify portable archive; check prospective bindings; install exact additive bytes."""
import gzip,hashlib,importlib.util,json,sys,tarfile,subprocess,functools
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4]
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(name,node):
 p=B/name;assert not p.exists(),str(p);p.write_text(json.dumps(node,indent=2)+'\n')
def load():
 a=json.loads((B/'artifact.json').read_text());m=json.loads((B/'members.json').read_text())
 assert sha((B/a['archive']).read_bytes())==a['archive_sha256'];assert sha((B/'members.json').read_bytes())==a['members_sha256']
 out={}
 with tarfile.open(B/a['archive'],'r:gz')as t:
  for x in t.getmembers():
   assert x.isfile()and not Path(x.name).is_absolute()and '..'not in Path(x.name).parts and x.name not in out
   out[x.name]=t.extractfile(x).read()
 assert set(out)==set(m)
 for p,h in m.items():assert sha(out[p])==h,p
 assert sha(out['plan.json'])==a['plan_sha256'];assert out['plan.json']==(B/'plan.json').read_bytes()
 return a,out,json.loads(out['plan.json'])
def resolve(reader,row):
 doc=row['document'];assert sha(reader(doc))==row['document_sha256'],('document',doc)
 path=row['original_path'];h=row['sha256'];selected=path
 side=str(Path(doc).parent/'source-archive-map.json')
 try:m=json.loads(reader(side))
 except(FileNotFoundError,KeyError):m=None
 if m:
  assert m['version']=='immutable-source-archive-map-0.1';assert m['documents'].get(doc)==row['document_sha256'],('guard',doc)
  found=[e for e in m['entries']if e['original_path']==path and e['sha256']==h];assert len(found)<=1
  if found:selected=found[0]['archived_path'];assert selected=='catalogue/source-snapshots/'+h+'/'+path
 assert sha(reader(selected))==h,('source',doc,path)
 return selected
if __name__=='__main__':
 mode=sys.argv[1]if len(sys.argv)>1 else'check';a,payload,p=load();print('Archive verified',len(payload),'members')
 if mode=='virtual':
  spec=importlib.util.spec_from_file_location('prep',B/'prepare.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
  prep.gitdata=functools.lru_cache(None)(lambda path: subprocess.check_output(['git','-C',str(prep.WORKSPACE),'show',prep.REMOTE+':'+path],stderr=subprocess.DEVNULL))
  inventory=json.loads(gzip.decompress(payload['inventory.json.gz']));checks=[];errors=[]
  for ns,key,base in [('remote','remote_rows',prep.gitdata),('isolated','own_rows',prep.localdata)]:
   def reader(path):
    if 'proposed-sidecars/'+path in payload:return payload['proposed-sidecars/'+path]
    if 'prior-bytes/'+path in payload:return payload['prior-bytes/'+path]
    if path.startswith('catalogue/source-snapshots/')and(R/path).exists():return(R/path).read_bytes()
    if ns=='remote'and path in p['planned_source_predecessors']:return b'prospective changed shared source'
    if path in p['own_mutable_prior_sources']:return(R/path).read_bytes()
    try:return base(path)
    except Exception as exc:
     if isinstance(exc,(FileNotFoundError,KeyError))or getattr(exc,'returncode',None)is not None:raise FileNotFoundError(path)from exc
     raise
   for row in inventory[key]:
    if row['resolution']not in('live','archived'):continue
    try:resolve(reader,row);checks.append([ns,row['document'],row['original_path'],row['sha256']])
    except Exception as exc:errors.append({'row':row,'error':str(exc)})
  result={'identity':'kelvin-origin-v4-prospective-bindings-v1','archive_sha256':a['archive_sha256'],'checked':len(checks),'errors':errors,'passed':not errors};dump('virtual-check-v4.json',result);print('checked',len(checks),'errors',len(errors));assert not errors
 elif mode=='install':
  v=json.loads((B/'virtual-check-v4.json').read_text());assert v['passed']and v['archive_sha256']==a['archive_sha256'];assert not(B/'installation.json').exists()
  # Check every original document and map before any installation mutation.
  for row in p['required_additive_edges']:assert sha((R/row['document']).read_bytes())==row['document_sha256'],row['document']
  for path,node in p['sidecar_proposals'].items():
   target=R/path;actual=sha(target.read_bytes())if target.exists()else None;assert actual==node['isolated_premerge_sha256'],(path,actual,node)
  for path,h in p['current_v4_files'].items():assert sha((R/path).read_bytes())==h,path
  for node in p['canonical_archives']:
   path=node['archived_path'];data=payload['prior-bytes/'+path];assert sha(data)==node['sha256'];target=R/path
   if target.exists():assert target.read_bytes()==data,path
  for node in p['canonical_archives']:
   path=node['archived_path'];target=R/path;target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():target.write_bytes(payload['prior-bytes/'+path])
  for path in p['sidecar_proposals']:
   target=R/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload['proposed-sidecars/'+path])
  sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
  verified=[]
  for row in p['required_additive_edges']:
   selected=checked_receipt(R,row['document'],row['original_path'],row['sha256']);verified.append(dict(row,resolved_after_install=str(selected.relative_to(R))))
  result={'identity':'kelvin-origin-v4-binding-installation-v1','archive_sha256':a['archive_sha256'],'remote_commit':p['remote'],'files':{path:sha((R/path).read_bytes())for path in p['sidecar_proposals']}|{n['archived_path']:n['sha256']for n in p['canonical_archives']}|p['current_v4_files'],'original_documents':{r['document']:r['document_sha256']for r in p['required_additive_edges']},'verified_edges':verified,'passed':True};dump('installation.json',result);print('Installed:',len(p['sidecar_proposals']),'maps;',len(p['canonical_archives']),'snapshots;',len(verified),'bindings')
 elif mode=='actual':
  sys.path.insert(0,str(R));from atlas.evidence import checked_receipt,verify_manifest_files
  for row in p['required_additive_edges']:checked_receipt(R,row['document'],row['original_path'],row['sha256'])
  checked=[]
  for name in ['interface-v1/freeze.json','interface-v2/freeze.json','interface-v3/freeze.json','interface-v4/freeze.json','integration-v1/archive-installation.json','integration-v2/installation.json']:
   path='docs/ingestion/kelvin-voigt-comsol63/'+name;node=json.loads((R/path).read_text())
   if 'files'in node:verify_manifest_files(R,path);checked.append(path)
  dump('actual-check.json',{'passed':True,'required_edges':len(p['required_additive_edges']),'checked_manifests':checked});print('Actual bindings passed')
 elif mode!='check':raise SystemExit('check|virtual|install|actual')
