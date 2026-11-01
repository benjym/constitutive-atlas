"""Resolve exactly two later nonpackaged UI changes using preserved old bytes."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
receipt=read(HERE/'final-bindings-v1.json');changed={}
for name,h in receipt['files'].items():
 f=ROOT/name
 assert f.is_file(),name
 if sha(f)!=h:changed[name]={'accepted_sha256':h,'current_sha256':sha(f)}
assert set(changed)=={'web/implicit-path-laboratory.mjs','web/implicit-path-runner.mjs'}
manifest=read(HERE.parent/'package-manifest-v1.json');base=Path(manifest['source_path'])
for name,item in changed.items():
 archive=ROOT/'docs/ingestion/lade-duncan-1975/outer-predictor-v1/independent-review/integration-prospective-v1-context'/name
 assert sha(archive)==item['accepted_sha256'];item['preserved_path']=str(archive.relative_to(ROOT))
 assert Path(name).name not in manifest['files']
 for rel in manifest['files']:
  if Path(rel).suffix in ['.mjs','.js','.html']:
   assert Path(name).name not in (base/rel).read_text(),rel
for file in ['tools/build_web.py','web/app.js','web/index.html','web/laboratory-controller-router.mjs']:
 assert 'implicit-path-laboratory.mjs' not in (ROOT/file).read_text() and 'implicit-path-runner.mjs' not in (ROOT/file).read_text()
result={'status':'passed','original_pins':len(receipt['files']),'unchanged_pins':len(receipt['files'])-2,'resolved_later_changes':changed,'package_affected':False,'bounded_E6_E7_acceptance_changed':False,'compiled_execution':False,'browser_control':False}
(HERE/'later-drift-results-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
