from pathlib import Path
import hashlib,json,re
O=Path(__file__).resolve().parent;R=O.parents[3];target='.github/workflows/verify.yml';h=hashlib.sha256((R/target).read_bytes()).hexdigest()
def pairs(n):
 if isinstance(n,dict):
  for k,v in n.items():
   if isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) and ('/' in k or '.' in k):yield k,v
  if isinstance(n.get('path'),str):
   for k in ['hash','sha256']:
    if isinstance(n.get(k),str) and re.fullmatch('[0-9a-f]{64}',n[k]):yield n['path'],n[k]
  for v in n.values():yield from pairs(v)
 elif isinstance(n,list):
  for v in n:yield from pairs(v)
rows=[];scanned=0
for folder in ['catalogue','docs','tools','tests','schemas']:
 for p in (R/folder).rglob('*.json'):
  if O.is_relative_to(p) or p.is_relative_to(O):continue
  scanned+=1;b=p.read_bytes()
  if h.encode() not in b:continue
  try:n=json.loads(b)
  except ValueError:continue
  rows.append({'document':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'recognized_old_workflow_pairs':[list(z) for z in pairs(n) if z==(target,h)]})
x={'workflow_sha256':h,'json_files_scanned':scanned,'mentions':rows};(O/'WORKFLOW-DISCOVERY.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
