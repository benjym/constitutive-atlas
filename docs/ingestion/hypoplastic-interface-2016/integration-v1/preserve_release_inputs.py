"""Preserve exact source receipts in the isolated release; atomically break links."""
from pathlib import Path
import hashlib,json,os
ROOT=Path('/private/tmp/atlas-interface2016-delivery-v1/release')
OUT=Path(__file__).resolve().parent
NAMES=['web/app.js','tools/build_web.py','web/model-profile-data.mjs','catalogue/manifest.json','catalogue/approved-models.json','.github/workflows/verify.yml']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.interface2016-new');assert not tmp.exists();tmp.write_bytes(b);os.replace(tmp,p)
def archive(p):
 n=p.relative_to(ROOT);target=ROOT/'catalogue/source-snapshots'/sha(p)/n
 if target.exists():assert target.read_bytes()==p.read_bytes()
 else:write(target,p.read_bytes())
 return target.relative_to(ROOT).as_posix()
def has(v,n,h):
 if isinstance(v,dict):return v.get(n)==h or (v.get('path')==n and (v.get('sha256')==h or v.get('hash')==h)) or any(has(w,n,h) for w in v.values())
 return isinstance(v,list) and any(has(w,n,h) for w in v)
originals={n:sha(ROOT/n) for n in NAMES};receipts=[]
for base in ['docs','catalogue']:
 for p in (ROOT/base).rglob('*.json'):
  if 'source-snapshots' in p.parts or any(part.startswith('retained') for part in p.parts) or p.name=='source-archive-map.json':continue
  try:s=p.read_text()
  except (UnicodeError,OSError):continue
  relevant=[n for n,h in originals.items() if n in s and h in s]
  if not relevant:continue
  v=json.loads(s)
  for n in relevant:
   if has(v,n,originals[n]):receipts.append((p,n,originals[n]))
changes=[]
for p,n,h in receipts:
 mp=p.parent/'source-archive-map.json'
 m=json.loads(mp.read_text()) if mp.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 assert m['version']=='immutable-source-archive-map-0.1'
 matches=[e for e in m['entries'] if e.get('original_path')==n and e.get('sha256')==h]
 if matches:
  assert len(matches)==1 and sha(ROOT/matches[0]['archived_path'])==h
  continue
 if mp.exists():old_archive=archive(mp)
 else:old_archive=None
 rel=p.relative_to(ROOT).as_posix();pin=sha(p)
 if rel in m['documents']:assert m['documents'][rel]==pin,('pinned receipt drift',rel)
 m['documents'][rel]=pin
 ap=archive(ROOT/n);m['entries'].append({'original_path':n,'sha256':h,'archived_path':ap})
 write(mp,(json.dumps(m,indent=2)+'\n').encode());changes.append({'map':mp.relative_to(ROOT).as_posix(),'document':rel,'source':n,'source_sha256':h,'old_map_archive':old_archive})
(OUT/'preservation-receipt.json').write_text(json.dumps({'isolated_release':str(ROOT),'source_preimages':originals,'matched_receipts':len(receipts),'map_changes':changes,'root_shared_files_modified':False},indent=2)+'\n')
print(json.dumps({'matched_receipts':len(receipts),'map_edits':len(changes)}))
