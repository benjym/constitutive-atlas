"""Saved-only standard package/browser evidence checks; no browser/compiled execution."""
import hashlib,importlib.util,json,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6];BASE=ROOT/'docs/ingestion/maxwell-itasca900/atlas-integration-v1';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
def captured(v):
 if 'result' in v:return captured(v['result'])
 if 'content' in v:
  t='\n'.join(c.get('text','') for c in v['content']);return json.JSONDecoder().raw_decode(t.split('### Result\n',1)[1])[0]
 return v
m=load(BASE/'package-manifest-v1.json');site=Path(m['package']);assert len(m['files'])==950
assert {str(p.relative_to(site)) for p in site.rglob('*') if p.is_file()}==set(m['files'])
for n,h in m['files'].items():assert sha((site/n).read_bytes())==h,n
for n,h in m['source_bindings'].items():assert sha((ROOT/n).read_bytes())==h
for n,x in load(BASE/'independent-review/manifest.json')['files'].items():assert sha((ROOT/n).read_bytes())==x['sha256'],n
cmd=load(BASE/'package-command.json');proc=load(BASE/'package-process-v1.json');assert proc['command']==cmd['command'] and proc['cwd']==cmd['cwd'] and proc['returncode']==0 and proc['command_document_sha256']==sha((BASE/'package-command.json').read_bytes())
for s in ['Power-creep package:','nullRateMaskComparisons','fullStateStressComparisons','stateComparisons','Packaged ']:assert s in proc['stdout']
assert not proc['stderr'];assert '--maxwell-wasm-dir' in proc['command'];assert 'maxwell.html' not in m['files']
fresh=captured(load(BASE/'browser-fresh-assets-v1.json'));assert fresh['passed'] is True and not fresh['body_capture_gaps'] and not fresh['errors'] and not fresh['failed'];assert len(fresh['fresh_response_sha256'])==56
for n,h in fresh['fresh_response_sha256'].items():assert m['files'][n]==h,n
for n in ['app.js','maxwell-laboratory.mjs','maxwell-atlas-runner.mjs','maxwell-atlas-contract.mjs','maxwell-atlas-engine.mjs','maxwell-atlas-worker.mjs','laboratory-controller-router.mjs','engine-maxwell/maxwell.mjs','engine-maxwell/maxwell.wasm']:assert n in fresh['fresh_response_sha256']
identity=load(site/'engine-maxwell/identity.json');qualification=load(site/'engine-maxwell/qualification.json');buildreview=load(site/'engine-maxwell/build-review.json');assert buildreview['status']=='accepted' and qualification['binding']==buildreview['binding']
for k,n in {'model_sha256':'engine-maxwell/maxwell-itasca900-zero-spin-ode.json','catalogue_file_sha256':'engine-maxwell/models.json','module_sha256':'engine-maxwell/maxwell.mjs','wasm_sha256':'engine-maxwell/maxwell.wasm','approval_sha256':'engine-maxwell/approval.json','review_sha256':'engine-maxwell/review.json','review_html_sha256':'engine-maxwell/review.html','qualification_sha256':'engine-maxwell/qualification.json','build_review_sha256':'engine-maxwell/build-review.json','interface_review_sha256':'engine-maxwell/interface-review.json'}.items():assert sha((site/n).read_bytes())==identity[k]
for n,h in identity['component_sha256'].items():assert sha((site/n).read_bytes())==h
model=load(ROOT/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json');assert load(site/'engine-maxwell/models.json')['models']==[model]
# Unchanged frozen source assessor over the four actual downloaded UI exports.
sys.path.insert(0,str(ROOT));sp=importlib.util.spec_from_file_location('browser_saved_assessor',ROOT/'tests/test_maxwell.py');checks=importlib.util.module_from_spec(sp);sp.loader.exec_module(checks)
cases=load(ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')['cases'];wasm=load(ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1/observations/wasm-raw.json');errors={}
for n,cid in [('relaxation','relaxation-schedule'),('creep','creep-schedule'),('oedometer','oedometer'),('load-hold-reverse','load-hold-reverse')]:
 run=load(BASE/'browser-exports'/f'browser-{n}.json');case=next(c for c in cases if c['id']==cid);s=case['specification'];assert run['provenance']==identity
 for k in s:
  if k!='solver':assert run['controls'][k]==s[k],(n,k)
 errors[n]=checks.assess(case,run['result']);actual=json.loads(next(r for r in wasm if r['id']==cid)['calls'][0]['stdout']);assert run['result']==actual,n
assert load(BASE/'browser-exports/browser-relaxation.json')==load(BASE/'browser-exports/browser-replayed.json')
parameter=load(BASE/'browser-exports/browser-parameter-edit.json');state=load(BASE/'browser-exports/browser-state-edit.json');history=load(BASE/'browser-exports/browser-history-edit.json')
assert parameter['controls']['parameters']==parameter['result']['parameters']==[20000000,12000000,48000000]
assert state['controls']['initial']==state['result']['initial']==[141000,81000,81000,3000,-2000,1000]
assert history['controls']['start_time']==history['result']['start_time']==2 and history['result']['points'][-1]['time']==6
assert history['controls']['segments']==history['result']['segments'] and history['controls']['segments'][0]['duration']==4 and history['controls']['segments'][0]['samples']==4
# Export database: exact definition, canonical review and both extant approval authorities.
con=sqlite3.connect('file:'+str(site/'atlas.sqlite')+'?mode=ro',uri=True);mid=model['id'];row=con.execute('select definition_json from models where id=?',(mid,)).fetchone();assert row and json.loads(row[0])==model
source_rows=set(con.execute('select url,locator,role from sources where model_id=?',(mid,)).fetchall());assert source_rows=={(s['url'],s['locator'],s['role']) for s in model['sources']}
registry=load(ROOT/'catalogue/approved-models.json');entries=registry['models'] if isinstance(registry,dict) else registry
assert {a['id'] for a in entries if a['model_id']==mid}=={'maxwell-user-approval-v1','maxwell-itasca900-zero-spin-agent-review-v2-approval'}
for a in entries:
 if a['model_id']==mid:
  saved=con.execute('select definition_sha256,record_json from model_approvals where id=?',(a['id'],)).fetchone();assert saved and saved[0]==identity['model_sha256'] and json.loads(saved[1])==a
review=con.execute('select sha256,record_json from agent_reviews where model_id=?',(mid,)).fetchone();assert review and review[0]==identity['review_sha256'] and json.loads(review[1])==load(site/'engine-maxwell/review.json')
# Saved actual browser scripts/results: preserved failures are not relabeled passing.
presets=captured(load(BASE/'browser-presets-v1.json'));assert presets['passed'] and not presets['errors'] and not presets['failed']
assert [r['preset'] for r in presets['records']]==['relaxation','creep','oedometer','load-hold-reverse']
for r in presets['records']:
 run=load(BASE/'browser-exports'/('browser-'+r['preset']+'.json'));assert r['provenance']==identity and r['rows']==len(run['result']['points'])+1
assert presets['body_capture_gaps']  # retained initial incomplete capture, superseded by verified fresh bodies

flow=captured(load(BASE/'browser-flow-v3.json'));assert flow['passed'] and flow['import_replay'] and flow['identity_tamper_rejected'] and flow['plots'] and flow['invalid_input_recovery'] and flow['sls_switch'] and flow['catalogue_route_and_sources']
assert flow['result_tamper_rejected']=='Run failed: Replayed complete result differs from saved output.'
assert flow['model_switch_cancellation']['hidden'] and 'Running' in flow['model_switch_cancellation']['running']
assert len(flow['localLinks'])==4 and all(x['status']==200 for x in flow['localLinks'])
assert 'stress plot geometry' in json.dumps(load(BASE/'browser-flow-v2.json'))
extra=captured(load(BASE/'browser-extra-v1.json'));assert extra['passed'] and extra['custom_history_and_clock'] and extra['reset_clock'] and extra['mixed_entry_null_rate_disclosure'] and extra['component_plot_switch'] and extra['mobile']=={'viewport':390,'document':390}
latest=captured(load(BASE/'browser-latest-request-v1.json')['actual_tool_result'])
assert latest['stages']=={'first':'Running physical-time history…','edited':'Inputs changed. Run to update results.','cleared':True,'second':'Running physical-time history…'}
assert latest['final']=='Physical-time history complete.' and latest['url'].endswith('/index.html#laboratory?model=maxwell-itasca900-zero-spin-ode')
assert load(BASE/'browser-exports/browser-latest-request.json')==parameter
supported=load(BASE/'supported-package-v1.json');supportedproc=load(BASE/'supported-package-process-v1.json');assert supportedproc['returncode']==0 and supported['status']=='passed' and len(supported['ordinary'])==14 and len(supported['named'])==1
print(json.dumps({'passed':True,'package_files':950,'fresh_actual_response_body_hashes':56,'source_reference_errors_Pa':errors,'four_browser_complete_results_equal_qualified_wasm':True,'full_saved_export_replay_exact':True,'database_definition_sources_review_approvals_exact':True,'actual_flow_v3_and_extra_saved_results':'passed','ordinary_supported_requests':14,'named_supported_examples':1,'actual_same_model_input_cancel_replacement':'passed; replacement export exactly matches earlier parameter-edited run','reviewer_builds':0,'reviewer_compiled_calls':0,'reviewer_browser_actions':0},indent=2))
