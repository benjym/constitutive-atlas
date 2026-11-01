"""Use the normal benchmark consumer on an exact retained package; no solver calls."""
from pathlib import Path
import hashlib, json, shutil, sys
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from tools.build_benchmark import bundle
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=ROOT/'.local/private-evidence/ordinary-model-deeplinks-v1/site-v1'
manifest=read(ROOT/'docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json')['files']
assert {str(p.relative_to(baseline)) for p in baseline.rglob('*') if p.is_file()} == set(manifest)
for name,row in manifest.items():
    assert sha(baseline/name) == row['sha256'],name
assert (baseline/'index.html').read_bytes() == (HERE/'prior-source/web/index.html').read_bytes()
dest=ROOT/'.local/private-evidence/web-tmd2-reporting-agent-v1/serve/constitutive-atlas'
assert not dest.exists()
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copytree(baseline,dest)
shutil.copyfile(ROOT/'web/index.html',dest/'index.html')
returned=bundle(dest)
files={str(p.relative_to(dest)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(dest.rglob('*')) if p.is_file()}
added=set(files)-set(manifest)
removed=set(manifest)-set(files)
changed={n for n in set(files)&set(manifest) if files[n]!=manifest[n]}
assert not removed
assert added == {'benchmark-tmd2/review/decision.json','benchmark-tmd2/review/review.md','benchmark-tmd2/review/review.html'}
assert changed == {'index.html','tmd2.html'}
result={'scope':'Static reporting delta on the exact retained ordinary package; no fresh full-engine package or live qualification.',
'path':str(dest),'baseline_manifest_sha256':sha(ROOT/'docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json'),
'baseline_files':len(manifest),'files':files,'added':sorted(added),'changed':sorted(changed),'removed':[],
'benchmark_public_assets':returned,'compiled_calls_by_this_command':0,'builds':0}
(HERE/'package-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: normal benchmark consumer; '+str(len(files))+' exact packaged files; only two changed pages and three new public review assets.')
