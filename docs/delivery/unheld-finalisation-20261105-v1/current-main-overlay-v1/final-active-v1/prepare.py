from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;D=P.parent;BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source');OUT=P/'proposed'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(x):return (json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
rows=json.loads((D/'source-delta.json').read_text())['files'];changes={}
def put(path,b,reason):
 old=(BASE/path).read_bytes() if (BASE/path).is_file() else None
 if old==b:return
 target=OUT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 changes[path]={'path':path,'preimage_sha256':sha(old) if old is not None else None,'preimage_mode':'100644' if old is not None else None,'sha256':sha(b),'bytes':len(b),'mode':'100644','proposal':target.relative_to(P).as_posix(),'reason':reason}
for row in rows:
 if row['path'] in ['atlas/research.py','catalogue/approved-models.json','catalogue/source-archive-map.json']:continue
 put(row['path'],(D/row['proposal']).read_bytes(),row['reason'])
oldraw=(BASE/'catalogue/approved-models.json').read_bytes();old=json.loads(oldraw);draft=json.loads((D/'proposed/catalogue/approved-models.json').read_text());new={a['model_id']:a for a in draft['models'][30:]};assert len(new)==5
history_path='catalogue/approval-history/baseline-five-supersession-20261105-v1.json';oldarchive=f'catalogue/source-snapshots/{sha(oldraw)}/catalogue/approved-models.json'
relationships=[];active=[]
for a in old['models']:
 if a['model_id'] in new:
  replacement=new[a['model_id']];relationships.append({'model_id':a['model_id'],'historical_approval_id':a['id'],'historical_definition':a['definition'],'current_approval_id':replacement['id'],'current_definition':replacement['definition']});active.append(replacement)
 else:active.append(a)
assert len(relationships)==5 and len(active)==30
history={'schema_version':'0.1','kind':'exact-active-approval-supersession-history','id':'baseline-five-supersession-20261105-v1','historical_registry':{'path':oldarchive,'sha256':sha(oldraw),'source_url':'https://github.com/benjym/constitutive-atlas/blob/main/'+oldarchive},'scope':'Only active registration changes. Historical approvals/reviews/definitions remain exact; no legacy approval transfers to current bytes.','supersessions':relationships}
put(history_path,dump(history),'Explicit exact legacy-registry/supersession technical history')
registry=dict(old);registry['models']=active
registry['historical_registries']=list(registry.get('historical_registries',[]))+[{'path':oldarchive,'sha256':sha(oldraw),'history':{'path':history_path,'sha256':sha(dump(history)),'url':'https://github.com/benjym/constitutive-atlas/blob/main/'+history_path}}]
put('catalogue/approved-models.json',dump(registry),'Preserve other25 ordered approvals; supersede five active identities')
# Retain old catalogue map/entries unchanged apart from exact new document pins.
m=json.loads((D/'proposed/catalogue/source-archive-map.json').read_text());m['documents']['catalogue/approved-models.json']=sha(dump(registry))
put('catalogue/source-archive-map.json',dump(m),'Additive retained history/current registry document pin')
(P/'source-delta.json').write_bytes(dump({'base_revision':'6b957b866c977263fad0c02be4216c7f9170cf5b','policy':'active-approval-supersession','files':sorted(changes.values(),key=lambda r:r['path'])}))
# Full exact base guard includes unchanged scientific support and all untouched shared source families.
basepins={}
for directory,pattern in [('atlas','*.py'),('models','*.json'),('schemas','*.json'),('web','*'),('cmake','*'),('cpp','*'),('.github/workflows','*.yml')]:
 for f in (BASE/directory).rglob(pattern):
  if f.is_file() and not f.is_symlink():
   rel=f.relative_to(BASE).as_posix()
   # Bound metadata/code only; engine binaries are separately qualified.
   if f.suffix in ['.py','.json','.mjs','.js','.html','.css','.cmake','.hpp','.cpp','.yml','.txt'] or f.name=='CMakeLists.txt':basepins[rel]=sha(f.read_bytes())
for path in json.loads((D/'direct-support.json').read_text()):
 if (BASE/path).is_file():basepins[path]=sha((BASE/path).read_bytes())
(P/'base-pins.json').write_bytes(dump(basepins))
print(json.dumps({'targets':len(changes),'payload_bytes':sum(r['bytes'] for r in changes.values()),'active_approvals':len(active),'base_pins':len(basepins)},indent=2))
