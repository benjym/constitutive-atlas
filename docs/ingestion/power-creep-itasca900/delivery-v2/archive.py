"""Preserve exact prior bytes and additive receipt bindings for this delivery."""
from pathlib import Path
import hashlib,json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
excluded={'source-snapshots','snapshots','frozen','frozen-sources','frozen-source','frozen-sources-v1','inputs','reviewed-sources','prior-source'}
paths=set(subprocess.check_output(['git','ls-files','--','*.json'],cwd=ROOT,text=True).splitlines())
paths.add('catalogue/agent-reviews/power-creep-agent-v2.json')
docs={}
for p in paths:
 if not (ROOT/p).is_file() or excluded&set(Path(p).parts):continue
 try:docs[p]=json.loads((ROOT/p).read_text())
 except (ValueError,UnicodeDecodeError):pass
changes=json.loads((OUT/'before.json').read_text());changes={p:h for p,h in changes.items() if p in ['atlas/research.py','web/power-creep.html','tools/build_power_creep_web.py','tools/test_power_creep_package.mjs']}
originals={p:OUT/'prior-source'/p for p in changes}
def pairs(v):
 if isinstance(v,dict):
  for k,h in v.items():
   if isinstance(h,str) and len(h)==64:yield k,h
  if isinstance(v.get('path'),str):
   for k in ['sha256','hash']:
    if isinstance(v.get(k),str):yield v['path'],v[k]
  for x in v.values():yield from pairs(x)
 elif isinstance(v,list):
  for x in v:yield from pairs(x)
refs=[];seen=set();maps={}
while True:
 n=len(changes)
 for doc,v in docs.items():
  for p,h in pairs(v):
   if changes.get(p)!=h or (doc,p,h) in seen:continue
   seen.add((doc,p,h));side=(Path(doc).parent/'source-archive-map.json').as_posix()
   if side not in maps:maps[side]=json.loads((ROOT/side).read_text()) if (ROOT/side).exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
   m=maps[side]
   m.setdefault('version','immutable-source-archive-map-0.1');m.setdefault('documents',{});m.setdefault('entries',[])
   if any(e['original_path']==p and e['sha256']==h for e in m['entries']):continue
   refs.append((doc,p,h,side))
   if (ROOT/side).exists() and side not in changes:
    changes[side]=sha(ROOT/side);originals[side]=ROOT/side
 if len(changes)==n:break
for p,h in changes.items():
 src=originals[p];assert sha(src)==h,p
 dest=ROOT/'catalogue/source-snapshots'/h/p;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert sha(dest)==h
 else:shutil.copyfile(src,dest)
for doc,p,h,side in refs:
 m=maps[side];m['documents'][doc]=sha(ROOT/doc)
 entry={'original_path':p,'sha256':h,'archived_path':str(Path('catalogue/source-snapshots')/h/p)}
 if entry not in m['entries']:m['entries'].append(entry)
for side,m in maps.items():(ROOT/side).write_text(json.dumps(m,indent=2)+'\n')
(OUT/'archive-result.json').write_text(json.dumps({'snapshots':changes,'receipt_edges':[{'document':d,'path':p,'sha256':h,'sidecar':s} for d,p,h,s in refs],'sidecars':list(maps)},indent=2)+'\n')
print('Preserved',len(changes),'original files/maps and',len(refs),'receipt edges')
