"""Coordinator-only conservative preservation preparation; not run by the auditor.

Default stages proposed archives/maps only under this packet/prepared-v1.
--apply installs the exact staged additive result after a second concurrency check.
Historical receipt/review documents and expected hashes are never rewritten.
"""
import argparse,hashlib,json,pathlib,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
PLAN_SHA='1c6ce7183340999e73c24c5266d69f10e17a0099049e9a65e2a6921136f3ba83'
sha=lambda b:hashlib.sha256(b).hexdigest()
def safe(name):
 p=pathlib.Path(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe path: '+name)
 q=(ROOT/p).resolve()
 if not q.is_relative_to(ROOT):raise ValueError('escaped root: '+name)
 return q

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 raw=(HERE/'current-v3/plan.json').read_bytes();assert sha(raw)==PLAN_SHA,'audit plan bytes changed';plan=json.loads(raw)
 assert len(plan['targets'])==9 and len(plan['sidecars_to_add_or_extend'])==67
 primary=plan['primary_live_edges_requiring_addition'];secondary=plan['secondary_live_map_edges_requiring_addition'];assert len(primary)==187 and len(secondary)==292
 before={};archives={};maps={};documents={};added=[]
 def remember(name,expected=None):
  data=safe(name).read_bytes()
  if expected is not None:assert sha(data)==expected,('baseline changed',name)
  if name in before:assert before[name]==data
  else:before[name]=data
  return data
 def archive(name,data):
  h=sha(data);dest='catalogue/source-snapshots/'+h+'/'+name
  if safe(dest).exists():assert safe(dest).read_bytes()==data,('existing snapshot differs',dest)
  archives[dest]=data
 for row in plan['targets']:
  data=remember(row['path'],row['base_sha256']);archive(row['path'],data)
 for row in plan['sidecars_to_add_or_extend']:
  name=row['sidecar']
  if row['exists']:
   data=remember(name,row['base_sha256']);archive(name,data);m=json.loads(data)
  else:
   assert not safe(name).exists(),('new sidecar appeared',name)
   before[name]=None;m={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  assert m['version']=='immutable-source-archive-map-0.1'
  assert not row['document_pin_conflicts'],'document version conflict requires explicit prior archival'
  maps[name]=m
  for sib in row['file_manifest_sibling_coverage']:
   data=remember(sib['document'],sib['sha256'])
   # Existing older sibling bindings stay intact; this preparation does not roll them forward.
   m['documents'].setdefault(sib['document'],sha(data))
 for row in primary+secondary:
  doc=row['document'];name=row['original_path'];expected=row['sha256'];side=str(pathlib.Path(doc).parent/'source-archive-map.json');m=maps[side]
  data=remember(doc,row['document_sha256']);documents[doc]=data
  assert m['documents'].get(doc,sha(data))==sha(data),('immutable document pin conflict',doc)
  m['documents'][doc]=sha(data)
  source=remember(name,expected);archive(name,source)
  e={'original_path':name,'sha256':expected,'archived_path':'catalogue/source-snapshots/'+expected+'/'+name}
  matches=[x for x in m['entries'] if x.get('original_path')==name and x.get('sha256')==expected]
  assert not matches or matches==[e],('duplicate/different existing entry',side,name)
  if not matches:m['entries'].append(e);added.append({'sidecar':side,**e})
 proposed={name:(json.dumps(m,indent=2)+'\n').encode() for name,m in maps.items()}
 # Simulate all479 original document-bound references in a private context.
 # This is evidence resolution only: no model evaluator or compiled artifact is invoked.
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 with tempfile.TemporaryDirectory(prefix='atlas-bingham-preservation-check-') as temp:
  context=pathlib.Path(temp)
  for name,data in archives.items()|documents.items()|proposed.items():
   p=context/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  for row in primary+secondary:
   p=checked_receipt(context,row['document'],row['original_path'],row['sha256'])
   assert sha(p.read_bytes())==row['sha256']
 def unchanged():
  for name,data in before.items():
   p=safe(name)
   assert (not p.exists()) if data is None else p.read_bytes()==data,('concurrent change',name)
 unchanged()
 stage=HERE/'prepared-v1';stage.mkdir(exist_ok=True)
 for name,data in archives.items()|proposed.items():
  p=stage/'tree'/name;p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():assert p.read_bytes()==data,('prior preparation differs',name)
  else:p.write_bytes(data)
 manifest={'plan_sha256':PLAN_SHA,'mode':'conservative all67 candidate maps including retained copied receipt contexts; coordinator explicitly requested this scope','source_targets':9,'existing_sidecars_archived':62,'proposed_sidecars':67,'new_sidecars':5,'primary_bindings_checked':187,'secondary_bindings_checked':292,'added_unique_entries':len(added),'archives':{n:sha(b) for n,b in archives.items()},'sidecars':{n:sha(b) for n,b in proposed.items()},'immutable_receipt_documents':{n:sha(b) for n,b in documents.items()},'receipt_documents_rewritten':False,'applied':False}
 if args.apply:
  unchanged()
  # Preserve all old bytes before modifying any map; no expected source/document hash changes.
  for name,data in archives.items():
   p=safe(name);p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():assert p.read_bytes()==data
   else:p.write_bytes(data)
  for name,data in proposed.items():
   p=safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  for name,data in documents.items():assert safe(name).read_bytes()==data,('receipt changed',name)
  for row in primary+secondary:checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])
  manifest['applied']=True
 (stage/('applied.json' if args.apply else 'prospective.json')).write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({k:manifest[k] for k in ['source_targets','proposed_sidecars','primary_bindings_checked','secondary_bindings_checked','added_unique_entries','applied']},indent=2))
if __name__=='__main__':main()
