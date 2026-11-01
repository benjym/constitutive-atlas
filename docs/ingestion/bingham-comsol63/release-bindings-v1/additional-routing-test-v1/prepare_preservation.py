"""Coordinator preparation only. Default stages/simulates; --apply installs archives/maps.
This file was syntax inspected, not executed by the audit worker.
"""
import argparse,pathlib,hashlib,json,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[5];OUT=pathlib.Path(__file__).resolve().parent
PLAN_SHA='84f95bcbefea99f1f1122147a39783fa152d940cacb5a8af1e2eb055198b8730'
sha=lambda b:hashlib.sha256(b).hexdigest()
def path(n):
 p=pathlib.Path(n);assert not p.is_absolute() and '..' not in p.parts
 q=(ROOT/p).resolve();assert q.is_relative_to(ROOT);return q

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');arg=ap.parse_args()
 raw=(OUT/'plan.json').read_bytes();assert sha(raw)==PLAN_SHA;p=json.loads(raw);assert p['summary']=={'primary_live':4,'secondary_live':6,'maps':5,'copied_mentions':64,'historical_other_hashes':7,'unresolved':0}
 before={};snapshots={};maps={};docs={};added=[]
 def remember(n,h=None):
  b=path(n).read_bytes()
  if h:assert sha(b)==h,('concurrent source/document change',n)
  assert n not in before or before[n]==b;before[n]=b;return b
 def archive(n,b):
  dest='catalogue/source-snapshots/'+sha(b)+'/'+n
  if path(dest).exists():assert path(dest).read_bytes()==b
  snapshots[dest]=b
 archive(p['target'],remember(p['target'],p['target_sha256']))
 copied={r['document']:remember(r['document']) for r in p['copied_mentions']}
 for row in p['maps']:
  n=row['sidecar'];assert not row['document_conflicts']
  if row['exists']:
   b=remember(n,row['before_sha256']);archive(n,b);m=json.loads(b)
  else:
   assert not path(n).exists();before[n]=None;m={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  assert m['version']=='immutable-source-archive-map-0.1';maps[n]=m
  for sib in row['siblings']:
   b=remember(sib['document'],sib['sha256']);m['documents'].setdefault(sib['document'],sha(b))
 for row in p['primary']+p['secondary']:
  n=row['original_path'];h=row['sha256'];doc=row['document'];m=maps[row['sidecar']]
  b=remember(doc,row['document_sha256']);docs[doc]=b;assert m['documents'].get(doc,sha(b))==sha(b);m['documents'][doc]=sha(b)
  archive(n,remember(n,h));e={'original_path':n,'sha256':h,'archived_path':'catalogue/source-snapshots/'+h+'/'+n}
  matches=[x for x in m['entries'] if x.get('original_path')==n and x.get('sha256')==h];assert not matches or matches==[e]
  if not matches:m['entries'].append(e);added.append({'sidecar':row['sidecar'],**e})
 proposed={n:(json.dumps(m,indent=2)+'\n').encode() for n,m in maps.items()}
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 with tempfile.TemporaryDirectory(prefix='atlas-bingham-routing-preservation-') as temp:
  context=pathlib.Path(temp)
  for n,b in snapshots.items()|docs.items()|proposed.items():
   f=context/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  for row in p['primary']+p['secondary']:checked_receipt(context,row['document'],row['original_path'],row['sha256'])
 def unchanged():
  for n,b in before.items():assert (not path(n).exists()) if b is None else path(n).read_bytes()==b,('concurrent change',n)
 unchanged();stage=OUT/'prepared-v1'
 for n,b in snapshots.items()|proposed.items():
  f=stage/'tree'/n;f.parent.mkdir(parents=True,exist_ok=True)
  if f.exists():assert f.read_bytes()==b
  else:f.write_bytes(b)
 result={'plan_sha256':PLAN_SHA,'checked_bindings':10,'source_targets':1,'maps':5,'new_maps':1,'old_map_archives':4,'archives':{n:sha(b) for n,b in snapshots.items()},'proposed_maps':{n:sha(b) for n,b in proposed.items()},'added_entries':added,'unchanged_receipts':{n:sha(b) for n,b in docs.items()},'unchanged_copied_context_documents':{n:sha(b) for n,b in copied.items()},'applied':False}
 if arg.apply:
  unchanged()
  for n,b in snapshots.items():
   f=path(n);f.parent.mkdir(parents=True,exist_ok=True)
   if f.exists():assert f.read_bytes()==b
   else:f.write_bytes(b)
  for n,b in proposed.items():
   f=path(n);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  for n,b in docs.items()|copied.items():assert path(n).read_bytes()==b
  for row in p['primary']+p['secondary']:checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])
  result['applied']=True
 (stage/('applied.json' if arg.apply else 'prospective.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['checked_bindings','source_targets','maps','new_maps','old_map_archives','applied']},indent=2))
if __name__=='__main__':main()
