#!/usr/bin/env python3
"""Read-only Git receipt scan of the two bounded model deltas, with exact pin context."""
from pathlib import Path
import json,subprocess,hashlib,re
P=Path(__file__).resolve().parent;status=json.loads((P/'three-way-status.json').read_text());targets={x['path'] for x in status['overlap']}
def git(*a):return subprocess.check_output(['git',*a])
def pins(node):
 if isinstance(node,dict):
  if node.get('path') in targets:
   for key in ['sha256','hash']:
    if isinstance(node.get(key),str) and re.fullmatch('[0-9a-f]{64}',node[key]):yield node['path'],node[key]
  for k,v in node.items():
   if k in targets and isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v):yield k,v
   yield from pins(v)
 elif isinstance(node,list):
  for x in node:yield from pins(x)
known={(x['original_path'],x['sha256']):x for x in json.loads((P/'archive-contexts.json').read_text())}
rows=[];map_inputs={}
for side,paths in [('interface',status['interface_changed']),('published',status['published_changed'])]:
 ref=status['refs'][side]
 for f in paths:
  if not f.endswith('.json'):continue
  raw=git('show',ref+':'+f)
  try:d=json.loads(raw)
  except ValueError:continue
  hits=sorted(set(pins(d)))
  if not hits:continue
  parent=Path(f).parent;sidecar=str(parent/'source-archive-map.json')
  try:mapraw=git('show',ref+':'+sidecar);mapping=json.loads(mapraw)
  except (subprocess.CalledProcessError,ValueError):mapraw=None;mapping={}
  if mapraw:map_inputs[sidecar]=mapraw
  for target,sha in hits:
   proposed=hashlib.sha256((P/'proposed'/target).read_bytes()).hexdigest()
   if sha==proposed:continue
   existing=[x for x in mapping.get('entries',[]) if x.get('original_path')==target and x.get('sha256')==sha]
   rows.append({'side':side,'document':f,'document_sha256':hashlib.sha256(raw).hexdigest(),'original_path':target,'sha256':sha,'sidecar':sidecar,'document_already_bound':mapping.get('documents',{}).get(f)==hashlib.sha256(raw).hexdigest(),'existing_matching_entries':len(existing),'context_archive':known.get((target,sha)),'classification':'existing-map-context' if existing else 'new-context-archive' if (target,sha) in known else 'historical-other-context-unresolved'})
for f,b in map_inputs.items():
 t=P/'inputs/maps'/f;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b)
(P/'receipt-pin-audit.json').write_text(json.dumps({'bounded_scope':'All changed JSON receipts in both model deltas; full unmodified historical tree is not rescanned','rows':rows,'count':len(rows),'unresolved':sum(x['classification']=='historical-other-context-unresolved' for x in rows)},indent=2)+'\n')
print('ChangedJSON receiptpins',len(rows),'unresolved',sum(x['classification']=='historical-other-context-unresolved' for x in rows));print('Documents',len({x['document'] for x in rows}));print('Classes', {k:sum(x['classification']==k for x in rows) for k in {x['classification'] for x in rows}})
