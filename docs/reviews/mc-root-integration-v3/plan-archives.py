from pathlib import Path
import subprocess,json,hashlib
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/mc-root-integration-v3';P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
valid=lambda h:isinstance(h,str)and len(h)==64 and all(c in '0123456789abcdef'for c in h)
excluded={'source-snapshots','snapshots','frozen','frozen-sources','frozen-source','frozen-sources-v1','inputs','reviewed-sources'}
docs={}
for n in subprocess.check_output(['git','ls-files','--','*.json'],cwd=R,text=True).splitlines():
 if any(x in excluded for x in Path(n).parts):continue
 if not(R/n).is_file():continue
 try:obj=json.loads((R/n).read_text())
 except (ValueError,UnicodeDecodeError):continue
 docs[n]=obj

def pairs(obj):
 if isinstance(obj,dict):
  for n,h in obj.items():
   if valid(h):yield n,h
  n=obj.get('path',obj.get('original_path'))
  if isinstance(n,str):
   for hk in ['sha256','hash']:
    if valid(obj.get(hk)):yield n,obj[hk]
  for v in obj.values():yield from pairs(v)
 elif isinstance(obj,list):
  for v in obj:yield from pairs(v)
changes={n:sha(R/n)for n in ['catalogue/manifest.json', 'catalogue/applicability/kfs-development-v1.json', 'catalogue/laboratory-examples.json', 'web/index.html', 'web/app.js', 'ROADMAP.md', 'docs/STATUS.md']}
refs=[];maps={};seen=set()
while True:
 before=len(changes)
 for doc,obj in docs.items():
  for path,h in pairs(obj):
   if path not in changes or changes[path]!=h or (doc,path,h)in seen:continue
   side=(Path(doc).parent/'source-archive-map.json').as_posix()
   old=json.loads((R/side).read_text())if(R/side).exists()else None
   # Already archived references remain valid and require no map mutation.
   if old and any(e.get('original_path')==path and e.get('sha256')==h for e in old['entries']):
    seen.add((doc,path,h));continue
   refs.append({'document':doc,'original_path':path,'sha256':h,'sidecar':side});seen.add((doc,path,h))
   maps[side]=old
   if old and side not in changes:changes[side]=sha(R/side)
 if len(changes)==before:break
bindings={}
for side in maps:
 bindings[side]={q.relative_to(R).as_posix():sha(q)for q in(R/side).parent.glob('*.json')if q.name!='source-archive-map.json'}
plan={'version':'mc-root-integration-archive-plan-0.1','initial_changes':['catalogue/manifest.json', 'catalogue/applicability/kfs-development-v1.json', 'catalogue/laboratory-examples.json', 'web/index.html', 'web/app.js', 'ROADMAP.md', 'docs/STATUS.md'],'original_bytes':changes,'references':refs,'sibling_document_bindings':bindings}
(P/'archive-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Archive plan:',len(changes),'exact source/map snapshots;',len(refs),'receipt edges;',len(maps),'additive sidecars')
