"""Union immutable parent metadata, preserving both exact parent receipt inputs."""
from pathlib import Path
import json,subprocess,hashlib,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
def raw(rev,p):return subprocess.check_output(['git','show',f'{rev}:{p}'],cwd=ROOT)
def union_map(a,b):
 assert a['version']==b['version']
 out=json.loads(json.dumps(b))
 for k,v in a['documents'].items():assert k not in out['documents'] or out['documents'][k]==v;out['documents'][k]=v
 for e in a['entries']:
  m=[x for x in out['entries'] if (x['original_path'],x['sha256'])==(e['original_path'],e['sha256'])];assert not m or m==[e]
  if not m:out['entries'].append(e)
 return out
if __name__=='__main__':
 conflicts=subprocess.check_output(['git','diff','--name-only','--diff-filter=U'],cwd=ROOT,text=True).splitlines()
 for p in conflicts:
  a,b=json.loads(raw('HEAD',p)),json.loads(raw('origin/main',p))
  if p=='catalogue/approved-models.json':
   ours=[x for x in a['models'] if x['model_id']=='barodesy-sand'];assert len(ours)==1;assert not any(x['model_id']=='barodesy-sand' for x in b['models'])
   source=raw('origin/main',p).decode();idx=source.rfind('\n  ]');assert idx>=0
   text=source[:idx]+',\n'+ '\n'.join('    '+line for line in json.dumps(ours[0],indent=2).splitlines())+source[idx:]
  else:assert p.endswith('/source-archive-map.json');text=json.dumps(union_map(a,b),indent=2)+'\n'
  (ROOT/p).write_text(text)
 subprocess.run(['git','add','--',*conflicts],cwd=ROOT,check=True)
 print('Resolved',len(conflicts),'metadata-only conflicts by exact registry append / additive map union')
