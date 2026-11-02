"""Metadata-only selection diagnostic plus bounded committed JSON reads; no hashes/build."""
from pathlib import Path
import subprocess,json,collections,time
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');HERE=Path(__file__).resolve().parent;WORK=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v3');REV='4e60096f3ab4535c53fd48ee92acb094b5682f4d';PARENTS=['106a9cf8c327c9c262a97eb86aa04dae3f6cadb8','136636f14ce12b0dd83e65a8c37d3af9a5cc1381'];MAX_JSON=4*1024*1024
PREFIXES=('tools/','atlas/','web/','models/','schemas/','cpp/','catalogue/','data/','docs/models/','docs/benchmarks/','docs/capabilities/','docs/development/')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
tracked={}
for entry in git('ls-tree','-r','-z',REV).split(b'\0'):
 if entry:
  meta,name=entry.split(b'\t');mode,kind,oid=meta.decode().split();assert kind=='blob';tracked[name.decode()]={'mode':mode,'git_blob':oid}
ids=sorted({v['git_blob'] for v in tracked.values()});meta=subprocess.run(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=''.join(i+'\n' for i in ids).encode(),cwd=ROOT,stdout=subprocess.PIPE,check=True).stdout.decode();sizes={}
for line in meta.splitlines():oid,kind,size=line.split();assert kind=='blob';sizes[oid]=int(size)
reasons=collections.defaultdict(list);delta=set()
for parent in PARENTS:
 for n in git('diff-tree','-r','--no-commit-id','--name-only','-z',parent,REV).split(b'\0'):
  if n:
   name=n.decode();delta.add(name)
   if name in tracked:reasons[name].append({'kind':'branch-delta','parent':parent})
for n in tracked:
 if n.startswith(PREFIXES) and not n.startswith('catalogue/source-snapshots/') and '/dist/' not in n and '/preview/' not in n:reasons[n].append({'kind':'runtime-prefix'})
for n in ['CMakeLists.txt','pyproject.toml','requirements.txt','requirements-dev.txt']:
 if n in tracked:reasons[n].append({'kind':'root-source'})
initial=set(reasons)
def summary(names):
 groups=collections.Counter();extensions=collections.Counter()
 for n in names:
  size=sizes[tracked[n]['git_blob']];parts=n.split('/');groups['/'.join(parts[:3])]+=size;extensions[Path(n).suffix]+=size
 return {'files':len(names),'logical_bytes':sum(sizes[tracked[n]['git_blob']] for n in names),'groups_top20':groups.most_common(20),'extensions_top12':extensions.most_common(12)}
(HERE/'initial-prefix-metadata.json').write_text(json.dumps(summary(initial),indent=2)+'\n')
def references(value):
 if isinstance(value,dict):
  if any(isinstance(value.get(k),str) and len(value[k])==64 for k in ['sha256','hash']):
   for field in ['path','original_path','archived_path']:
    if isinstance(value.get(field),str):yield value[field]
  for k,v in value.items():
   if isinstance(k,str) and '/' in k and isinstance(v,str) and len(v)==64:yield k
   yield from references(v)
 elif isinstance(value,list):
  for item in value:yield from references(item)
parsed=set();cache={};large=[]
while True:
 queue=sorted(n for n in set(reasons)-parsed if n.endswith('.json'))
 if not queue:break
 for n in queue:
  parsed.add(n);oid=tracked[n]['git_blob'];size=sizes[oid]
  if size>MAX_JSON:large.append({'path':n,'git_blob':oid,'bytes':size});continue
  if oid not in cache:
   try:cache[oid]=sorted(set(references(json.loads(git('cat-file','blob',oid)))))
   except (UnicodeError,json.JSONDecodeError):cache[oid]=[]
  for target in cache[oid]:
   if target in tracked and target not in reasons:reasons[target].append({'kind':'recursive-json-hash-reference','document':n})
rows=[]
for n in sorted(reasons):rows.append({'path':n,**tracked[n],'bytes':sizes[tracked[n]['git_blob']],'actual_stat_bytes':(WORK/n).stat().st_size,'reasons':reasons[n]})
selected={r['path'] for r in rows};total=sum(r['bytes'] for r in rows);actual_total=sum(r['actual_stat_bytes'] for r in rows);unique={r['git_blob']:r['bytes'] for r in rows};report={'status':'bounded metadata diagnostic; no actual file hash/freeze','revision':REV,'parents':PARENTS,'initial':summary(initial),'selected':summary(selected),'unique_git_blobs':len(unique),'unique_git_blob_bytes':sum(unique.values()),'actual_stat_bytes_total':actual_total,'target_v4_failure_total':2904465794,'exact_failed_total_reproduced':actual_total==2904465794,'large_json_not_read':large,'max_single_json_read_bytes':MAX_JSON,'unique_json_blobs_read':len(cache),'recursive_added_paths':len(selected-initial),'largest_files':sorted(rows,key=lambda r:r['bytes'],reverse=True)[:30],'all_target_sizes_equal_actual_stat':all(r['bytes']==r['actual_stat_bytes'] for r in rows),'selection_complete':not large,'no_whole_byte_hash_or_copy_or_execution':True}
(HERE/'selection-paths.json').write_text(json.dumps({'revision':REV,'entries':rows},indent=2)+'\n');(HERE/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['initial','selected','unique_git_blobs','unique_git_blob_bytes','recursive_added_paths','exact_failed_total_reproduced','large_json_not_read','selection_complete']},indent=2))
