#!/usr/bin/env python3
"""Independent source/saved-package four-profile check; no compiled engine execution."""
import hashlib,json,pathlib,re,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;BASE=HERE.parent.parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def run(site):
 receipts=read(HERE/'manifest.json')
 for group in ['inputs','outputs']:
  for path,digest in receipts[group].items():
   q=pathlib.Path(path);q=q if q.is_absolute() else ROOT/q
   assert sha(q)==digest,path
 f=read(HERE/'source/ship-freeze.json');assert f['new_ship_package_runs_before_freeze']==f['new_ship_browser_runs_before_freeze']==0
 for p,h in f['files'].items():assert sha(HERE/'source'/p)==h,p
 assert sha(BASE/'ship-browser-server.py')==f['server']
 for name in read(HERE/'source-results.json')['committed_SLS_and_router_unchanged']:
  assert hashlib.sha256(subprocess.check_output(['git','show',f['base']+':'+name],cwd=ROOT)).hexdigest()==f['files'][name],name
 for p,h in f['reused_sls'].items():
  target='models.json' if p=='generated/models.json' else p
  assert sha(site/'engine-sls'/target)==h,p
 for p in ['web/j2-laboratory.mjs','web/j2-contract.mjs','web/timed-laboratory.mjs','web/timed-contract.mjs','web/timed-worker.mjs','web/sls-laboratory.mjs','web/sls-atlas-contract.mjs','web/sls-atlas-worker.mjs','web/laboratory-controller-router.mjs']:assert sha(site/pathlib.Path(p).name)==f['files'][p],p
 # Distinct subsequent catalogue-copy preservation: retain original ship source and bind sole changed line.
 follow=read(HERE/'catalogue-copy-followup/receipt.json');oldapp=(HERE/'source/web/app.js').read_text();newapp=(HERE/'catalogue-copy-followup/app.js').read_text()
 assert sha(HERE/'catalogue-copy-followup/app.js')==follow['app_sha256'] and follow['previous_app_sha256']==f['files']['web/app.js']
 oldlines=oldapp.splitlines();newlines=newapp.splitlines();assert len(oldlines)==len(newlines)
 changed=[(a,b) for a,b in zip(oldlines,newlines) if a!=b];assert len(changed)==1
 before,after=changed[0];insertion="else if(timedRoute){const section=element('section');section.append(element('h3','Physical-time formulation'),element('p','Open the dedicated laboratory for supported controls, conventions and source/review links.'));body.append(section);}"
 assert after==before.replace('else body.append(formulationSection',insertion+'else body.append(formulationSection')
 assert sha(site/'app.js') in [f['files']['web/app.js'],follow['app_sha256']]
 # Preserve exact approved J2 material identity; review HTML may differ between delivery identities.
 old=read(BASE/'package-manifest-r3.json');manifest=read(BASE/'package-manifest-ship.json')
 assert manifest==read(site/'material-point-j2/package-manifest.json')
 for p,h in manifest.items():assert sha(site/p)==h,p
 for p,h in old.items():
  if p!='material-point-j2/review.html':assert manifest[p]==h,p
 burgers=read(site/'engine-burgers/package.json')
 for p,h in burgers['files'].items():assert sha(site/p)==h,p
 r3=read(BASE/'interface-freeze-r3.json')
 for source,target in [('atlas.js','atlas.js'),('atlas.wasm','atlas.wasm'),('generated/models.json','models.json')]:assert sha(site/target)==r3['reused_engine']['/private/tmp/atlas-j2-delivery-v1/root-wasm/'+source]
 log=(BASE/'package-ship.log').read_text();reports=[json.JSONDecoder().raw_decode(log[m.start():])[0] for m in re.finditer(r'(?m)^\{',log)]
 j2=next(x for x in reports if x.get('calls')==327);assert j2['passed'] and j2['stateComparisons']==1264 and j2['tangentComparisons']==192
 for flag in ['immutableIdentity','exactReplay','preset','actualHistory','failedPrefix','recovery','corruptImportRejected']:assert j2[flag],flag
 assert j2['identity']==read(site/'material-point-j2/identity.json')
 timed=next(x for x in reports if x.get('model')=='burgers-itasca900-dry-zero-spin-ode');assert timed['ok'] and timed['finitePhysicalScalarComparisons']==594 and timed['nullRateMaskComparisons']==6 and timed['exactReplay']
 assert 'Power-creep package: identity, Pages-relative paths, analytical creep and relaxation passed' in log and 'Packaged '+str(site) in log
 obs=read(BASE/'browser-ship.json');assert obs['freeze']=='ship-freeze.json' and obs['source_app_sha256']==f['files']['web/app.js']
 profiles=['J2','Burgers','SLS','ordinary']
 assert set(obs['directed_edges_passed'])=={a+'→'+b for a in profiles for b in profiles if a!=b}
 observations=' '.join(obs['observations'])
 for phrase in ['Forced20s sls-atlas-worker.mjs','Forced20s material-point-j2/identity.json','After delayed worker','After delayed initialization','Browser error/warning logs empty']:assert phrase in observations,phrase
 assert 'Ran 38 tests' in (BASE/'ship-python-tests.log').read_text() and '\nOK' in (BASE/'ship-python-tests.log').read_text()
 nodes=(BASE/'ship-node-tests.log').read_text();assert 'pass 13' in nodes and 'fail 0' in nodes
 sls=read(site/'engine-sls/package-manifest.json')
 for p,h in sls['files'].items():assert sha(site/p)==h,p
 slsr=next(x for x in reports if x.get('model')=='sls-comsol63-deviatoric-zero-spin-ode')
 assert slsr['ok'] and slsr['fullStateStressComparisons']==324 and slsr['nullRateMaskEntries']==6 and slsr['allPackageAssetsGuarded']==12
 for k in ['exactReplay','failedRequestRecovery','standalonePageAbsent']:assert slsr[k],k
 pure={}
 for filename in ['check_sls_cancellation.mjs']:
  out=json.loads(subprocess.check_output(['node',str(HERE/filename)],cwd=ROOT));assert out['passed'] and out['compiledCalls']==0;pure[filename]=out
 routing=json.loads(subprocess.check_output(['node',str(HERE/'source/tests/test_j2_main_routing.mjs'),str(HERE/'source/web/app.js')],cwd=ROOT));assert routing['passed'] and routing['checks']==157 and routing['transitionCalls']==27
 followrouting=json.loads(subprocess.check_output(['node',str(HERE/'source/tests/test_j2_main_routing.mjs'),str(HERE/'catalogue-copy-followup/app.js')],cwd=ROOT));assert followrouting['passed'] and followrouting['checks']==157
 return dict(passed=True,verdict='accept exact frozen four-profile main interface',source_inputs=20,package_J2_assets=len(manifest),package_Burgers_assets=len(burgers['files']),package_SLS_assets=len(sls['files']),unchanged_root_assets=3,J2_calls=327,J2_state_comparisons=1264,J2_tangent_comparisons=192,Burgers_physical_comparisons=594,SLS_state_stress_comparisons=324,durable_routing_checks=157,durable_routing_transitions=27,late_SLS_cases=len(pure['check_sls_cancellation.mjs']['cases']),saved_browser_directed_edges=12,reviewer_compiled_calls=0,limits=['Coordinator actual IAB observations assessed from saved record; reviewer did not operate browser.','Prior custom/import/export/failure/descriptor coverage reused only for unchanged J2 module/contract/engine.','No new scientific approval, experimental validation, whole-domain qualification or live release claim.'])

if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-j2-main-v2/site-ship')),indent=2))
