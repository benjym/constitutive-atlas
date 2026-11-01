"""Complete immutable identity after the bounded pure overlay run."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[5];P=H.parent/'revision-v3'
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
checks=read(P/'CHECK_RESULTS.json');current=read(H/'CHECK_RESULTS.json');plan=read(H/'PLAN.json')
changed=set(read(H/'TRUE_DELTA_MAPS.json')['paths']);drift={r['original_path'] for r in read(H/'DRIFT.json')['inputs']}
composed=[];affected=[]
for row in checks['checks']:
 if row['outcome']!='passed':continue
 side=(Path(row['document']).parent/'source-archive-map.json').as_posix()
 (affected if side in changed or side in drift or row['original_path'] in drift or row['document'] in drift else composed).append(row)
# The one additional outside-write sidecar (Tresca) has no prior passing predicate.
assert len(composed)==current['unchanged_composed_predicates']
assert len(affected)==current['affected_previous_predicates']
for doc in {r['document'] for r in checks['checks'] if r['outcome']=='passed'}|{r['document'] for r in current['checks']}:
 p=H/'receipt-bytes'/doc;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/doc).read_bytes())
save(H/'COMPOSITION_PARTITION.json',dict(composed=composed,affected=affected,unchanged_checker=dict(original_path='atlas/evidence.py',old_sha256=sha((R/'atlas/evidence.py').read_bytes()))))
# Freeze own immutable context plus all exact v3 context files; current guards are separate.
files={r['original_path']:r['old_sha256'] for r in read(P/'SOURCE_FREEZE.json')['files']}
for p in sorted(H.rglob('*')):
 if p.is_file() and p.name!='SOURCE_FREEZE.json':files[p.relative_to(R).as_posix()]=sha(p.read_bytes())
for n,h in files.items():assert sha((R/n).read_bytes())==h,n
save(H/'SOURCE_FREEZE.json',dict(identity='shared-hook-preservation-revision-v4-additive-composition',scope='Prospective metadata preservation only; prior full v3 replay retained, changed resolutions rechecked; no production writes',files=[dict(original_path=n,old_sha256=h) for n,h in sorted(files.items())]))
print(json.dumps({n:sha((H/n).read_bytes()) for n in ['SOURCE_FREEZE.json','PLAN.json','APPLY_WHITELIST.json','CHECK_RESULTS.json','COMPOSITION_PARTITION.json']},indent=2))
