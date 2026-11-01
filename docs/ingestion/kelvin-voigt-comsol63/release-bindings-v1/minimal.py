import gzip
"""Separate immutable copied closures from active original receipt namespace."""
import hashlib,json,re,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;T=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source');x=json.loads((B/'inventory.json').read_text() if (B/'inventory.json').exists() else gzip.decompress((B/'inventory.json.gz').read_bytes()));commit=x['summary']['baseline'];objs={l.split('\t',1)[1]:l.split()[2]for l in subprocess.check_output(['git','ls-tree','-r',commit],text=True).splitlines()};cache={}
def data(n):
 if n not in cache:
  b=(T/n).read_bytes()if(T/n).is_file()else b''
  if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=objs.get(n):b=subprocess.check_output(['git','show',commit+':'+n])
  cache[n]=b
 return cache[n]
def sha(b):return hashlib.sha256(b).hexdigest()
def excluded(n):
 parts=Path(n).parts
 for p in parts:
  if p in {'source-snapshots','frozen-sources','receipt-bytes','prior-source','source','source-mirror','planned-sidecars','proposal-inputs','context','isolated'}or re.fullmatch(r'.*-context-v\d+',p)or re.fullmatch(r'prior-v\d+',p):return p
 return None
edges=x['primary_edges']+x['secondary_edges'];active=[r for r in edges if not excluded(r['document'])];copied=[dict(r,excluded_copy_marker=excluded(r['document']))for r in edges if excluded(r['document'])];required=[r for r in active if r['original_path']in x['baseline_source_pins']and r['resolution']=='live'];maps={str(Path(r['document']).parent/'source-archive-map.json')for r in required}
while True:
 extra=[r for r in active if r['original_path']in maps and r['resolution']=='live'and r not in required];before=len(maps);required+=extra;maps.update(str(Path(r['document']).parent/'source-archive-map.json')for r in extra)
 if len(maps)==before:break
proposals={};archives={}
for r in required:
 p,h=r['original_path'],r['sha256'];a='catalogue/source-snapshots/'+h+'/'+p;archives[(p,h)]={'original_path':p,'sha256':h,'archived_path':a,'already_present':a in objs}
for name in sorted(maps):
 exists=name in objs;m=json.loads(data(name))if exists else{'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]};oldentries=len(m['entries']);olddocs=len(m['documents']);parent=Path(name).parent
 for sib in objs:
  if Path(sib).parent!=parent or not sib.endswith('.json')or sib==name:continue
  try:n=json.loads(data(sib))
  except Exception:continue
  if isinstance(n,dict)and(isinstance(n.get('files'),dict)or isinstance(n.get('dependencies'),dict)or(bool(n)and all(isinstance(h,str)and re.fullmatch('[a-f0-9]{64}',h)for h in n.values()))):m['documents'][sib]=sha(data(sib))
 for r in required:
  if str(Path(r['document']).parent/'source-archive-map.json')!=name:continue
  m['documents'][r['document']]=r['document_sha256'];entry={k:archives[(r['original_path'],r['sha256'])][k]for k in['original_path','sha256','archived_path']}
  if not any(q.get('original_path')==entry['original_path']and q.get('sha256')==entry['sha256']for q in m['entries']):m['entries'].append(entry)
 dest=B/'minimal-planned-sidecars'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(m,indent=2)+'\n')
 proposals[name]={'baseline_sha256':sha(data(name))if exists else None,'proposed_sha256':sha(dest.read_bytes()),'entries_added':len(m['entries'])-oldentries,'documents_added':len(m['documents'])-olddocs}
 if exists:
  h=sha(data(name));a='catalogue/source-snapshots/'+h+'/'+name;archives[(name,h)]={'original_path':name,'sha256':h,'archived_path':a,'already_present':a in objs}
summary=dict(baseline=commit,required_primary_pairs=sum(r['original_path']in x['baseline_source_pins']for r in required),required_secondary_pairs=sum(r['original_path']not in x['baseline_source_pins']for r in required),changed_sidecars=len(proposals),canonical_snapshots=len(archives),excluded_copied_namespace_pairs=len(copied))
result={'summary':summary,'excluded_copy_namespace_policy':'Copied source/receipt/context namespaces remain immutable with their enclosing project evidence; they are not active root receipt documents. All exact copied path/hash pairs remain enumerated in inventory.json; this is a namespace classification, not a repair of pre-existing unresolved pairs. Markers are explicit in minimal.py.','baseline_source_pins':x['baseline_source_pins'],'required_additive_edges':required,'sidecar_proposals':proposals,'canonical_archives':sorted(archives.values(),key=lambda x:x['archived_path']),'excluded_copy_pairs':copied,'active_primary_edges':[r for r in active if r['original_path']in x['baseline_source_pins']]};(B/'minimal-inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summary,indent=2));print('\n'.join(proposals))
