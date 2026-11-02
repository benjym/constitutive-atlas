"""Preserve exact current tracking bytes and every literal/reverse receipt before closeout."""
import json,hashlib,subprocess,sys
from pathlib import Path
R=Path('/private/tmp/atlas-barodesysand-live-v2');sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
D=R/'docs/ingestion/barodesy-sand/delivery-v1/live-release-v3/closeout-preservation-v1'
assert not D.exists();D.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
targets=['IMPLEMENTATION_PLAN.md','docs/ingestion/barodesy-sand/DELIVERY.md','docs/ingestion/barodesy-sand/CHECKLIST.md'];original={p:(R/p).read_bytes()for p in targets};pending={};before={};snapshots={};rows=[]
def pair(n,path,h):
 if isinstance(n,dict):return n.get(path)==h or n.get('path')==path and(n.get('sha256')==h or n.get('hash')==h)or any(pair(v,path,h)for v in n.values())
 return isinstance(n,list)and any(pair(v,path,h)for v in n)
def archive(path,data):
 h=sha(data);dest='catalogue/source-snapshots/'+h+'/'+path;snapshots[dest]=data;return dict(original_path=path,sha256=h,archived_path=dest)
def references(path,data):
 h=sha(data);a=subprocess.run(['rg','-l','-F',path,'-g','*.json','-g','!**/source-archive-map.json','-g','!catalogue/source-snapshots/**','docs','catalogue','tests'],cwd=R,text=True,capture_output=True);assert a.returncode in(0,1)
 for doc in a.stdout.splitlines():
  if not pair(json.loads((R/doc).read_text()),path,h):continue
  checked_receipt(R,doc,path,h);yield dict(document=doc,original_path=path,sha256=h)
def add(row,data):
 doc=row['document'];name=str(Path(doc).parent/'source-archive-map.json')
 if name not in pending:
  raw=(R/name).read_bytes()if(R/name).exists()else None;before[name]=raw;pending[name]=json.loads(raw)if raw else dict(version='immutable-source-archive-map-0.1',documents={},entries=[])
 m=pending[name];h=sha((R/doc).read_bytes());assert doc not in m['documents']or m['documents'][doc]==h;m['documents'][doc]=h;e=archive(row['original_path'],data)
 if e not in m['entries']:m['entries'].append(e)
 rows.append(row)
for p,data in original.items():
 archive(p,data)
 for row in references(p,data):add(row,data)
scanned=set()
while set(pending)-scanned:
 for name in sorted(set(pending)-scanned):
  scanned.add(name);data=before[name]
  if data is None:continue
  archive(name,data)
  for row in references(name,data):add(row,data)
for path,data in snapshots.items():
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
for name,m in pending.items():(R/name).write_text(json.dumps(m,indent=2)+'\n')
for row in rows:checked_receipt(R,row['document'],row['original_path'],row['sha256'])
a=dict(identity='barodesy-tracking-closeout-preservation-v1',targets={p:sha(data)for p,data in original.items()},bindings=rows,files={p:sha((R/p).read_bytes())for p in list(pending)+list(snapshots)},passed=True);(D/'receipt.json').write_text(json.dumps(a,indent=2)+'\n');(D/'archive.py').write_bytes(Path(__file__).read_bytes());print('Preserved',len(original),'tracking files,',len(rows),'literal bindings,',len(pending),'maps')
