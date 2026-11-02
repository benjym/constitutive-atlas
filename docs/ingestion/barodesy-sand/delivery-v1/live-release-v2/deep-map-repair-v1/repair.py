import json,hashlib,subprocess,sys
from pathlib import Path
R=Path('/private/tmp/atlas-barodesysand-live-v2'); sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
D=R/'docs/ingestion/barodesy-sand/delivery-v1/live-release-v2/deep-map-repair-v1';D.mkdir(exist_ok=True)
source=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/barodesy-sand/delivery-v1/interface-review-v3/live-e8-v2/initial-binding-failures.json')
rows=json.loads(source.read_text())['failures']; pending={}; before={}; snapshots={}; reverse=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
def pairs(n,path,h):
 if isinstance(n,dict):
  if n.get(path)==h or n.get('path')==path and (n.get('sha256')==h or n.get('hash')==h):return True
  return any(pairs(v,path,h)for v in n.values())
 return isinstance(n,list)and any(pairs(v,path,h)for v in n)
def archive(path,h,data):
 assert sha(data)==h
 dest='catalogue/source-snapshots/'+h+'/'+path
 snapshots[dest]=data
 return dict(original_path=path,sha256=h,archived_path=dest)
def add(row):
 name=str(Path(row['document']).parent/'source-archive-map.json')
 if name not in pending:
  p=R/name; raw=p.read_bytes()if p.exists()else None;before[name]=raw
  pending[name]=json.loads(raw)if raw else dict(version='immutable-source-archive-map-0.1',documents={},entries=[])
 m=pending[name];doc=row['document'];h=sha((R/doc).read_bytes())
 assert doc not in m['documents']or m['documents'][doc]==h
 m['documents'][doc]=h
 path=row['original_path'];expected=row['sha256'];archive_file=R/'catalogue/source-snapshots'/expected/path
 data=archive_file.read_bytes()if archive_file.exists()else before.get(path)
 if data is None:
  oldroot=Path('/private/tmp/atlas-barodesysand-delivery-v1');oldarchive=oldroot/'catalogue/source-snapshots'/expected/path
  data=oldarchive.read_bytes()if oldarchive.exists()else (R/path).read_bytes()
 e=archive(path,expected,data)
 if e not in m['entries']:m['entries'].append(e)
for row in rows:add(row)
scanned=set()
while set(pending)-scanned:
 for name in sorted(set(pending)-scanned):
  scanned.add(name);old=before[name]
  if old is None:continue
  h=sha(old);archive(name,h,old)
  found=subprocess.run(['rg','-l','-F',name,'-g','*.json','-g','!**/source-archive-map.json','-g','!catalogue/source-snapshots/**','docs','catalogue','tests'],cwd=R,text=True,capture_output=True)
  assert found.returncode in (0,1)
  for doc in found.stdout.splitlines():
   if not pairs(json.loads((R/doc).read_text()),name,h):continue
   checked_receipt(R,doc,name,h)
   row=dict(document=doc,original_path=name,sha256=h);reverse.append(row);add(row)
for name,data in snapshots.items():
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
for name,m in pending.items():(R/name).write_text(json.dumps(m,indent=2)+'\n')
for row in rows+reverse:checked_receipt(R,row['document'],row['original_path'],row['sha256'])
report=dict(identity='barodesy-deep-map-repair-v1',scope='Additive historical archive mappings only; original receipt and executable files unchanged',original_failures=rows,reverse_bindings=reverse,prior_maps={p:sha(b)if b else None for p,b in before.items()},files={p:sha((R/p).read_bytes())for p in list(pending)+list(snapshots)},passed=True)
(D/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');(D/'repair.py').write_bytes(Path(__file__).read_bytes());print('PASS',len(rows),'bindings',len(pending),'maps',len(reverse),'reverse bindings',len(snapshots),'snapshots')
