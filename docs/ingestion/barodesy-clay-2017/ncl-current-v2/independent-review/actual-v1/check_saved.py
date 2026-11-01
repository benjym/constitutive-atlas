from pathlib import Path
import hashlib,json,importlib.util,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas'); P=R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2'; OLD=P.parent/'ncl-laboratory-v1'; OUT=P/'independent-review/actual-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if OUT.exists():
 for p,h in read(OUT/'inputs.json').items():assert sha(R/p)==h,p
f=read(P/'prospective-freeze-v2.json')
for p,h in f['files'].items():assert sha(R/p)==h,p
manifest=read(P/'results-manifest-v1.json');assert len(manifest)==13
assert {x.name for x in (P/'results').iterdir()}=={Path(x).name for x in manifest}
for name,item in manifest.items():
 p=P/name;assert sha(p)==item['sha256']and p.stat().st_size==item['bytes'];assert p.read_bytes()==(Path('/private/tmp/atlas-barodesy-ncl-current-v2-run')/Path(name).name).read_bytes()
pre=read(P/'independent-review/prospective-review.json');e=read(P/'execution-v1.json');assert e['argv']==pre['accepted_command']and e['cwd']==str(R)and e['timeout_seconds']==120 and e['exit_code']==0 and not e['timed_out']and e['stderr']==''
a=read(P/'assessment-execution-v1.json');assert a['argv']==pre['subsequent_required_saved_assessor']+['--output','/private/tmp/atlas-barodesy-ncl-current-v2-run/assessment.json']and a['exit_code']==0 and a['stderr']==''
cat=read(Path(f['catalogue']));assert len(cat['models'])==14 and cat['sha256']==f['catalogue_hash']
requests=read(P/'results/requests.json');assert requests==read(R/f['requests'])
rows={b:read(P/f'results/{b}.json')for b in ['native','wasm']};raw=read(P/'results/raw.json');assert len(raw)==16
ids=['metadata']+[q['id']for q in requests];assert [(x['backend'],x['id'])for x in raw]==[(b,i)for b in ['native','wasm']for i in ids]
for b,ix in [('native',0),('wasm',8)]:assert json.loads(raw[ix]['stdout'])==cat
assert raw[0]['args']==['--describe']and raw[0]['status']==0 and raw[0]['stderr']=='' and raw[0]['signal']is None and raw[0]['error']is None
assert raw[8]['function']=='atlas_describe'and raw[8]['args']==[]
# Pure public validators and CSV/CLI reconstruction; no generated module imported.
js="""import{readFileSync}from'node:fs';import assert from'node:assert/strict';import{settingsCsv}from'./web/numerics.mjs';import{verifyScopedLaboratory}from'./web/laboratory-scope.mjs';const p='docs/ingestion/barodesy-clay-2017/ncl-current-v2',read=x=>JSON.parse(readFileSync(x));const f=read(p+'/prospective-freeze-v2.json'),cat=read(f.catalogue),q=read(p+'/results/requests.json'),raw=read(p+'/results/raw.json');for(let i=0;i<7;i++){const {id,specification:s}=q[i],csv=settingsCsv(s.integration_settings),n=raw[i+1],w=raw[i+9];assert.deepEqual(n.args,['--mode','run-controls','--model',s.model,'--parameters',s.parameters.join(','),'--initial',s.initial.join(','),'--protocol',String(s.protocol),'--integration-settings',csv,'--laboratory-controls-file','/private/tmp/atlas-barodesy-ncl-current-v2-run/'+id+'-controls.txt','--response-contract',s.response_contract]);assert.equal(w.function,'atlas_run_controls_scope_with_settings');assert.deepEqual(w.args,[s.model,s.parameters.join(','),s.initial.join(','),s.protocol,s.loading.controls_bits.join(','),csv]);if(id!=='invalid-initial')for(const x of[n,w])verifyScopedLaboratory(JSON.parse(x.stdout),s,cat);}console.log('PASS: exact seven CLI/generic ABI requests and twelve scoped successful responses; no compiled calls');"""
z=subprocess.run(['node','--input-type=module','-e',js],cwd=R,text=True,capture_output=True);assert z.returncode==0,z.stderr
for i,q in enumerate(requests):
 assert (P/f"results/{q['id']}-controls.txt").read_text()==','.join(q['specification']['loading']['controls_bits'])
 for b,j in [('native',i+1),('wasm',i+9)]:
  rr=raw[j];row=rows[b][i];assert rr['id']==row['id'] and json.loads(rr['stdout'])==row['result']
  if b=='native':assert rr['status']==row['exit_code']==int(q['id']=='invalid-initial')and rr['stderr']==row['stderr']==''and rr['signal']is None and rr['error']is None
identity=read(P/'results/identity.json');assert identity['files']==f['files']and identity['catalogue_hash']==f['catalogue_hash']
assessor=load(OLD/'check.py','original_assessor');assessment=assessor.assess(P/'results');assert assessment==read(P/'results/assessment.json')==json.loads(a['stdout'])and assessment['passed']
auditor=load(OLD/'independent-review/check_review.py','original_independent');metrics=auditor.validate_rows(requests,rows,read(OLD/'policy.json'),cat,read(R/'models/barodesy-clay-2017.json'))
assert metrics['successful_caller_points']=={'native':507,'wasm':507}
report={'passed':True,'frozen_pins':len(f['files']),'saved_files':13,'raw_metadata_calls':2,'raw_material_calls':14,'compiled_catalogue_models':14,'public_validator_stdout':z.stdout.strip(),'original_assessment':assessment,'enhanced_original_audit':metrics,'reviewer_compiled_calls':0,'reviewer_builds':0}
print(json.dumps(report,indent=2))
