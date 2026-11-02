"""Restore exact declared historical bytes; never relax a replay outcome."""
from pathlib import Path
import ast,collections,difflib,gzip,hashlib,json,os,re,sys
from functools import lru_cache
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CLONE=Path('/private/tmp/atlas-bingham-final-context-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();encode=lambda o:(json.dumps(o,indent=2)+'\n').encode();valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
sys.path.insert(0,str(ROOT));import atlas.evidence as evidence
evidence.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads));checked_receipt=evidence.checked_receipt
source=ast.parse((HERE/'prepare.py').read_text());names={'put','saved','zipped','safe','pairs','outcome','change_map'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(HERE/'prepare.py'),'exec'))
proof=json.loads(gzip.decompress((HERE/'REPLAY.json.gz').read_bytes()));composition=json.loads((HERE/'COMPOSITION.json').read_text());preservation=json.loads((HERE/'PRESERVATION.json').read_text());changes=preservation['maps'];archive_origins=preservation['archive_origins'];inventory=json.loads(gzip.decompress((HERE/'imported-input-inventory.json.gz').read_bytes()));capsules=json.loads((HERE/'SOURCE-CAPSULES.json').read_text());byhash=collections.defaultdict(list)
for n,h in inventory.items():byhash[h].append(ROOT/n)
# Only actual immutable source-capsule locations; never abandoned/private fixtures.
roots=[Path('/private/tmp/atlas-time-profile-v2'),Path('/private/tmp/atlas-bingham-delivery-v1'),Path('/private/tmp/atlas-bingham-release-v2'),Path('/private/tmp/atlas-schedule-predictor-v1')]
def locate(n,h):
 for r in [ROOT,CLONE]+roots:
  for p in [r/'catalogue/source-snapshots'/h/n,r/n]:
   if p.is_file() and sha(p)==h:return p
 for p in byhash[h]:
  if p.is_file() and sha(p)==h:return p
 return None
wanted={(e['original_path'],e['sha256']) for e in proof['failures']}|{(e['path'],e['sha256']) for e in capsules['gaps']}
# Exact capsule subtrees only, rather than recursively reading old release fixtures.
allowed=[]
for r in roots:
 for d in ['execution-v1','execution-v2','execution-v3','execution-v4','execution-v5','generic-predictor-plan-v1','public-profile-v1','interface-v1','interface-v3']:
  p=r/'docs/ingestion/bingham-comsol63'/d
  if p.is_dir():allowed.append(p)
 for d in ['physical-time-v2-profile-v1','physical-time-v2-standalone-v1','schedule-predictor-v1']:
  p=r/'docs/investigations'/d
  if p.is_dir():allowed.append(p)
missing_hashes={h for n,h in wanted if locate(n,h) is None}
for base in allowed:
 for folder,dirs,names_ in os.walk(base):
  dirs[:]=[d for d in dirs if d not in {'consumer-context','regression-context','routing-context','node_modules','__pycache__'} and not d.startswith('.mock')]
  for name in names_:
   p=Path(folder)/name
   if p.is_symlink() or not p.is_file():continue
   h=sha(p)
   if h in missing_hashes:byhash[h].append(p)
restored=[];gaps=[]
requests=[{'document':e['document'],'path':e['original_path'],'sha256':e['sha256'],'reason':'exact context for changed historical failure'} for e in proof['failures']]+[{**e,'reason':'exact historical source-capsule gap'} for e in capsules['gaps']]
for e in requests:
 if outcome(CLONE,e['document'],e['path'],e['sha256'])['ok']:continue
 src=locate(e['path'],e['sha256'])
 if src:
  change_map(e['document'],e['path'],e['sha256'],src,e['reason']);restored.append({**e,'provider':str(src)})
 else:gaps.append(e)
# New map extensions can be reverse-consumed; preserve original passes exactly.
for iteration in range(20):
 count=0
 for e in proof['edges']:
  if not e['before']['ok']:continue
  after=outcome(CLONE,e['document'],e['original_path'],e['sha256'])
  if after['ok'] and after['sha256']==e['sha256']:continue
  count+=change_map(e['document'],e['original_path'],e['sha256'],ROOT/e['before']['resolved'],'preserve passing reverse edge after exact context restoration')
 print({'restoration_round':iteration,'map_extensions':count},flush=True)
 if not count:break
else:raise ValueError('reverse preservation failed to terminate')
summary=collections.Counter();failures=[]
for e in proof['edges']:
 a=outcome(CLONE,e['document'],e['original_path'],e['sha256']);b=e['before'];e['after']=a
 if b['ok']:
  if a['ok'] and a['sha256']==b['sha256']:summary['preserved_pass']+=1
  else:summary['newly_broken']+=1;failures.append(e)
 elif a['ok']:summary['restored_prior_failure']+=1
 elif a==b:summary['retained_failure']+=1
 else:summary['changed_failure']+=1;failures.append(e)
summary.update({'pairs':len(proof['edges']),'documents':len({e['document'] for e in proof['edges']}),'maps_changed':len(changes),'newly_broken':summary['newly_broken'],'changed_failure':summary['changed_failure'],'unresolved_context_requests':len(gaps)})
proposals={}
for n in changes:
 proposals[n]=sha(CLONE/n);before=(ROOT/n).read_text() if (ROOT/n).exists() else '';put(HERE/'diffs'/(n+'.diff'),''.join(difflib.unified_diff(before.splitlines(True),(CLONE/n).read_text().splitlines(True),fromfile='before/'+n,tofile='proposed/'+n)).encode())
for n in archive_origins:proposals[n]=sha(CLONE/n)
for n,h in proposals.items():put(HERE/'preservation-candidates'/n,(CLONE/n).read_bytes())
composition['preservation_files']=proposals;saved('FINAL-COMPOSITION.json',composition);saved('FINAL-PRESERVATION.json',{'maps':changes,'files':proposals,'archive_origins':archive_origins});saved('CONTEXT-RESTORATION.json',{'restored':restored,'gaps':gaps,'allowed_capsule_subtrees':[str(p) for p in allowed]});zipped('FINAL-REPLAY.json.gz',{**proof,'summary':dict(summary),'failures':failures});saved('FINAL-SUMMARY.json',dict(summary));print(json.dumps(dict(summary),indent=2),flush=True)
if failures or gaps:raise SystemExit('Exact historical context gaps retained; do not install')
