#!/usr/bin/env python3
"""Independent source/saved-package mixed-profile check; no compiled engine execution."""
import hashlib,json,pathlib,re,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;BASE=HERE.parent.parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def run(site):
 f=read(HERE/'source/mixed-freeze.json');assert f['new_mixed_package_runs_before_freeze']==f['new_mixed_browser_runs_before_freeze']==0
 for p,h in f['files'].items():assert sha(HERE/'source'/p)==h,p
 assert sha(BASE/'mixed-browser-server.py')==f['server']
 for p,h in f['reused_burgers'].items():
  target='models.json' if p=='generated/models.json' else p
  assert sha(site/'engine-burgers'/target)==h,p
 for p in ['web/app.js','web/j2-laboratory.mjs','web/j2-contract.mjs','web/timed-laboratory.mjs','web/timed-contract.mjs','web/timed-worker.mjs']:assert sha(site/pathlib.Path(p).name)==f['files'][p],p
 # Preserve exact approved J2 material identity; review HTML may differ between delivery identities.
 old=read(BASE/'package-manifest-r3.json');manifest=read(BASE/'package-manifest-mixed.json')
 assert manifest==read(site/'material-point-j2/package-manifest.json')
 for p,h in manifest.items():assert sha(site/p)==h,p
 for p,h in old.items():
  if p!='material-point-j2/review.html':assert manifest[p]==h,p
 burgers=read(site/'engine-burgers/package.json')
 for p,h in burgers['files'].items():assert sha(site/p)==h,p
 r3=read(BASE/'interface-freeze-r3.json')
 for source,target in [('atlas.js','atlas.js'),('atlas.wasm','atlas.wasm'),('generated/models.json','models.json')]:assert sha(site/target)==r3['reused_engine']['/private/tmp/atlas-j2-delivery-v1/root-wasm/'+source]
 log=(BASE/'package-mixed.log').read_text();reports=[json.JSONDecoder().raw_decode(log[m.start():])[0] for m in re.finditer(r'(?m)^\{',log)]
 j2=next(x for x in reports if x.get('calls')==327);assert j2['passed'] and j2['stateComparisons']==1264 and j2['tangentComparisons']==192
 assert j2['identity']==read(site/'material-point-j2/identity.json')
 timed=next(x for x in reports if x.get('model')=='burgers-itasca900-dry-zero-spin-ode');assert timed['ok'] and timed['finitePhysicalScalarComparisons']==594 and timed['nullRateMaskComparisons']==6 and timed['exactReplay']
 assert 'Power-creep package: identity, Pages-relative paths, analytical creep and relaxation passed' in log and 'Packaged '+str(site) in log
 obs=read(BASE/'browser-mixed.json');assert obs['freeze']=='mixed-freeze.json' and obs['source_app_sha256']==f['files']['web/app.js']
 assert set(obs['directed_edges_passed'])=={'J2→Burgers','Burgers→ordinary','ordinary→J2','J2→ordinary','ordinary→Burgers','Burgers→J2'}
 assert obs['delayed_j2_initialization'].startswith('PASS:20sec')
 assert any('Delayedtimed-worker.mjs20sec' in s for s in obs['observations'])
 assert 'Ran 39 tests' in (BASE/'mixed-python-tests.log').read_text() and '\nOK' in (BASE/'mixed-python-tests.log').read_text()
 nodes=(BASE/'mixed-node-tests.log').read_text();assert 'pass 6' in nodes and 'fail 0' in nodes
 pure={}
 for filename in ['check_async.mjs','check_timed_cancellation.mjs']:
  out=json.loads(subprocess.check_output(['node',str(HERE/filename)],cwd=ROOT));assert out['passed'] and out['compiledCalls']==0;pure[filename]=out
 routing=json.loads(subprocess.check_output(['node',str(HERE/'source/tests/test_j2_main_routing.mjs'),str(HERE/'source/web/app.js')],cwd=ROOT));assert routing['passed'] and routing['checks']==63
 return dict(passed=True,verdict='accept exact mixed J2/Burgers/ordinary interface',source_inputs=14,package_J2_assets=10,package_Burgers_assets=len(burgers['files']),unchanged_root_assets=3,J2_calls=327,J2_state_comparisons=1264,J2_tangent_comparisons=192,Burgers_physical_comparisons=594,Burgers_null_rate_masks=6,durable_routing_checks=63,late_ordinary_worker_cases=len(pure['check_async.mjs']['workerCases']),late_import_error_cases=len(pure['check_async.mjs']['importCases']),late_Burgers_cases=len(pure['check_timed_cancellation.mjs']['cases']),saved_browser_directed_edges=6,reviewer_compiled_calls=0,limits=['Coordinator IAB observations assessed from saved record; reviewer did not operate browser.','Prior J2 import/export/custom/failure evidence reused only for unchanged module/contract/engine.','No new scientific approval, experimental validation, whole-domain qualification or live release claim.'])
if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-j2-main-v2/site-next')),indent=2))
