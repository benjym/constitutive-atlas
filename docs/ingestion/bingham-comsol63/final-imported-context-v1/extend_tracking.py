"""Add final coordinator tracking candidates to the completed original replay."""
from pathlib import Path
import ast,collections,difflib,gzip,hashlib,json,re,subprocess,sys
from functools import lru_cache
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CLONE=Path('/private/tmp/atlas-bingham-final-context-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();encode=lambda o:(json.dumps(o,indent=2)+'\n').encode();valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
sys.path.insert(0,str(ROOT));import atlas.evidence as evidence
evidence.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads));checked_receipt=evidence.checked_receipt
# Reuse the identical bounded preparation functions; do not execute its driver.
source=ast.parse((HERE/'prepare.py').read_text());names={'put','saved','zipped','safe','pairs','outcome','change_map','excluded'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(HERE/'prepare.py'),'exec'))
old=json.loads(gzip.decompress((HERE/'REPLAY.json.gz').read_bytes()));composition=json.loads((HERE/'COMPOSITION.json').read_text());preservation=json.loads((HERE/'PRESERVATION.json').read_text());changes=preservation['maps'];archive_origins=preservation['archive_origins'];EXCLUDED=set(old['exclusion_parts']);edges=old['edges'];seen={(e['document'],e['original_path'],e['sha256']) for e in edges}
tracking=ROOT/'docs/ingestion/bingham-comsol63/release-tracking-v3-preparation-v1';manifest=json.loads((tracking/'MANIFEST.json').read_text());assert set(manifest['candidate_files'])=={'docs/STATUS.md','ROADMAP.md','IMPLEMENTATION_PLAN.md'}
for n,h in manifest['candidate_files'].items():
 assert sha(ROOT/n)==manifest['inputs'][n];src=tracking/'candidates'/n;assert sha(src)==h;put(CLONE/n,src.read_bytes());composition['selected_source_and_admission_files'][n]=h;composition['selected_file_sources'][n]=str(src)
# New direct consumers and recursive consumers of their sibling maps. Existing
# discovery already includes all map-path mentions; use exact path tokens.
parents=set();scanned=set();discovered=[]
active=set(manifest['candidate_files'])
for iteration in range(20):
 command=['rg','-l','-F','-g','*.json']
 for token in sorted(active):command+=['-e',token]
 command+=['catalogue','docs','schemas','tests','tools'];run=subprocess.run(command,cwd=ROOT,text=True,capture_output=True);assert run.returncode in [0,1]
 newparents=set()
 for n in run.stdout.splitlines():
  if excluded(n) or n.endswith('/source-archive-map.json'):continue
  try:found=sorted(set(pairs(json.loads((ROOT/n).read_text()))))
  except (UnicodeError,json.JSONDecodeError):continue
  if any(path in active for path,h in found):newparents.add(Path(n).parent.as_posix())
 newparents-=parents
 if not newparents:break
 parents|=newparents
 for parent in sorted(newparents):
  for document in (ROOT/parent).glob('*.json'):
   d=document.relative_to(ROOT).as_posix()
   if document.name=='source-archive-map.json':continue
   for n,h in sorted(set(pairs(json.loads(document.read_text())))):
    key=(d,n,h)
    if key not in seen:edges.append({'document':d,'original_path':n,'sha256':h,'before':outcome(ROOT,d,n,h)});seen.add(key)
 active={p+'/source-archive-map.json' for p in newparents};discovered.append({'iteration':iteration,'new_parent_contexts':sorted(newparents)})
else:raise ValueError('tracking closure did not terminate')
for iteration in range(20):
 repaired=0
 for e in edges:
  if not e['before']['ok']:continue
  after=outcome(CLONE,e['document'],e['original_path'],e['sha256'])
  if after['ok'] and after['sha256']==e['sha256']:continue
  repaired+=change_map(e['document'],e['original_path'],e['sha256'],ROOT/e['before']['resolved'],'preserve original passing edge after final tracking candidates')
 print({'tracking_round':iteration,'map_extensions':repaired},flush=True)
 if not repaired:break
else:raise ValueError('tracking preservation did not terminate')
summary=collections.Counter();failures=[]
for e in edges:
 a=outcome(CLONE,e['document'],e['original_path'],e['sha256']);b=e['before'];e['after']=a
 if b['ok']:
  if a['ok'] and a['sha256']==b['sha256']:summary['preserved_pass']+=1
  else:summary['newly_broken']+=1;failures.append(e)
 elif a['ok']:summary['restored_prior_failure']+=1
 elif a==b:summary['retained_failure']+=1
 else:summary['changed_failure']+=1;failures.append(e)
summary.update({'pairs':len(edges),'documents':len({e['document'] for e in edges}),'maps_changed':len(changes),'newly_broken':summary['newly_broken'],'changed_failure':summary['changed_failure']})
proposals={}
for n in changes:
 proposals[n]=sha(CLONE/n);before=(ROOT/n).read_text() if (ROOT/n).exists() else '';put(HERE/'diffs'/(n+'.diff'),''.join(difflib.unified_diff(before.splitlines(True),(CLONE/n).read_text().splitlines(True),fromfile='before/'+n,tofile='proposed/'+n)).encode())
for n in archive_origins:proposals[n]=sha(CLONE/n)
for n,h in proposals.items():put(HERE/'preservation-candidates'/n,(CLONE/n).read_bytes())
composition['preservation_files']=proposals;composition['tracking_manifest']={'path':str(tracking/'MANIFEST.json'),'sha256':sha(tracking/'MANIFEST.json')};composition['selected_nonpreservation_count']=len(set(composition['selected_source_and_admission_files'])-set(json.loads((ROOT/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/COMPOSITION.json').read_text())['preservation_files']))
zipped('FINAL-REPLAY.json.gz',{'summary':dict(summary),'edges':edges,'failures':failures,'tracking_discovery':discovered,'prior_replay':sha(HERE/'REPLAY.json.gz'),'scope':'Original final imported replay plus exact final coordinator tracking additions; no numerical gates changed.'});saved('FINAL-SUMMARY.json',dict(summary));saved('FINAL-PRESERVATION.json',{'maps':changes,'files':proposals,'archive_origins':archive_origins});saved('FINAL-COMPOSITION.json',composition)
print(json.dumps({'summary':dict(summary),'source_admission_tracking_count':composition['selected_nonpreservation_count']},indent=2))
if failures:raise SystemExit('Final replay differences retained; do not install')
