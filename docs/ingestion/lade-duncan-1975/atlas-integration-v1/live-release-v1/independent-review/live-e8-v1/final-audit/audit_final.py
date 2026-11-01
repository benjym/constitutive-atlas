import pathlib,json,hashlib,importlib.util
S=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');H=pathlib.Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');O=S/H/'independent-review/live-e8-v1/final-audit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('live',S/H/'check_live_v5.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prior=m.read('independent-review/live-checker-v1/v5-audit/review-receipt.json');assert all(sha(S/k)==h for k,h in prior['files'].items())
# Recomputes the complete private ZIP->tar->979member chain, not a saved self-report.
result=m.final();assert m.equal(result,m.read('FINAL_CHECK-v5.json'))
w=S/H/'browser-witness-v1';witness=m.parse((w/'manifest.json').read_bytes());assert len(witness['files'])==13
for n,h in witness['files'].items():assert sha(w/n)==h,n
# Tie normalized states and asset reports directly to the actual browser tool logs.
def logged(name):
 text=(w/name).read_text();raw=text.split('### Result\n',1)[1];return json.JSONDecoder().raw_decode(raw)[0]
for name in ['dense','loose']:
 assert m.equal(logged(name+'-capture.log'),m.read('browser-'+name+'-state.json'))
 log=(w/(name+'-capture.log')).read_text();script=(w/(name+'-capture.js')).read_text()
 assert script in log and "getByRole('button',{name:'Export complete run',exact:true}).click()" in script
 assert 'Downloading file lade-duncan-1975-run.json' in log
 assert m.read('browser-'+name+'-state.json')['status']=='Strain-path response complete.'
assets=logged('live-assets-fetch.log');saved=m.read('live-assets.json')['assets'];assert len(assets)==len(saved)==30
for a,b in zip(assets,saved):assert a=={k:v for k,v in b.items()if k!='expected'}
assert 'cache:"no-store"' in (w/'fetch-live-assets.js').read_text()
assert "selectOption('loose')" in (w/'loose-select.log').read_text()
assert "getByRole('button', { name: 'Run strain path' }).click()" in (w/'loose-run.log').read_text()
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (w/'console.log').read_text()
paths=[H/n for n in ['check_live_v5.py','LIVE_POLICY-v5.json','release-run.json','deployment.json','live-assets.json','browser-dense-export.json','browser-loose-export.json','browser-dense-state.json','browser-loose-state.json','browser-console.json','public-presets-v1.json','run-artifacts.json','upload-acquisition.json','tested-upload.json','uploaded-identity.json','uploaded-package-manifest.json','upload-verification.json','FINAL_CHECK-v5.json','browser-witness-v1/manifest.json','independent-review/live-checker-v1/v5-audit/review-receipt.json','independent-review/live-e8-v1/upload-review-receipt.json']]
paths += [H/'browser-witness-v1'/n for n in witness['files']]
files={str(p):sha(S/p)for p in paths};(O/'RECOMPUTED_RESULTS.json').write_text(json.dumps({'final':result,'witness_files':13,'exact_browser_states':2,'actual_HTTP_observation_rows':30,'files':files},indent=2)+'\n');print(json.dumps(result,indent=2));print('bound',len(files))
