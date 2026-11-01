import pathlib,json,sys,hashlib,subprocess
r=pathlib.Path('/private/tmp/atlas-lade-release-v1');h=pathlib.Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');o=pathlib.Path('/Users/bmar5496/code/constitutive-atlas')/h/'independent-review/ci-compat-v3/final-audit';sys.path.insert(0,str(r));from atlas.evidence import checked_receipt
x=json.loads((r/h/'ci-compat-v3/CONTEXT_REPAIR.json').read_text());targets={(p,s)for p,s in x['prior_map_hashes'].items()if s}; found=[];errs=[]
def pairs(n):
 out=set()
 if isinstance(n,dict):
  for k,v in n.items():
   if isinstance(v,str)and len(v)==64 and '/' in k:out.add((k,v))
  if isinstance(n.get('path'),str):
   for key in ['sha256','hash']:
    if isinstance(n.get(key),str):out.add((n['path'],n[key]))
  for v in n.values():out|=pairs(v)
 elif isinstance(n,list):
  for v in n:out|=pairs(v)
 return out
for base in ['docs','catalogue']:
 for p in (r/base).rglob('*.json'):
  rel=p.relative_to(r).as_posix()
  if rel.startswith('catalogue/source-snapshots/')or p.name=='source-archive-map.json':continue
  try:ps=pairs(json.loads(p.read_text()))&targets
  except (ValueError,UnicodeError):continue
  for path,s in ps:
   try:q=checked_receipt(r,rel,path,s);found.append({'document':rel,'path':path,'sha256':s})
   except Exception as e:errs.append({'document':rel,'path':path,'sha256':s,'error':str(e)})
# exact registry compare
from atlas.agent_review import approval_entry
registry=json.loads((r/'catalogue/approved-models.json').read_text())['models'];approval=[]
for row in json.loads((o.parent/'APPROVAL_CHECKS.json').read_text()):
 a=approval_entry(r/row['path'],root=r);assert a in registry,row['path'];approval.append(row['path'])
result={'transitive_pass':len(found),'transitive_failures':errs,'resolved':found,'registry_exact':approval}
(o/'TRANSITIVE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print('transitive',len(found),'fail',len(errs));print(json.dumps(errs[:8],indent=2))
