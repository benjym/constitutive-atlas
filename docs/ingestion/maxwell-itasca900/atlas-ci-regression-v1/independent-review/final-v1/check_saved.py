"""Saved-only Maxwell CI regression review; never imports generated JS or Wasm."""
from pathlib import Path
import hashlib,json,subprocess,sys,tarfile
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from tests.test_maxwell import assess_rows,assess
from tools.build_maxwell_laboratory import source_manifest
PACKET=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1';OBS=PACKET/'observations'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (Path(__file__).parent/'inputs.json').exists():
 for p,h in load(Path(__file__).parent/'inputs.json').items():assert sha(ROOT/p)==h,p
manifest=load(PACKET/'output-manifest.json');output=Path(manifest['root'])
assert set(manifest['files'])=={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
for p,h in manifest['files'].items():assert sha(output/p)==h,p
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
archive=ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1/source-closure.tar.gz'
assert sha(archive)=='8fdf522c48bc32ddf29029b648f9e4cc07e0e5b016141768dc1d054bb9e16b76'
with tarfile.open(archive,'r:gz') as frozen:
 for p,h in inputs['source_manifest']['files'].items():assert hashlib.sha256(frozen.extractfile(p).read()).hexdigest()==h,p
assert inputs['source_manifest']['sha256']==qual['binding']['source_manifest_sha256']
current=source_manifest();old=inputs['source_manifest']['files'];now=current['files']
drift=[p for p in sorted(old.keys()|now.keys()) if old.get(p)!=now.get(p)]
print('CURRENT-SOURCE LIMITATION: runtime drift since saved execution:',drift,'current manifest',current['sha256'])
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
execution=load(PACKET/'execution.json');prospective=load(PACKET/'independent-review/prospective-review.json')
assert execution['command']==prospective['accepted_command'] and execution['exit_code']==0 and execution['builds']==0 and execution['remote_runs']==0
assert json.loads(execution['stdout'])==report and execution['stderr']==''
node="""
import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {preset,presetNames,solver,request,types,verifyResult,exportRun,importRun,verifyReplay} from './web/maxwell-atlas-contract.mjs';
const dir=process.argv[1],read=n=>JSON.parse(readFileSync(dir+'/'+n,'utf8'));
const identity=read('identity.json'),rows=read('presets.json'),raw=read('presets.json.raw.json');
assert.equal(raw.length,9);assert.equal(raw[0].function,'atlas_describe');
const catalogue=JSON.parse(readFileSync('/private/tmp/atlas-maxwell-ci-regression-v1/guarded-package/engine-maxwell/models.json','utf8'));assert.deepEqual(JSON.parse(raw[0].stdout),catalogue);
for(const [i,row] of rows.entries()){
 assert.equal(row.name,presetNames[i]);assert.deepEqual(row.controls,preset(row.name));assert.deepEqual(row.controls.solver,solver);
 assert.deepEqual(row.args,request(row.controls,identity));verifyResult(row.result,identity,row.controls);verifyResult(row.replayed_result,identity,row.controls);
 const saved=exportRun(row.controls,row.result,identity);assert.deepEqual(saved.provenance,identity);const imported=importRun(JSON.stringify(saved),identity);verifyReplay(row.replayed_result,imported.result);
 for(const [j,phase] of ['first','replay'].entries()){const r=raw[1+2*i+j];assert.equal(r.name,row.name);assert.equal(r.phase,phase);assert.equal(r.function,'atlas_run_schedule');assert.deepEqual(r.args,row.args);assert.deepEqual(JSON.parse(r.stdout),j?row.replayed_result:row.result);}
}
console.log('PASS: saved metadata + eight material stdout; full controls/result/provenance/import/replay and all fixed solver settings.');
"""
r=subprocess.run(['node','--input-type=module','-e',node,str(OBS)],cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);print(r.stdout.strip())
binding=load(PACKET/'workflow-binding.json');old=(ROOT/binding['before_archive']).read_bytes();current=(ROOT/binding['path']).read_bytes()
assert hashlib.sha256(old).hexdigest()==binding['before_sha256'] and hashlib.sha256(current).hexdigest()==binding['after_sha256']
line=b'          python -B tools/check_maxwell_ci.py --output "$RUNNER_TEMP/maxwell-ci-regression"\n'
assert current.count(line)==2 and current.replace(line,b'')==old
sequence=b'          python -B tools/provision_maxwell_assets.py\n'+line+b'          python tools/build_web.py\n'
assert current.count(sequence)==2
preservation=load(PACKET/'preservation.json')
for item in preservation['bindings']:checked_receipt(ROOT,item['document'],item['original_path'],item['sha256'])
repair=load(PACKET/'own-binding-repair.json');assert sha(ROOT/repair['document'])==repair['document_sha256']
assert sha(ROOT/repair['old_sidecar']['archive'])==repair['old_sidecar']['sha256']
repair_archive=ROOT/'catalogue/source-snapshots'/repair['new_sidecar_sha256']/repair['old_sidecar']['path']
assert sha(repair_archive)==repair['new_sidecar_sha256']
repaired=load(repair_archive);live_map=load(ROOT/repair['old_sidecar']['path'])
assert all(live_map['documents'].get(k)==v for k,v in repaired['documents'].items())
assert all(item in live_map['entries'] for item in repaired['entries'])
entry=repair['workflow_entry'];checked_receipt(ROOT,repair['document'],entry['original_path'],entry['sha256'])
inventory=load(PACKET/'frozen/bindings-before.json');counts={}
for key in ['primary_references','secondary_source_map_references']:
 count=0
 for item in inventory[key]:
  if item['resolution']=='unresolved':continue
  if item['resolution'].endswith('sidecar-entry'):
   original=ROOT/item['original_path'];canonical=ROOT/'catalogue/source-snapshots'/item['sha256']/item['original_path']
   assert any(p.is_file() and sha(p)==item['sha256'] for p in [original,canonical]),item
  else:checked_receipt(ROOT,item['document'],item['original_path'],item['sha256'])
  count+=1
 counts[key]=count
print('PASS: exact two additive required workflow hooks; prior workflow/receipt/sidecar and all previously resolved bindings preserved:',counts)
print(json.dumps({'output_files':len(manifest['files']),'frozen_calls':48,'public_calls':8,'max_direct_error_Pa':max(errors[c['id']] for c in cases if c['kind']=='direct'),'max_preset_error_Pa':max(preseterrors.values()),'retained_coarse_error_Pa':errors['refine-coarse'],'baseline_unresolved_retained':len(preservation['preexisting_unresolved'])},indent=2))
