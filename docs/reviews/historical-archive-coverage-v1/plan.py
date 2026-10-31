"""Read-only live-map closure; no historical document mutations."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');W=Path(__file__).resolve().parent
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
valid=lambda h:isinstance(h,str)and re.fullmatch('[a-f0-9]{64}',h)is not None
def manifest(d):return isinstance(d,dict)and(isinstance(d.get('files'),dict)or isinstance(d.get('dependencies'),dict)or(d and all(valid(h)for h in d.values())))
excluded={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','reviewed-sources'}
missing=[];historical=[]
for side in sorted((R/'catalogue').rglob('source-archive-map.json')):
 m=load(side)
 for p in sorted(side.parent.glob('*.json')):
  if p==side or not manifest(load(p)):continue
  rel=p.relative_to(R).as_posix()
  if rel not in m['documents']:
   row={'document':rel,'document_sha256':sha(p),'sidecar':side.relative_to(R).as_posix()}
   (historical if any(x in excluded for x in p.relative_to(R).parts)else missing).append(row)
def pairs(n):
 if isinstance(n,dict):
  for p,h in n.items():
   if (p.endswith('/source-archive-map.json')or p=='tests/test_evidence_archives.py')and valid(h):yield p,h,'direct'
  for key in ('path','original_path'):
   p=n.get(key)
   if isinstance(p,str)and (p.endswith('/source-archive-map.json')or p=='tests/test_evidence_archives.py'):
    for hk in ('sha256','hash'):
     if valid(n.get(hk)):yield p,n[hk],key
  for x in n.values():yield from pairs(x)
 elif isinstance(n,list):
  for x in n:yield from pairs(x)
refs={}
for name in subprocess.check_output(['git','ls-files','-z','--','*.json'],cwd=R).decode().split('\0'):
 if not name or name.split('/')[0]not in {'catalogue','docs','tools','schemas','tests'}or any(x in excluded for x in Path(name).parts):continue
 try:node=load(R/name)
 except Exception:continue
 for path,h,shape in pairs(node):
  row=refs.setdefault((name,path,h),{'document':name,'document_sha256':sha(R/name),'original_path':path,'sha256':h,'shapes':[]});row['shapes'].append(shape)
changed={r['sidecar']for r in missing};assignments={r['document']:r for r in missing}
test_source='tests/test_evidence_archives.py';test_pin=sha(R/test_source);test_rows=[]
for row in refs.values():
 if row['original_path']!=test_source or row['sha256']!=test_pin:continue
 resolved=checked_receipt(R,row['document'],test_source,test_pin)
 assert resolved==R/test_source
 row=dict(row);row['resolved_before']=resolved.relative_to(R).as_posix();test_rows.append(row)
 side=(Path(row['document']).parent/'source-archive-map.json').as_posix();changed.add(side)
 assignments.setdefault(row['document'],{'document':row['document'],'document_sha256':row['document_sha256'],'sidecar':side})
while True:
 old=set(changed)
 for row in refs.values():
  if row['original_path']not in changed:continue
  try:resolved=checked_receipt(R,row['document'],row['original_path'],row['sha256'])
  except Exception:continue
  if resolved==R/row['original_path']:
   side=(Path(row['document']).parent/'source-archive-map.json').as_posix();changed.add(side)
   assignments.setdefault(row['document'],{'document':row['document'],'document_sha256':row['document_sha256'],'sidecar':side})
 if changed==old:break
# Every newly touched live map covers all sibling file manifests under the current rule.
for name in sorted(changed):
 for p in (R/name).parent.glob('*.json'):
  if p.name=='source-archive-map.json' or not manifest(load(p)):continue
  doc=p.relative_to(R).as_posix();assignments.setdefault(doc,{'document':doc,'document_sha256':sha(p),'sidecar':name})
old_maps={p:sha(R/p)if(R/p).exists()else None for p in sorted(changed)}
affected=[]
for row in refs.values():
 if row['original_path']not in changed:continue
 row=dict(row)
 try:row['resolved_before']=checked_receipt(R,row['document'],row['original_path'],row['sha256']).relative_to(R).as_posix();row['resolution']='checked'
 except Exception as e:
  row['resolution']='unresolved';row['error']=str(e)
  if 'original_path'in row['shapes']:
   archive=R/'catalogue/source-snapshots'/row['sha256']/row['original_path'];live=R/row['original_path']
   if archive.is_file()and sha(archive)==row['sha256']:row['resolution']='descriptive-archived'
   elif live.is_file()and sha(live)==row['sha256']:row['resolution']='descriptive-live'
 affected.append(row)
for row in assignments.values():
 p=R/row['sidecar'];mapping=load(p)if p.exists()else{};pin=mapping.get('documents',{}).get(row['document']);assert pin is None or pin==row['document_sha256'],row
result={'base_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'missing_live':missing,'historical_namespace_failures':historical,'test_source':{'path':test_source,'sha256':test_pin,'receipts':test_rows},'old_maps':old_maps,'documents':list(assignments.values()),'affected_reverse_references':affected,'policy':'Append live document pins and required reverse entries only; archive every prior changed-map byte at canonical content address first. Preserve all original receipt bytes, document pins, entries and unresolved references. Frozen namespaces receive no mutations.'}
(W/'plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'missing_live':len(missing),'historical':len(historical),'maps':len(changed),'document_pins':len(assignments),'reverse_edges':len(affected),'reverse_states':{v:sum(r['resolution']==v for r in affected)for v in {r['resolution']for r in affected}}}))
