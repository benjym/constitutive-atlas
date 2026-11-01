import gzip
"""No mutation: simulate all nine sources changed plus proposed sidecar replacements."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;x=json.loads((B/'minimal-inventory.json').read_text() if (B/'minimal-inventory.json').exists() else gzip.decompress((B/'minimal-inventory.json.gz').read_bytes()));raw=json.loads((B/'inventory.json').read_text() if (B/'inventory.json').exists() else gzip.decompress((B/'inventory.json.gz').read_bytes()));commit=x['summary']['baseline'];cache={};newmaps=x['sidecar_proposals'];archives={r['archived_path']:r for r in x['canonical_archives']}
def baseline(p):
 if p not in cache:cache[p]=subprocess.check_output(['git','show',commit+':'+p],stderr=subprocess.DEVNULL)
 return cache[p]
def sha(b):return hashlib.sha256(b).hexdigest()
def virtual(p):
 if p in newmaps:return(B/'minimal-planned-sidecars'/p).read_bytes()
 if p in x['baseline_source_pins']:return b'Prospective changed source; original exact bytes archived separately.'
 if p in archives:return baseline(archives[p]['original_path'])
 return baseline(p)
def excluded(name):
 import re
 return any(p in {'source-snapshots','frozen-sources','receipt-bytes','prior-source','source','source-mirror','planned-sidecars','proposal-inputs','context','isolated'}or re.fullmatch(r'.*-context-v\d+',p)or re.fullmatch(r'prior-v\d+',p)for p in Path(name).parts)
rows=[r for r in raw['primary_edges']+raw['secondary_edges']if not excluded(r['document'])and r['resolution']in['live','archived']];failures=[]
for r in rows:
 try:
  doc=r['document'];path=r['original_path'];expected=r['sha256'];side=str(Path(doc).parent/'source-archive-map.json');chosen=path
  try:m=json.loads(virtual(side))
  except(subprocess.CalledProcessError,FileNotFoundError):m=None
  if m:
   assert m['documents'].get(doc)==sha(virtual(doc)),('document pin',doc)
   matches=[z for z in m['entries']if z.get('original_path')==path and z.get('sha256')==expected];assert len(matches)<=1
   if matches:chosen=matches[0]['archived_path'];assert chosen=='catalogue/source-snapshots/'+expected+'/'+path
  assert sha(virtual(chosen))==expected,('source pin',chosen)
 except Exception as e:failures.append(dict(document=r['document'],original_path=r['original_path'],error=str(e)))
# Proposals preserve every original entry/document rather than resetting shared maps.
for path in newmaps:
 try:old=json.loads(baseline(path))
 except subprocess.CalledProcessError:continue
 new=json.loads(virtual(path));assert all(e in new['entries']for e in old['entries']);assert all(new['documents'].get(k)==v for k,v in old['documents'].items())
for r in x['canonical_archives']:assert sha(baseline(r['original_path']))==r['sha256']
result=dict(identity='kelvin-release-bindings-virtual-check-v1',baseline=commit,previously_resolved_active_pairs=len(rows),new_resolution_failures=failures,passed=not failures,scope='Exact nine source replacements simulated; original document bytes and expected hashes unchanged; copies/frozen namespaces excluded. No shared writes/builds/compiled calls.')
(B/'virtual-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not failures
