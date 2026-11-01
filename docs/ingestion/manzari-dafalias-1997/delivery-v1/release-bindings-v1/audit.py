#!/usr/bin/env python3
"""Read committed Git blobs only; produce a prospective reverse-pin plan, never archives/maps."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path,PurePosixPath
BASE='d1c3a19409adaa32791c105429a4167e5bac9d9d'
TARGETS=['catalogue/manifest.json','catalogue/approved-models.json','catalogue/laboratory-package-policy.json','catalogue/laboratory-profile-policy.json','tests/test_solver.cpp','tests/test_recorded.cpp','tools/check_native_fixture_contracts.py','.github/workflows/verify.yml','README.md','ROADMAP.md','docs/STATUS.md','IMPLEMENTATION_PLAN.md']
SKIP={'source-snapshots','source-snapshot','source-snapshots-v1','source','frozen-sources','snapshots','snapshot','compiler-snapshot','proposed-native-source','proposed-source','frozen-source','build-source-snapshot','catalogue-source','source-bytes','initial-source-bytes','prior-source','reviewed-source','reviewed-sources','release-source-context','final-source','release-source','preflight-source','source-final','source-initial','tracking-snapshots','tmd2-web-snapshot-v1','reviewed-snapshots','consumer-source-v1','delivery-source-v1','receipt-bytes','isolated'}
MAX_BYTES=2_000_000
H=re.compile(r'^[a-f0-9]{64}$')
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args])
def pairs(node,loc='$'):
 if isinstance(node,dict):
  if isinstance(node.get('path'),str):
   for k in ('sha256','hash'):
    v=node.get(k)
    if isinstance(v,str) and H.fullmatch(v):yield node['path'],v,loc+'.'+k
  for k,v in node.items():
   if isinstance(v,str) and H.fullmatch(v):yield k,v,loc+'.'+k
   if isinstance(v,(dict,list)):yield from pairs(v,loc+'.'+k)
 elif isinstance(node,list):
  for i,v in enumerate(node):yield from pairs(v,loc+'['+str(i)+']')
def run(output):
 tree={}
 for line in git('ls-tree','-rlz',BASE).split(b'\0'):
  if not line:continue
  meta,name=line.split(b'\t',1);mode,kind,oid,size=meta.decode().split(); name=name.decode()
  if kind=='blob':tree[name]={'git_blob':oid,'bytes':int(size)}
 skipped=[];selected=[]
 for name,info in tree.items():
  if set(PurePosixPath(name).parts[:-1])&SKIP or PurePosixPath(name).parts.count('docs')>1 or PurePosixPath(name).parts.count('catalogue')>1:skipped.append({'path':name,'reason':'nested-copy-or-snapshot'});continue
  if info['bytes']>MAX_BYTES:skipped.append({'path':name,'reason':'over-2MB'});continue
  if PurePosixPath(name).suffix.lower() not in {'.json','.jsonl','.md','.py','.mjs','.js','.yml','.yaml','.cpp','.hpp','.txt','.cmake'} and name!='CMakeLists.txt':continue
  selected.append(name)
 # One cat-file batch avoids spawning a subprocess per committed file.
 proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 blobs={}
 for name in sorted(set(selected+TARGETS)):
  proc.stdin.write((tree[name]['git_blob']+'\n').encode());proc.stdin.flush()
  header=proc.stdout.readline().decode().split();size=int(header[2]);blobs[name]=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
 proc.stdin.close();proc.wait()
 json_docs={};edges=[];invalid=[]
 for name in selected:
  if not name.endswith('.json'):continue
  try:d=json.loads(blobs[name])
  except (ValueError,UnicodeDecodeError,RecursionError):invalid.append(name);continue
  json_docs[name]=d
  edges.extend({'document':name,'original_path':p,'sha256':h,'locator':loc} for p,h,loc in pairs(d) if p in tree)
 targetinfo={name:{**tree[name],'sha256':sha(blobs[name]),'canonical_archive':'catalogue/source-snapshots/'+sha(blobs[name])+'/'+name} for name in TARGETS}
 pending=set(TARGETS);all_mutations=set(TARGETS);actions=[];seen=set();unsupported=[]
 # A matching sidecar entry can already isolate a historical target. A new entry
 # changes the sidecar bytes, which themselves may be hash-pinned elsewhere.
 while pending:
  changed=pending.pop(); expected=sha(blobs[changed]) if changed in blobs else sha(git('show',BASE+':'+changed))
  for e in edges:
   if e['original_path']!=changed or e['sha256']!=expected:continue
   doc=e['document'];side=str(PurePosixPath(doc).parent/'source-archive-map.json');key=(doc,changed,expected)
   if key in seen:continue
   seen.add(key);mapping=json_docs.get(side,{})
   mapped=any(x.get('original_path')==changed and x.get('sha256')==expected and x.get('archived_path')=='catalogue/source-snapshots/'+expected+'/'+changed for x in mapping.get('entries',[]) if isinstance(x,dict))
   docpin=mapping.get('documents',{}).get(doc)==sha(blobs[doc])
   action={**e,'document_sha256':sha(blobs[doc]),'sidecar':side,'sidecar_exists':side in tree,'sidecar_document_pin_present':docpin,'entry_present':mapped,'canonical_archive':'catalogue/source-snapshots/'+expected+'/'+changed,'archive_exists_in_base':('catalogue/source-snapshots/'+expected+'/'+changed) in tree,'requires_map_change':not(mapped and docpin)}
   actions.append(action)
   # Archive sidecar maps are metadata, not receipt documents to redirect to
   # themselves. Their documents map hash pins original docs. If doc is itself
   # changed, original receipt must remain untouched and metadata be extended.
   if doc.endswith('/source-archive-map.json'):
    action['classification']='sidecar-metadata-reference-review-manually';continue
   action['classification']='candidate-receipt-check-consumer-before-install'
   if not(mapped and docpin) and side not in all_mutations:
    all_mutations.add(side)
    if side in tree:pending.add(side)
 # Historical pins to older bytes are not silently rebound to the base bytes.
 historical=[e for e in edges if e['original_path'] in TARGETS and e['sha256']!=targetinfo[e['original_path']]['sha256']]
 text=[]
 needles={p:{p.encode(),v['sha256'].encode()} for p,v in targetinfo.items()}
 for name,b in blobs.items():
  for target,n in needles.items():
   if name!=target and all(x in b for x in n):text.append({'document':name,'target':target,'contains_exact_path_and_base_hash':True})
 report={'schema_version':'md1997-release-reverse-bindings-audit-1','source_commit':BASE,'scope':'prospective exact-base structural reverse path/hash audit, no map/archive mutation','targets':targetinfo,'tracked_blob_count':len(tree),'scanned_text_blob_count':len(selected),'parsed_json_document_count':len(json_docs),'skips':{'directory_tokens':sorted(SKIP),'max_bytes':MAX_BYTES,'files':skipped,'invalid_json':invalid},'direct_and_sidecar_closure':sorted(actions,key=lambda x:(x['original_path'],x['document'],x['locator'])),'prospective_mutating_paths':sorted(all_mutations),'new_sidecar_candidates':sorted(p for p in all_mutations if p not in tree),'older_target_pins':historical,'textual_path_plus_current_hash_matches':text,'limits':['Structural pairs match checked_receipt supported object/map shapes; textual matches are candidates, not proof of active runtime consumption.','JSONL and non-JSON text checked only by path+hash co-occurrence. Nested snapshots/copies and >2MB blobs excluded as recorded.','Sidecar-mediated closure is prospective: every affected consumer must be classified; custom raw-hash checks may need a separate new study rather than archive redirection.','No build, compiled call, shared edit, archival installation or scientific acceptance.']}
 output.mkdir(parents=True,exist_ok=True);(output/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'tracked':len(tree),'scanned':len(selected),'json':len(json_docs),'actions':len(actions),'mutation_paths':len(all_mutations),'older_pins':len(historical),'textmatches':len(text)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).parent);run(p.parse_args().output)
