"""Prospective full imported-tree receipt preservation. No build/engine/install."""
from pathlib import Path
import ast,collections,difflib,gzip,hashlib,json,os,re,sys,time,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CLONE=Path('/private/tmp/atlas-bingham-final-context-v1')
DRAFT=ROOT/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1';ADMISSION=ROOT/'docs/ingestion/bingham-comsol63/actual-integration-v3-candidates-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encode=lambda o:(json.dumps(o,indent=2)+'\n').encode()
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() or p.is_symlink():p.unlink() # Detach fixture hardlink before any write.
 p.write_bytes(b)
def saved(n,o):put(HERE/n,encode(o))
def zipped(n,o):put(HERE/n,gzip.compress(encode(o),mtime=0))
def safe(n):return isinstance(n,str) and not Path(n).is_absolute() and '..' not in Path(n).parts
valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
# Reuse accepted scanner owner-context classification, do not execute draft authoring.
tree=ast.parse((DRAFT/'audit_preservation.py').read_text())
EXCLUDED=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='excluded' for t in n.targets))
EXCLUDED|={'final-imported-context-v1','actual-integration-v3-candidates-v1','qualified-engine-candidate-v5','qualified-engine-evidence-v5','package-inputs-v3-preparation-v1'}
def excluded(n):return sorted(set(Path(n).parts)&EXCLUDED | {x for x in Path(n).parts if re.fullmatch(r'prior-v\d+',x)})
def pairs(node):
 if isinstance(node,dict):
  for k,v in node.items():
   if valid(v) and ('/' in k or '.' in k or (ROOT/k).is_file()):yield k,v
  if isinstance(node.get('path'),str):
   for k in ['sha256','hash']:
    if valid(node.get(k)):yield node['path'],node[k]
  for v in node.values():yield from pairs(v)
 elif isinstance(node,list):
  for v in node:yield from pairs(v)
PRUNE={'.git','.local','__pycache__','node_modules','consumer-context','routing-context','regression-context','final-imported-context-v1'}
def files(root):
 for folder,dirs,names in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in PRUNE and not d.startswith('.mock-') and not d.startswith('build-') and not d.startswith('.venv'))
  for name in sorted(names):
   p=Path(folder)/name
   if not p.is_symlink() and p.is_file() and p.suffix not in {'.pyc'}:yield p
assert CLONE.is_dir() and (HERE/'imported-input-inventory.json.gz').is_file()
inventory=json.loads(gzip.decompress((HERE/'imported-input-inventory.json.gz').read_bytes()))
composition=json.loads((DRAFT/'COMPOSITION.json').read_text());receipt=json.loads((ADMISSION/'RECEIPT.json').read_text());selected={};sources={}
for folder,key in [('candidates','candidate_files'),('preservation-candidates','preservation_files')]:
 for n,h in composition[key].items():
  p=DRAFT/folder/n;assert sha(p)==h,(n,h);selected[n]=h;sources[n]=str(p)
for n,h in receipt['outputs'].items():
 p=ADMISSION/n;assert sha(p)==h
 if n in selected:assert selected[n]==h
 selected[n]=h;sources[n]=str(p)
tracking=ROOT/'docs/ingestion/bingham-comsol63/release-tracking-v3-preparation-v1'
tracking_manifest=json.loads((tracking/'MANIFEST.json').read_text())
for n,h in tracking_manifest['candidate_files'].items():
 assert sha(ROOT/n)==tracking_manifest['inputs'][n]
 source=tracking/'candidates'/n;assert sha(source)==h
 selected[n]=h;sources[n]=str(source)
for n,h in selected.items():put(CLONE/n,Path(sources[n]).read_bytes())
sys.path.insert(0,str(ROOT))
import atlas.evidence as evidence
from functools import lru_cache
from types import SimpleNamespace
# Pure memoization of exact immutable JSON text; original resolver logic is unchanged.
evidence.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review
review='catalogue/agent-reviews/bingham-comsol63-agent-v1.json';assert sha(ROOT/review)=='61022026949f2ce9b9a536ab564239edd97ac0b5b3ba66f4ffe3f0066aa6b836'
def outcome(root,d,n,h):
 try:
  p=checked_receipt(root,d,n,h);return {'ok':True,'resolved':p.relative_to(root).as_posix(),'sha256':sha(p)}
 except Exception as e:return {'ok':False,'error_type':type(e).__name__,'error':str(e).replace(str(root),'<ROOT>')}
documents={};excluded_docs={};edges=[];catalogue={}
command=['rg','-l','-F','-g','*.json']
for token in sorted(set(selected)|{'source-archive-map.json'}):command+=['-e',token]
command+=['catalogue','docs','schemas','tests','tools']
search=subprocess.run(command,cwd=ROOT,text=True,capture_output=True);assert search.returncode in [0,1],search.stderr
prefilter=set(search.stdout.splitlines())
prefilter|={n for n in inventory if n.startswith(('docs/ingestion/bingham-comsol63/','docs/investigations/physical-time-v2-')) and n.endswith('.json')}
saved('DISCOVERY.json',{'method':'Exact path-string prefilter plus every imported Bingham/physical-time JSON; recursive parent-map reverse closure thereafter','candidate_paths':sorted(selected),'selected_json_paths':sorted(prefilter),'reason':'Path-string prefilter is conservative. Actual discovery requires exact original path AND current ROOT before SHA. Any prior pass at another hash necessarily resolves an unchanged archive; existing failures at other hashes cannot become newly broken. Reverse links use each old map before SHA. All immediate siblings of selected parents are then loaded explicitly.'})
print('path-prefilter candidates',len(prefilter),flush=True)
for n in inventory:
 if n not in prefilter:continue
 if not n.endswith('.json') or n.endswith('/source-archive-map.json'):continue
 ex=excluded(n)
 if ex:excluded_docs[n]=ex;continue
 try:found=sorted(set(pairs(json.loads((ROOT/n).read_text()))))
 except (UnicodeError,json.JSONDecodeError,FileNotFoundError):continue
 if found:catalogue[n]=found
# Accepted discovery pattern: all changed-path consumers, all their sibling
# receipt documents, reverse sidecar consumers, plus every newly imported
# Bingham and physical-time source context. Unrelated stock siblings are not
# a new numerical campaign.
live_targets={n:sha(ROOT/n) for n in selected if (ROOT/n).is_file() and sha(ROOT/n)!=selected[n]}
parents={Path(n).parent.as_posix() for n,found in catalogue.items() if any(path in live_targets and live_targets[path]==h for path,h in found)}
parents|={Path(n).parent.as_posix() for n in catalogue if n.startswith(('docs/ingestion/bingham-comsol63/','docs/investigations/physical-time-v2-'))}
parents.add('catalogue/agent-reviews')
for iteration in range(20):
 maps={parent+'/source-archive-map.json':sha(ROOT/parent/'source-archive-map.json') for parent in parents if (ROOT/parent/'source-archive-map.json').is_file()}
 expanded=parents|{Path(n).parent.as_posix() for n,found in catalogue.items() if any(path in maps and maps[path]==h for path,h in found)}
 if expanded==parents:break
 parents=expanded
else:raise ValueError('Consumer discovery did not terminate')
# Every immediate sibling is loaded, including documents with no target tokens.
sibling_inventory={}
for parent in sorted(parents):
 for document in (ROOT/parent).glob('*.json'):
  n=document.relative_to(ROOT).as_posix()
  if document.name=='source-archive-map.json':continue
  sibling_inventory[n]=sha(document)
  catalogue[n]=sorted(set(pairs(json.loads(document.read_text()))))
saved('SIBLINGS.json',{'parent_contexts':sorted(parents),'documents':sibling_inventory,'exact_current_target_hashes':live_targets,'reverse_maps_before_hashes':maps})
for n,found in catalogue.items():
 if Path(n).parent.as_posix() not in parents:continue
 documents[n]=inventory[n]
 for path,h in found:edges.append({'document':n,'original_path':path,'sha256':h,'before':outcome(ROOT,n,path,h)})
print(json.dumps({'input_files':len(inventory),'active_receipt_documents':len(documents),'recognized_pairs':len(edges),'excluded_copied_namespace_json':len(excluded_docs)}),flush=True)
# Additive maps only. Existing document pins/entries are never replaced.
changes={};archive_origins={};sourced=[]
def change_map(doc,path=None,h=None,source=None,reason='preservation'):
 n=(Path(doc).parent/'source-archive-map.json').as_posix();live=CLONE/n
 old=json.loads(live.read_text()) if live.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 new=json.loads(json.dumps(old))
 for sibling in live.parent.glob('*.json'):
  sn=sibling.relative_to(CLONE).as_posix()
  if sibling.name!='source-archive-map.json' and sn not in new['documents']:new['documents'][sn]=sha(sibling)
 if path is not None:
  archived='catalogue/source-snapshots/'+h+'/'+path;entry={'original_path':path,'sha256':h,'archived_path':archived}
  found=[x for x in new['entries'] if x.get('original_path')==path and x.get('sha256')==h]
  if found:assert found==[entry],(doc,path,'conflicting original map')
  else:new['entries'].append(entry)
  ap=CLONE/archived
  if ap.exists():assert sha(ap)==h
  else:
   assert source is not None and sha(source)==h,(path,h,source)
   put(ap,source.read_bytes());archive_origins[archived]={'source':str(source),'sha256':h,'reason':reason}
 if new==old:return False
 if n not in changes:
  original=ROOT/n
  changes[n]={'before_sha256':sha(original) if original.exists() else None,'reasons':[]}
  if original.exists():
   archived='catalogue/source-snapshots/'+sha(original)+'/'+n
   put(CLONE/archived,original.read_bytes());archive_origins[archived]={'source':str(original),'sha256':sha(original),'reason':'immutable previous sidecar bytes'}
 changes[n]['reasons'].append({'document':doc,'path':path,'sha256':h,'reason':reason})
 put(live,encode(new));return True
# Canonical actual E5 document must be explicitly recognized by its sibling sidecar.
change_map(review,reason='actual canonical accepted Bingham E5 document')
# Restore only declared source-capsule records, using exact known source bytes.
PROVIDERS=[Path('/private/tmp/atlas-time-profile-v2'),Path('/private/tmp/atlas-bingham-delivery-v1'),Path('/private/tmp/atlas-bingham-release-v2')]
def provider(path,h):
 for candidate in [ROOT/'catalogue/source-snapshots'/h/path,CLONE/'catalogue/source-snapshots'/h/path]+[r/path for r in PROVIDERS]:
  if candidate.is_file() and sha(candidate)==h:return candidate
 return None
capsule_docs=[];capsule_gaps=[]
for d in documents:
 if not (d.startswith('docs/ingestion/bingham-comsol63/execution-') or d.startswith('docs/investigations/physical-time-v2-')):continue
 if not (Path(d).name.startswith(('freeze','FREEZE','source-bindings'))):continue
 capsule_docs.append(d)
 for n,h in sorted(set(pairs(json.loads((ROOT/d).read_text())))):
  if not safe(n) or not (n=='CMakeLists.txt' or n.startswith(('atlas/','cpp/','schemas/','cmake/','runtimes/','tests/','tools/','models/','docs/'))):continue
  if outcome(CLONE,d,n,h)['ok']:continue
  src=provider(n,h)
  if src:
   change_map(d,n,h,src,'source capsule exact-byte restoration');sourced.append({'document':d,'path':n,'sha256':h,'provider':str(src)})
  else:capsule_gaps.append({'document':d,'path':n,'sha256':h})
# Replay every active original consumer; repair only original passes using its
# actual resolved immutable bytes. Iterate for reverse edges to changed sidecars.
rounds=[]
for iteration in range(20):
 repaired=0
 for e in edges:
  if not e['before']['ok']:continue
  d,n,h=e['document'],e['original_path'],e['sha256'];after=outcome(CLONE,d,n,h)
  if after['ok'] and after['sha256']==h:continue
  if not safe(n):raise ValueError(('unsafe original passing edge',e))
  src=ROOT/e['before']['resolved'];repaired+=change_map(d,n,h,src,'preserve previously passing edge')
 rounds.append({'iteration':iteration,'map_extensions':repaired});print(rounds[-1],flush=True)
 if repaired==0:break
else:raise ValueError('Reverse closure failed to terminate')
summary=collections.Counter();failures=[]
for e in edges:
 a=outcome(CLONE,e['document'],e['original_path'],e['sha256']);b=e['before'];e['after']=a
 if b['ok']:
  if a['ok'] and a['sha256']==b['sha256']:summary['preserved_pass']+=1
  else:summary['newly_broken']+=1;failures.append(e)
 elif a['ok']:summary['restored_prior_failure']+=1
 elif a==b:summary['retained_failure']+=1
 else:summary['changed_failure']+=1;failures.append(e)
summary.update({'pairs':len(edges),'documents':len(documents),'maps_changed':len(changes),'source_capsule_restorations':len(sourced),'source_capsule_gaps':len(capsule_gaps),'newly_broken':summary['newly_broken'],'changed_failure':summary['changed_failure']})
zipped('REPLAY.json.gz',{'summary':dict(summary),'edges':edges,'failures':failures,'rounds':rounds,'excluded_copied_namespaces':excluded_docs,'exclusion_parts':sorted(EXCLUDED)})
saved('SOURCE-CAPSULES.json',{'documents':capsule_docs,'restored':sourced,'gaps':capsule_gaps})
# Every new/changed map and every selected old-byte archive is a proposal, not install.
proposals={}
for n in changes:
 proposals[n]=sha(CLONE/n)
 before=(ROOT/n).read_text() if (ROOT/n).exists() else ''
 put(HERE/'diffs'/(n+'.diff'),''.join(difflib.unified_diff(before.splitlines(True),(CLONE/n).read_text().splitlines(True),fromfile='before/'+n,tofile='proposed/'+n)).encode())
for n in archive_origins:proposals[n]=sha(CLONE/n)
for n,h in proposals.items():put(HERE/'preservation-candidates'/n,(CLONE/n).read_bytes())
saved('PRESERVATION.json',{'maps':changes,'files':proposals,'archive_origins':archive_origins})
saved('COMPOSITION.json',{'selected_nonpreservation_count':len(set(selected)-set(composition['preservation_files'])),'tracking_manifest':{'path':str(tracking/'MANIFEST.json'),'sha256':sha(tracking/'MANIFEST.json')},'selected_source_and_admission_files':selected,'selected_file_sources':sources,'preservation_files':proposals,'private_context':str(CLONE),'source_root':str(ROOT),'installed':False,'compiled_calls':0})
saved('SUMMARY.json',dict(summary));print(json.dumps(dict(summary),indent=2),flush=True)
# Normal scientific envelope validation is separate from receipt pair enumeration.
try:
 v=validate_review(CLONE/review,root=CLONE,for_approval=True);check={'passed':True,'artifacts':len(v['artifacts'])}
except Exception as e:check={'passed':False,'error_type':type(e).__name__,'error':str(e)}
saved('E5-VALIDATION.json',check);print('E5',check,flush=True)
zipped('prospective-context-inventory.json.gz',{p.relative_to(CLONE).as_posix():sha(p) for p in files(CLONE)})
if failures:raise SystemExit('Replay differences retained; do not install')
