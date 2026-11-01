"""Saved-only Maxwell CI regression review; never imports generated JS or Wasm."""
from pathlib import Path
import hashlib,json,subprocess,sys,tarfile
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from tests.test_maxwell import assess_rows,assess
from tools.build_maxwell_laboratory import source_manifest
PACKET=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2';OBS=PACKET/'observations'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (Path(__file__).parent/'inputs.json').exists():
 for p,h in load(Path(__file__).parent/'inputs.json').items():assert sha(ROOT/p)==h,p
raw_manifest=load(PACKET/'output-manifest-v2.json');manifest={'files':{k:v['sha256'] for k,v in raw_manifest.items()}};output=Path(load(PACKET/'execution-v2.json')['command'][-1])
assert set(manifest['files'])=={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
for p,h in manifest['files'].items():assert sha(output/p)==h and (output/p).stat().st_size==raw_manifest[p]['bytes'],p
for p in OBS.iterdir():assert sha(p)==manifest['files'][p.name],p
identity=load(OBS/'identity.json')
for prefix in ['guarded-package','guarded-package-after']:
 engine=output/prefix/'engine-maxwell'
 assert load(engine/'identity.json')==identity
 for name,key in [('models.json','catalogue_file_sha256'),('maxwell.mjs','module_sha256'),('maxwell.wasm','wasm_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('review.html','review_html_sha256'),('qualification.json','qualification_sha256'),('build-review.json','build_review_sha256'),('interface-review.json','interface_review_sha256')]:assert sha(engine/name)==identity[key]
 assert load(engine/'source-manifest.json')==load(OBS/'inputs.json')['source_manifest']
 for name,h in identity['component_sha256'].items():assert sha(ROOT/'web'/name)==h and sha(output/prefix/name)==h
 assert load(engine/'models.json')['sha256']==identity['catalogue_hash']
qual=load(output/'guarded-package/engine-maxwell/qualification.json');review=load(output/'guarded-package/engine-maxwell/build-review.json')
assert qual['binding']==review['binding'] and qual['gates']==review['gates'] and all(v is True for v in qual['gates'].values()) and len(qual['gates'])==5
assert review['status']=='accepted'
inputs=load(OBS/'inputs.json')
assert inputs['source_manifest']==source_manifest()
assert inputs['source_manifest']['sha256']==qual['binding']['source_manifest_sha256']=='af8a045962d73bef332222ae3b91139a53cd05078b9987444780635ef29bd493'
for p,h in inputs['files'].items():assert sha(ROOT/p)==h,p
assert len(inputs['files'])==12
cases=load(ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')['cases'];raw=load(OBS/'raw.json')
errors=assess_rows(cases,raw);report=load(OBS/'report.json')
assert len(cases)==24 and report['frozen_calls']==48 and errors==report['reference_errors_Pa']
mapping={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}
presets=load(OBS/'presets.json');assert [r['name'] for r in presets]==list(mapping)
preseterrors={}
for row in presets:
 case=next(c for c in cases if c['id']==mapping[row['name']]);source=load(ROOT/f"examples/maxwell/{row['name']}.json")
 assert source==case['specification'] and row['controls']==dict(source,solver=row['controls']['solver'])
 assert row['result']==row['replayed_result']
 preseterrors[row['name']]=assess(case,row['result'])
assert preseterrors==report['preset_errors_Pa'] and report['public_calls']==8 and report['status']=='passed'
commands=load(OBS/'commands.json');assert len(commands)==3 and all(c['returncode']==0 and c['timeout_seconds']==120 for c in commands)
assert 'tests 21' in commands[0]['stdout'] and 'pass 21' in commands[0]['stdout'] and 'fail 0' in commands[0]['stdout']
execution=load(PACKET/'execution-v2.json');prospective=load(PACKET/'independent-review/prospective-review.json')
assert execution['command']==prospective['accepted_command'] and execution['terminal_returncode']==0 and execution['status']=='passed'
assert all(c['stderr']=='' for c in commands)
node="""
import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {preset,presetNames,solver,request,types,verifyResult,exportRun,importRun,verifyReplay} from './web/maxwell-atlas-contract.mjs';
const dir=process.argv[1],read=n=>JSON.parse(readFileSync(dir+'/'+n,'utf8'));
const identity=read('identity.json'),rows=read('presets.json'),raw=read('presets.json.raw.json');
assert.equal(raw.length,9);assert.equal(raw[0].function,'atlas_describe');
const catalogue=JSON.parse(readFileSync('/private/tmp/atlas-maxwell-ci-regression-common-v2/guarded-package/engine-maxwell/models.json','utf8'));assert.deepEqual(JSON.parse(raw[0].stdout),catalogue);
for(const [i,row] of rows.entries()){
 assert.equal(row.name,presetNames[i]);assert.deepEqual(row.controls,preset(row.name));assert.deepEqual(row.controls.solver,solver);
 assert.deepEqual(row.args,request(row.controls,identity));verifyResult(row.result,identity,row.controls);verifyResult(row.replayed_result,identity,row.controls);
 const saved=exportRun(row.controls,row.result,identity);assert.deepEqual(saved.provenance,identity);const imported=importRun(JSON.stringify(saved),identity);verifyReplay(row.replayed_result,imported.result);
 for(const [j,phase] of ['first','replay'].entries()){const r=raw[1+2*i+j];assert.equal(r.name,row.name);assert.equal(r.phase,phase);assert.equal(r.function,'atlas_run_schedule');assert.deepEqual(r.args,row.args);assert.deepEqual(JSON.parse(r.stdout),j?row.replayed_result:row.result);}
}
console.log('PASS: saved metadata + eight material stdout; full controls/result/provenance/import/replay and all fixed solver settings.');
"""
r=subprocess.run(['node','--input-type=module','-e',node,str(OBS)],cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);print(r.stdout.strip())

preservation=load(PACKET/'preservation-v2.json')
assert sha(ROOT/preservation['helper_archive'])==preservation['helper_sha256']
for row in preservation['changed_sidecars']:
 prior=ROOT/'catalogue/source-snapshots'/row['before_sha256']/row['sidecar']
 assert sha(prior)==row['before_sha256'] and sha(ROOT/row['sidecar'])==row['after_sha256']
 oldmap=load(prior);newmap=load(ROOT/row['sidecar'])
 assert all(newmap['documents'].get(k)==v for k,v in oldmap['documents'].items())
 assert all(item in newmap['entries'] for item in oldmap['entries'])
for doc in preservation['checked_receipt_passes']:checked_receipt(ROOT,doc,'tools/provision_maxwell_assets.py',preservation['helper_sha256'])
print('PASS:45 output hashes and exact before/after guarded package identities; current149path accepted source manifest; oldhelper/seven receipt bindings/five maps preserved.')
print(json.dumps({'node_tests':21,'frozen_calls':48,'public_calls':8,'max_direct_error_Pa':max(errors[c['id']] for c in cases if c['kind']=='direct'),'max_preset_error_Pa':max(preseterrors.values()),'retained_coarse_error_Pa':errors['refine-coarse'],'fine_error_Pa':errors['refine-fine']},indent=2))

checked_receipt(ROOT,'docs/ingestion/maxwell-itasca900/atlas-ci-v2/prior-source.json','tools/provision_maxwell_assets.py',preservation['helper_sha256'])
print('PASS: new prior-source receipt resolves through its additive packet archive map.')
