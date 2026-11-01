from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[5];P=H.parent/'revision-v4';sha=lambda b:hashlib.sha256(b).hexdigest()
files={r['original_path']:r['old_sha256'] for r in json.loads((P/'SOURCE_FREEZE.json').read_bytes())['files']}
files[(P/'SOURCE_FREEZE.json').relative_to(R).as_posix()]=sha((P/'SOURCE_FREEZE.json').read_bytes())
for p in H.rglob('*'):
 if p.is_file() and p.name!='SOURCE_FREEZE.json':files[p.relative_to(R).as_posix()]=sha(p.read_bytes())
for n,h in files.items():assert sha((R/n).read_bytes())==h,n
(H/'SOURCE_FREEZE.json').write_text(json.dumps(dict(identity='shared-hook-preservation-revision-v5-chart-consumer-supplement',scope='Nonmutating final metadata proposal; v3/v4 proofs retained unchanged',files=[dict(original_path=n,old_sha256=h) for n,h in sorted(files.items())]),indent=2)+'\n')
print(json.dumps({n:sha((H/n).read_bytes()) for n in ['SOURCE_FREEZE.json','PLAN.json','APPLY_WHITELIST.json','CHECK_RESULTS.json','COMPOSITION_PARTITION.json']},indent=2))
