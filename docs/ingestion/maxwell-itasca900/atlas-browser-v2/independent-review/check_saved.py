"""Saved browser evidence checks; does not execute a compiled engine."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(R))
P=R/'docs/ingestion/maxwell-itasca900/atlas-browser-v2'
if (Path(__file__).parent/'inputs.json').exists():
 for path,h in json.loads((Path(__file__).parent/'inputs.json').read_text()).items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
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
assert report==json.loads((P/'checks-v1.json').read_text());print(json.dumps(report,indent=2))

identity=json.loads((site/'engine-maxwell/identity.json').read_text())
assert identity==freeze['maxwell_identity']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for file,key in [('maxwell.mjs','module_sha256'),('maxwell.wasm','wasm_sha256'),('models.json','catalogue_file_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('review.html','review_html_sha256'),('qualification.json','qualification_sha256'),('build-review.json','build_review_sha256'),('interface-review.json','interface_review_sha256')]:assert sha(site/'engine-maxwell'/file)==identity[key]
for name,h in identity['component_sha256'].items():assert sha(site/name)==h==sha(R/'web'/name)
qual=json.loads((site/'engine-maxwell/qualification.json').read_text());buildreview=json.loads((site/'engine-maxwell/build-review.json').read_text())
assert qual['binding']==buildreview['binding'] and qual['gates']==buildreview['gates'] and buildreview['status']=='accepted'
assert qual['binding']['source_manifest_sha256']==freeze['source_manifest']['sha256']=='af8a045962d73bef332222ae3b91139a53cd05078b9987444780635ef29bd493'
assert qual['binding']['wasm_sha256']==identity['wasm_sha256']=='fb415e8e539ebe6a344bbc84afa0767a0192489d7c75a578e0069ea794d271e5'
assert (site/'engine-maxwell/qualification.json').read_bytes()==(R/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/maxwell-qualification.json').read_bytes()
assert (site/'engine-maxwell/build-review.json').read_bytes()==(R/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/independent-review/final-v1/build-review.json').read_bytes()
assert len(manifest['files'])==953 and len(assets['assets'])==159 and len(seen)==58 and len(external)==3
assert set(x['name'] for x in assets['checked'])=={'engine-maxwell/review.html','engine-maxwell/review.json','engine-maxwell/approval.json','engine-maxwell/maxwell-itasca900-zero-spin-ode.json','engine-maxwell/qualification.json','scalar-functions-NOTICES.txt'}
notices=next(x for x in raw_bytes if x['url'].endswith('/scalar-functions-NOTICES.txt'))
assert notices['bytes']==17801 and notices['sha256']=='e22612e1a87864b4f3eb08d6e222fa4f18c082a020cc212fee67f40b44cd5dbe'
assert sha(R/'cpp/scalar-functions/NOTICES.txt')==notices['sha256']
print('PASS: exact freeze/qualified common-runtime identity, all interface components,953sitebytes,58directbrowserbyte hashes,three external fonts,recorded notice mismatch and six precise local link targets.')

trace=json.loads((P/'actual-interactions-tool-result.json').read_text())['content'][0]['text']
interaction=json.loads(trace.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0])
assert interaction['importedStatus']=='Physical-time history complete.'
assert interaction['invalid']['exportDisabled'] is True and interaction['invalid']['message'].startswith('Invalid input: K, G and eta')
assert interaction['recovered']['status']=='Physical-time history complete.' and interaction['recovered']['preset']=='creep' and interaction['recovered']['exportDisabled'] is False
assert json.loads(interaction['recovered']['parameters'])==[20000000,12000000,24000000]
for tag,presetname in [('import','relaxation'),('recovery','creep')]:
 durable=Path(__file__).parent/'interaction-exports'/f'{tag}.json'
 source=durable if durable.exists() else Path(f'/private/tmp/maxwell-v2-verified-{tag}.json')
 assert json.loads(source.read_text())==json.loads((P/'browser'/f'{presetname}.json').read_text())
print('PASS: retained actual browser import/error/export-disabled/reset-creep recovery tool source/result and complete downloaded outputs exact.')
