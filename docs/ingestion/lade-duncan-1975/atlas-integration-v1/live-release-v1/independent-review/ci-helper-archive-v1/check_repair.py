"""Read-only exact-byte cached replay of normal receipt semantics."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path('/private/tmp/atlas-lade-release-v1');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import atlas.evidence as ev
H=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');A=H.parent
raw={};parsed={};original_read=Path.read_text;original_loads=json.loads;original_sha=ev._sha
sha=lambda b:hashlib.sha256(b).hexdigest()
def content(p):
 p=Path(p).resolve()
 if p not in raw:raw[p]=p.read_bytes()
 return raw[p]
def text(p,*args,**kwargs):
 if args or kwargs:return original_read(p,*args,**kwargs)
 return content(p).decode('utf-8').replace('\r\n','\n').replace('\r','\n')
def loads(s,*args,**kwargs):
 if args or kwargs:return original_loads(s,*args,**kwargs)
 if s not in parsed:parsed[s]=original_loads(s)
 return parsed[s]
def pairs(node):
 out=[]
 if isinstance(node,dict):
  for k,v in node.items():
   if isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v) and (ROOT/k).is_file():out.append((k,v))
  if isinstance(node.get('path'),str) and (ROOT/node['path']).is_file():
   for key in ['sha256','hash']:
    v=node.get(key)
    if isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v):out.append((node['path'],v))
  for v in node.values():out+=pairs(v)
 elif isinstance(node,list):
  for v in node:out+=pairs(v)
 return set(out)
checks=[];failures=[]
try:
 Path.read_text=text;json.loads=loads;ev._sha=lambda p:sha(content(p))
 manifest=H/'ci-helper-archive-v1/FINAL_REPAIR.json';final=loads(text(ROOT/manifest))
 for n,h in final['files'].items():assert sha(content(ROOT/n))==h,n
 initial=loads(text(ROOT/H/'CI_HELPER_ARCHIVE-v1.json'))
 for n,h in initial['files'].items():ev.checked_receipt(ROOT,str(H/'CI_HELPER_ARCHIVE-v1.json'),n,h)
 docs=[A/'actual-package-v2/EXECUTION_SOURCE_FREEZE.json']
 for folder in [H,H/'independent-review']:
  docs += [p.relative_to(ROOT) for p in (ROOT/folder).glob('*.json') if p.name!='source-archive-map.json']
 for doc in docs:
  pp=pairs(loads(text(ROOT/doc)))
  for n,h in sorted(pp):
   try:ev.checked_receipt(ROOT,str(doc),n,h)
   except ValueError as exc:failures.append({'document':str(doc),'source':n,'sha256':h,'error':str(exc),'live_hash_matches':sha(content(ROOT/n))==h})
   else:checks.append({'document':str(doc),'source':n,'sha256':h})
 # Retain the superseded v1 failure; do not modify its existing archive map.
 try:ev.checked_receipt(ROOT,str(A/'actual-package-v1/EXECUTION_SOURCE_FREEZE.json'),'tools/build_ci_targets.py','8577aaadbf0bde78cf6e319d33c56bdb8b81e67e7d933e25c1e560ae82f47fb3')
 except ValueError as exc:historical_v1=str(exc)
 else:historical_v1=None
finally:
 Path.read_text=original_read;json.loads=original_loads;ev._sha=original_sha
# Cached helper values are valid only if every physical input still matches.
for p,b in raw.items():assert p.read_bytes()==b,'Input drift: '+str(p)
result={'passed_predicates':len(checks),'failed_predicates':len(failures),'failures':failures,'historical_v1_helper_failure':historical_v1,'physical_inputs_unchanged':len(raw),'final_repair_sha256':sha((ROOT/manifest).read_bytes()),'replay':'Unmodified checked_receipt function, cached immutable file/text/JSON inputs; every physical input rehashed after replay. No source mutation or compiled call.'}
(HERE/'CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'PASSED_PREDICATES.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(result,indent=2))
