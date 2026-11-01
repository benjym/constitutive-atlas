"""Saved browser evidence checks; does not execute a compiled engine."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R))
P=Path(__file__).resolve().parent
from tests.test_maxwell import assess
from tools.build_maxwell_laboratory import source_manifest
freeze=json.loads((P/'prospective-freeze-v1.json').read_text());site=R/freeze['site']
assert source_manifest()==freeze['source_manifest']
manifest=json.loads((R/freeze['package_manifest']).read_text())
assert hashlib.sha256((R/freeze['package_manifest']).read_bytes()).hexdigest()==freeze['package_manifest_sha256']
assert {str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}==manifest['files']
for p,h in freeze['references'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
rows=json.loads((R/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/observations/presets.json').read_text())
cases=json.loads((R/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text())['cases']
ids={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}
errors={}
for row in rows:
 saved=json.loads((P/'browser'/f"{row['name']}.json").read_text())
 assert saved['controls']==row['controls'] and saved['result']==row['result'] and saved['request']=={'function':'atlas_run_schedule','args':row['args']},row['name']
 errors[row['name']]=assess(next(c for c in cases if c['id']==ids[row['name']]),saved['result'])
for name,original in [('imported-relaxation','relaxation'),('recovered-reset-creep','creep')]:
 saved=json.loads((P/'browser'/f'{name}.json').read_text());expected=json.loads((P/'browser'/f'{original}.json').read_text())
 assert saved==expected,name
assets=json.loads((P/'browser/browser-assets.json').read_text())
assert assets['errors']==[] and assets['plots']==3 and assets['mobile']=={'width':390,'documentWidth':390}
seen=set();external=[];body_capture_differences=[]
for row in assets['assets']:
 if not row['url'].startswith('http://127.0.0.1:18784/'):
  from urllib.parse import urlparse
  assert urlparse(row['url']).hostname in {'fonts.googleapis.com','fonts.gstatic.com'} and row['status']==200,row['url']
  external.append(row);continue
 name=row['url'].split('http://127.0.0.1:18784/',1)[1].split('?',1)[0]
 assert row['status']==200,name
 if manifest['files'][name]!=row['sha256'] or (site/name).stat().st_size!=row['bytes']:body_capture_differences.append(name)
 seen.add(name)
required={'index.html','app.js','maxwell-laboratory.mjs','maxwell-atlas-contract.mjs','maxwell-atlas-engine.mjs','maxwell-atlas-worker.mjs','engine-maxwell/maxwell.mjs','engine-maxwell/maxwell.wasm','engine-maxwell/identity.json','engine-maxwell/models.json','engine-maxwell/review.html','engine-maxwell/qualification.json','scalar-functions-NOTICES.txt'}
assert required<=seen,required-seen
raw_bytes=json.loads((P/'browser/raw-byte-verification.json').read_text())
assert len(raw_bytes)==len(seen)
assert {r['url'].split('http://127.0.0.1:18784/',1)[1].split('?',1)[0] for r in raw_bytes}==seen
for row in raw_bytes:
 name=row['url'].split('http://127.0.0.1:18784/',1)[1].split('?',1)[0]
 assert row['status']==200 and manifest['files'][name]==row['sha256'] and (site/name).stat().st_size==row['bytes'],name
assert body_capture_differences==['scalar-functions-NOTICES.txt'],body_capture_differences

assert len(assets['links'])==7 and len(assets['checked'])==6 and all(x['status']==200 for x in assets['checked'])
result=subprocess.run(['node',str(P/'check_exports.mjs'),str(site),str(P/'browser')],capture_output=True,text=True)
assert result.returncode==0,result.stdout+result.stderr
report={'status':'passed','package_files':len(manifest['files']),'fetched_responses':len(assets['assets']),'unique_fetched_assets':len(seen),'external_font_responses':len(external),'direct_arraybuffer_matches':len(raw_bytes),'decoded_capture_difference':body_capture_differences,'complete_preset_matches':4,'replay_recovery_exact_exports':2,'source_errors_Pa':errors,'node_stdout':result.stdout,'scope':'Saved-only local browser delta; no new engine execution or live release'}
(P/'checks-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
