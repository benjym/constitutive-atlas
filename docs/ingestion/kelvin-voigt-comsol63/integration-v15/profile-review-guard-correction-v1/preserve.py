"""Exact premerge profile-input archival closure; no source changes."""
import hashlib,json,sys,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];D=Path('docs/ingestion/kelvin-voigt-comsol63');W=Path('/Users/bmar5496/code/constitutive-atlas');BASE='8cab145bacde8b0f25cb93c0aebef826e318710f';REMOTE='b31c0a94ea04b7282e0780112940a362e8f9d315';TARGETS={'AGENTS.md'};sha=lambda b:hashlib.sha256(b).hexdigest();enc=lambda n:(json.dumps(n,indent=2)+'\n').encode()
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt

def pairs(n):
 if isinstance(n,dict):
  for path,h in n.items():
   if isinstance(h,str)and len(h)==64 and(path in TARGETS or path.endswith('/source-archive-map.json')):yield path,h
  path=n.get('path')
  if isinstance(path,str)and(path in TARGETS or path.endswith('/source-archive-map.json')):
   for key in['sha256','hash']:
    if isinstance(n.get(key),str)and len(n[key])==64:yield path,n[key]
  for value in n.values():yield from pairs(value)
 elif isinstance(n,list):
  for value in n:yield from pairs(value)
def main():
 assert not(B/'receipt.json').exists();sources={path:(R/path).read_bytes()for path in TARGETS if(R/path).is_file()};before={path:sha(data)for path,data in sources.items()};rows=[];originals={};proposals={};archives={};prior_maps={}
 for file in sorted(R.rglob('*.json')):
  if B in file.parents or 'source-snapshots' in file.parts or 'frozen-sources' in file.parts or file.name=='source-archive-map.json'or any(x in file.parts for x in ['prior','premerge','proposed','base','remote','receipt-bytes','frozen-sources','release-bindings-v1']):continue
  try:node=json.loads(file.read_text())
  except Exception:continue
  for path,h in sorted(set(pairs(node))):
   if '/source-snapshots/'in path or '/planned-sidecars/'in path:continue
   doc=str(file.relative_to(R))
   try:selected=checked_receipt(R,doc,path,h)
   except Exception:
    if path.endswith('/source-archive-map.json')and(R/path).is_file()and sha((R/path).read_bytes())==h:selected=R/path
    else:continue
   if selected==R/path:rows.append({'document':doc,'document_sha256':sha(file.read_bytes()),'original_path':path,'sha256':h})
 # Explicit missing review context: old source exists in canonical archive.
 doc='catalogue/agent-reviews/vw96-agent-v1.json';h='af554aa5c12e4f3706efdf20399a283e7a09bda8be748b1f394b4d0c78c3709e'
 rows.append({'document':doc,'document_sha256':sha((R/doc).read_bytes()),'original_path':'AGENTS.md','sha256':h})
 def snapshot(path,h,data):
  assert sha(data)==h;name='catalogue/source-snapshots/'+h+'/'+path
  if(R/name).exists():assert(R/name).read_bytes()==data
  archives[name]=data;return{'original_path':path,'sha256':h,'archived_path':name}
 for path,bytes_ in sources.items():snapshot(path,sha(bytes_),bytes_)
 # Retain the committed predecessor bytes too, independently of local deltas.
 for path in sorted(TARGETS):
  old=subprocess.run(['git','-C',str(W),'show',BASE+':'+path],capture_output=True)
  if old.returncode==0:snapshot(path,sha(old.stdout),old.stdout)
 required=[row for row in rows if row['original_path']in TARGETS]
 while True:
  names={str(Path(row['document']).parent/'source-archive-map.json')for row in required}
  proposals={}
  for name in sorted(names):
   target=R/name;old=target.read_bytes()if target.exists()else None;prior_maps[name]=old
   m=json.loads(old)if old is not None else{'version':'immutable-source-archive-map-0.1','documents':{str(f.relative_to(R)):sha(f.read_bytes())for f in target.parent.glob('*.json')if f.name!='source-archive-map.json'},'entries':[]}
   for row in required:
    if str(Path(row['document']).parent/'source-archive-map.json')!=name:continue
    m['documents'][row['document']]=row['document_sha256'];path=row['original_path'];expected=row['sha256']
    if path in TARGETS:
     bytes_=sources[path]if sha(sources[path])==expected else(R/'catalogue/source-snapshots'/expected/path).read_bytes();assert sha(bytes_)==expected
    else:bytes_=(R/path).read_bytes()
    entry=snapshot(path,expected,bytes_)
    if entry not in m['entries']:m['entries'].append(entry)
   proposals[name]=enc(m)
  extra=[row for row in rows if row not in required and row['original_path']in proposals and sha(proposals[row['original_path']])!=row['sha256']]
  if not extra:break
  required+=extra
 for row in required:originals[row['document']]=row['document_sha256'];assert sha((R/row['document']).read_bytes())==row['document_sha256']
 for name,old in prior_maps.items():
  if old is not None and old!=proposals[name]:snapshot(name,sha(old),old)
 for name,bytes_ in archives.items():
  target=R/name;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():target.write_bytes(bytes_)
 for name,bytes_ in proposals.items():(R/name).write_bytes(bytes_)
 assert before=={path:sha((R/path).read_bytes())for path in sources}
 for row in required:checked_receipt(R,row['document'],row['original_path'],row['sha256'])
 result={'identity':'kelvin-profile-review-guard-correction-v1','scope':'Add missing exact vw96 review document guard and original AGENTS binding; preserve changed sidecar reverse pins without changing approval/review','current_source_snapshots':[{'original_path':path,'sha256':before[path],'archived_path':'catalogue/source-snapshots/'+before[path]+'/'+path}for path in sorted(sources)],'original_documents':originals,'files':{path:sha(bytes_)for path,bytes_ in archives.items()}|{path:sha(bytes_)for path,bytes_ in proposals.items()},'preserved_bindings':required,'source_files_unchanged':True,'passed':True};(B/'receipt.json').write_bytes(enc(result));print('READY',len(archives),'canonical snapshots;',len(proposals),'maps;',len(required),'preservedbindings')
if __name__=='__main__':main()
