"""Bounded exact-Git delta/reused closure audit; no root edits/build/backend calls."""
from pathlib import Path,PurePosixPath
import subprocess,json,hashlib,importlib.util
D=Path(__file__).resolve().parent;V2=D.parent/'release-bindings-v2';BASE='95210701c73718500ca41d0eb70a8281c585b1a3';OLD='ec47f3e47b41d01a51c0cd1ef0bfecb344def694';PRIOR='3873a48b256ed37cbc78378ee6b41d73139676f8'
sha=lambda b:hashlib.sha256(b).hexdigest();git=lambda *a:subprocess.check_output(['git',*a]);blob=lambda p,base=BASE:git('show',base+':'+p)
spec=importlib.util.spec_from_file_location('prior_rules','docs/ingestion/manzari-dafalias-1997/delivery-v1/release-bindings-v1/audit.py');rules=importlib.util.module_from_spec(spec);spec.loader.exec_module(rules)
prior=json.loads((V2/'audit.json').read_text());plan=json.loads((V2/'archive-plan.json').read_text());consumers=json.loads((V2/'consumer-inputs.json').read_text())
tree={}
for line in git('ls-tree','-rlz',BASE).split(b'\0'):
 if not line:continue
 meta,path=line.split(b'\t',1);mode,kind,oid,size=meta.decode().split()
 if kind=='blob':tree[path.decode()]={'oid':oid,'bytes':int(size)}
delta=git('diff','--name-status',OLD,BASE).decode().splitlines();changed=[x.split('\t')[-1]for x in delta]
seed=['cpp/include/atlas/solver.hpp','tests/test_solver.cpp','tools/check_native_fixture_contracts.py','.github/workflows/verify.yml','catalogue/approved-models.json','catalogue/laboratory-package-policy.json','catalogue/laboratory-profile-policy.json']
reviews=['catalogue/agent-reviews/'+n+'-agent-v1.json'for n in ['hypoplastic-clay-2013','igs97','vw96','ramberg-osgood']]
selected=set(seed+reviews+list(consumers['files']))
selected.update(a[k]for a in prior['direct_and_sidecar_closure']for k in ['document','sidecar']if a[k]in tree)
skips=[]
for p in changed:
 if not p.endswith('.json'):continue
 if set(PurePosixPath(p).parts[:-1])&rules.SKIP or PurePosixPath(p).parts.count('docs')>1 or PurePosixPath(p).parts.count('catalogue')>1:skips.append({'path':p,'reason':'nested-copy-or-snapshot'});continue
 if tree.get(p,{}).get('bytes',0)>2_000_000:skips.append({'path':p,'reason':'over-2MB'});continue
 if p in tree:selected.add(p)
cache={}
def get(p):
 if p not in cache:cache[p]=blob(p)
 return cache[p]
# Exact changed review artifacts, registry direct support, plus JSON source receipts
# already selected. No recursive traversal of unrelated historical snapshots.
for rp in reviews:
 r=json.loads(get(rp));selected.add(r['model']['path']);selected.update(a['path']for a in r['artifacts']if a['path'].endswith('.json')and a['path']in tree)
parsed={}
for p in sorted(selected):
 if p in tree and p.endswith('.json'):
  try:parsed[p]=json.loads(get(p))
  except (ValueError,UnicodeDecodeError):pass
edges=[dict(document=p,original_path=q,sha256=h,locator=l)for p,v in parsed.items()for q,h,l in rules.pairs(v)if q in tree]
# Reuse bounded original reverse closure consumers and changed documents only.
mutating=set(seed);pending=list(seed);actions=[];seen=set()
while pending:
 target=pending.pop();h=sha(get(target))
 for e in edges:
  if e['original_path']!=target or e['sha256']!=h:continue
  key=(e['document'],target,h)
  if key in seen:continue
  seen.add(key);doc=e['document'];side=str(PurePosixPath(doc).parent/'source-archive-map.json');mapping=parsed.get(side)
  if mapping is None and side in tree:
   mapping=json.loads(get(side));parsed[side]=mapping
  mapping=mapping or {};canonical='catalogue/source-snapshots/'+h+'/'+target
  matches=[x for x in mapping.get('entries',[])if isinstance(x,dict)and x.get('original_path')==target and x.get('sha256')==h]
  mapped=len(matches)==1 and matches[0].get('archived_path')==canonical;pin=mapping.get('documents',{}).get(doc)==sha(get(doc));archive=canonical in tree and sha(get(canonical))==h
  item={**e,'document_sha256':sha(get(doc)),'sidecar':side,'sidecar_exists':side in tree,'document_pin':pin,'exact_entry':mapped,'canonical_archive':canonical,'archive_verified':archive,'requires_map_change':not(pin and mapped),'metadata_only':doc.endswith('/source-archive-map.json')};actions.append(item)
  if not item['metadata_only']and item['requires_map_change']and side in tree and side not in mutating:mutating.add(side);pending.append(side)
# Exact four current reviews and registry correspondence; raw vs archived resolution.
registry=json.loads(get('catalogue/approved-models.json'));approval_list=registry.get('approvals',registry.get('models',[]))
reviewchecks=[]
for rp in reviews:
 r=json.loads(get(rp));items=[]
 for a in [r['model']]+r['artifacts']:
  p,h=a['path'],a['sha256'];live=p in tree and sha(get(p))==h;canonical='catalogue/source-snapshots/'+h+'/'+p
  side=str(PurePosixPath(rp).parent/'source-archive-map.json');mp=json.loads(get(side))if side in tree else{};docpin=mp.get('documents',{}).get(rp)==sha(get(rp));matches=[x for x in mp.get('entries',[])if x.get('original_path')==p and x.get('sha256')==h];mapped=docpin and len(matches)==1 and matches[0].get('archived_path')==canonical and canonical in tree and sha(get(canonical))==h
  items.append(dict(path=p,sha256=h,live_match=live,canonical_verified=canonical in tree and sha(get(canonical))==h,review_sidecar_resolves=mapped,consumer_resolution='live'if live else'checked_receipt'if mapped else'UNRESOLVED'))
 entries=[x for x in approval_list if x.get('review',{}).get('path')==rp]
 reviewchecks.append(dict(path=rp,sha256=sha(get(rp)),definition=r['model'],items=items,registry_entries=len(entries),registry_exact=bool(entries)and all(x['review']['sha256']==sha(get(rp))and x['definition']=={k:r['model'][k]for k in ['path','sha256']} and x['model_id']==r['model']['id']for x in entries)))
# Current snapshots are documentary only, never canonical installation.
snapshot_paths=set(seed+reviews+['atlas/agent_review.py','atlas/evidence.py','atlas/review_export.py','tools/build_web.py','tools/build_evidence.py','tools/laboratory_profile_policy.mjs'])
for rp in reviews:snapshot_paths.add(json.loads(get(rp))['model']['path'])
for p in sorted(snapshot_paths):
 q=D/'published-bytes'/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(get(p))
oldtargets=[]
for x in plan['canonical_old_bytes']:
 c=x['canonical_archive'];available=c in tree and sha(get(c))==x['sha256'];oldtargets.append({**x,'latest_canonical_verified':available,'latest_live_match':x['original_path']in tree and sha(get(x['original_path']))==x['sha256']})
canonical={}
sidecars={}
for a in actions:
 if a['metadata_only']or not a['requires_map_change']:continue
 key=(a['original_path'],a['sha256']);canonical[key]=dict(original_path=key[0],sha256=key[1],canonical_archive=a['canonical_archive'],already_verified=a['archive_verified'],git_source=BASE+':'+key[0])
 g=sidecars.setdefault(a['sidecar'],dict(exists=a['sidecar_exists'],documents={},entries=[]));g['documents'][a['document']]=a['document_sha256'];entry=dict(original_path=a['original_path'],sha256=a['sha256'],archived_path=a['canonical_archive'])
 if entry not in g['entries']:g['entries'].append(entry)
critical=seed+['tools/build_evidence.py','tools/laboratory_profile_policy.mjs','atlas/agent_review.py','atlas/evidence.py','tools/build_web.py','atlas/compiler.py','schemas/model-v0.3.schema.json','cpp/include/atlas/solver.hpp']+list(consumers['files'])
critical=list(dict.fromkeys(critical));identity={p:dict(sha256=sha(get(p)),same_as_ec47=get(p)==blob(p,OLD),same_as_3873=get(p)==blob(p,PRIOR))for p in critical if p in tree}
patched_path=Path('/private/tmp/atlas-control-partition-v1/source/cpp/include/atlas/solver.hpp');patched=dict(path=str(patched_path),sha256=sha(patched_path.read_bytes()),source_freeze_sha256=sha(Path('docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json').read_bytes()))
report=dict(patched_solver=patched,identity='md1997-latest-release-bindings-v3',base=BASE,delta_base=OLD,prior_audit=PRIOR,tracked_inventory=len(tree),delta_paths=delta,selected_json_documents=len(parsed),selected_paths=sorted(selected),skips=skips,review_checks=reviewchecks,direct_and_reverse_actions=actions,older_target_pins=[e for e in edges if e['original_path']in seed and e['sha256']!=sha(get(e['original_path']))],critical_consumers=identity,prior23_archive_refresh=oldtargets,scope='Bounded changed JSON + prior exact closure + four review JSON artifacts. Not exhaustive reverse closure; final integration inventory mandatory.',compiled_calls=0)
(D/'audit.json').write_text(json.dumps(report,indent=2)+'\n');(D/'archive-plan.json').write_text(json.dumps(dict(identity='md1997-latest-prospective-preservation-plan-v3',base=BASE,canonical_candidates=list(canonical.values()),sidecar_candidates=sidecars,limits=['Candidate paths only; classify actual consumers before installation.','No live/root maps or archives installed.','Fresh Maxwell/NorSand current qualification remains mandatory.','Old immutable receipts/expected hashes must not be repinned.','Bounded audit cannot replace final integration reinventory.']),indent=2)+'\n')
(D/'inputs.json').write_text(json.dumps({str(p):sha(p.read_bytes())for p in [V2/'manifest.json',V2/'audit.json',V2/'archive-plan.json',V2/'consumer-inputs.json',Path(rules.__file__)]},indent=2)+'\n')
print(json.dumps(dict(json_documents=len(parsed),actions=len(actions),canonical_candidates=len(canonical),sidecar_candidates=len(sidecars),review_items=sum(len(r['items'])for r in reviewchecks),unresolved=sum(i['consumer_resolution']=='UNRESOLVED'for r in reviewchecks for i in r['items']),prior23_verified=sum(x['latest_canonical_verified']for x in oldtargets),compiled_calls=0)))
