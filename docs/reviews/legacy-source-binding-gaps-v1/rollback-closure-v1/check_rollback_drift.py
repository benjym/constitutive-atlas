from pathlib import Path
import json,hashlib,subprocess,re,time
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();p=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');plan=json.loads((p/'PLAN.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();excluded={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','reviewed-sources'};targets={r['file'] for r in plan['mutations']};pins={r['file']:r['digest'] for r in plan['scanned_documents']};HEX=re.compile(r'[0-9a-f]{64}\Z');old={(r['document'],r['target'],r['expected_digest'],tuple(r['shapes'])) for r in plan['references'] if r['target'] in targets};changed=[];added_refs=[];errors=[];seen=set()
def pairs(n):
 todo=[n];found={}
 while todo:
  v=todo.pop()
  if isinstance(v,dict):
   for k,h in v.items():
    if k in targets and isinstance(h,str) and HEX.fullmatch(h):found.setdefault((k,h),set()).add('direct-map')
   for pk in ['path','original_path']:
    path=v.get(pk)
    if isinstance(path,str) and path in targets:
     for hk in ['sha256','hash']:
      h=v.get(hk)
      if isinstance(h,str) and HEX.fullmatch(h):found.setdefault((path,h),set()).add(pk+'-object')
   todo.extend(x for x in v.values() if isinstance(x,(dict,list)))
  elif isinstance(v,list):todo.extend(x for x in v if isinstance(x,(dict,list)))
 return found
for rel in subprocess.check_output(['rg','--files','catalogue','docs','tools','schemas','tests','-g','*.json'],cwd=root,text=True).splitlines():
 if any(x in excluded for x in Path(rel).parts):continue
 path=root/rel
 if not path.resolve().is_relative_to(root):errors.append({'file':rel,'error':'external symlink'});continue
 raw=path.read_bytes()
 if b'source-archive-map.json' not in raw and b'\\u' not in raw:continue
 seen.add(rel);h=sha(raw)
 if pins.get(rel)==h:continue
 try:refs=pairs(json.loads(raw))
 except Exception as e:errors.append({'file':rel,'error':str(e)});continue
 changed.append({'file':rel,'previous_digest':pins.get(rel),'current_digest':h,'relevant_pairs':len(refs)})
 for (target,digest),shapes in refs.items():
  if (rel,target,digest,tuple(sorted(shapes))) not in old:added_refs.append({'document':rel,'target':target,'digest':digest,'shapes':sorted(shapes)})
mutations=[]
for r in plan['mutations']:
 path=root/r['file'];actual=sha(path.read_bytes()) if path.exists() else None
 if actual!=r['before_digest']:mutations.append({'file':r['file'],'before_digest':r['before_digest'],'current_digest':actual})
removed=sorted(set(pins)-seen);result={'pass':not added_refs and not mutations and not errors and not removed,'changed_or_new_documents':changed,'new_relevant_references':added_refs,'mutation_input_drift':mutations,'errors':errors,'removed_indexed_documents':removed,'scope':'Fresh current JSON enumeration plus byte-prefilter/hash comparison against proposal index; recursively parse every changed/new candidate including Unicode-escaped forms. Snapshot/frozen trees and embedded encoded payloads remain excluded as declared. No root map mutation.','checked_at_unix':time.time()};(p/'DRIFT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'changed_or_new':len(changed),'new_relevant':len(added_refs),'mutation_drift':len(mutations),'errors':len(errors),'removed':len(removed)}))
