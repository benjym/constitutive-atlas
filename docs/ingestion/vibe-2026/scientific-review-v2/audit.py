"""Independent source-only worker-loader amendment review; no material call."""
from pathlib import Path
import json,hashlib,sys,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
old=R/'docs/ingestion/vibe-2026/browser-loader-v1/original-worker.mjs';new=R/'web/controlled-time-worker.mjs'
a,b=old.read_bytes(),new.read_bytes();needle=b'wasmBinary:new Uint8Array(bytes[3]),';replacement=needle+b'locateFile:name=>new URL(name,base).href,'
assert a.count(needle)==1 and a.replace(needle,replacement)==b
assert sha(old)=='45aeb0e49e0e820c18a962a1c1b804422b8ad3970ec4b06ccef886f5fa097f83'
assert sha(new)=='855823cb0e555478956ce96a606ad8a111c061b51b2fc6c2370f4f2651d0e951'
assert b'await sha(bytes)!==identity.files[name]' in b and b'wasmBinary:new Uint8Array(bytes[3])' in b
p1=R/'docs/ingestion/vibe-2026/public-qualification-v1/public-qualification.json';p2=R/'docs/ingestion/vibe-2026/public-qualification-v2/public-qualification.json';x,y=load(p1),load(p2)
assert set(x)==set(y);z=json.loads(json.dumps(y));z['root_receipt_path']=x['root_receipt_path'];changes=[]
for f in z['source_files']:
 if f['path']=='web/controlled-time-worker.mjs':
  assert f['sha256']==sha(new);f['sha256']=sha(old);changes.append(f['path'])
assert changes==['web/controlled-time-worker.mjs'] and z==x
for pin in y['source_files']:assert sha(R/pin['path'])==pin['sha256'],pin['path']
for k in ['examples','public_results','native_qualification','wasm_qualification','backend_review','public_actual_receipt']:
 pin=y[k];assert sha(R/pin['path'])==pin['sha256'],k
assert sha(R/'models/research/vibe/vibe-2026-explicit-appendix-a.json')=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987'
assets=R/'web/engines/controlled-time'
for n,h in y['artifacts'].items():assert sha(assets/n)==h
# Confirm actual generated Emscripten path selection without importing it.
s=(assets/'atlas_controlled_time_capability.mjs').read_text()
assert 'if(Module["locateFile"]){return locateFile("atlas_controlled_time_capability.wasm")}' in s
assert 'return new URL("atlas_controlled_time_capability.wasm",import.meta.url).href' in s
assert 'wasmBinaryFile??=findWasmBinary()' in s
# Pure URL algebra tests deliberately execute no module or Wasm.
js='''const assert=require('node:assert/strict');const name='atlas_controlled_time_capability.wasm';let rejected=false;try{new URL(name,'blob:https://atlas.example/58ab');}catch(e){rejected=e instanceof TypeError;}assert.ok(rejected);const cases=['https://atlas.example/controlled-time-worker.mjs','https://atlas.example/nested/controlled-time-worker.mjs','http://127.0.0.1:8766/controlled-time-worker.mjs'];for(const url of cases){const base=new URL('./engine-controlled-time/',url);const locateFile=name=>new URL(name,base).href;assert.equal(locateFile(name),new URL('engine-controlled-time/'+name,url).href);}process.stdout.write(JSON.stringify({status:'pass',default_blob_base_refused:true,absolute_package_base_cases:cases.length,compiled_calls:0}));'''
r=subprocess.run(['node','-e',js],capture_output=True,text=True);assert r.returncode==0,r.stderr;url_checks=json.loads(r.stdout)
syntax=subprocess.run(['node','--check',str(new)],capture_output=True,text=True);assert syntax.returncode==0,syntax.stderr
sys.path.insert(0,str(R));from atlas.agent_review import validate_review
prior=validate_review(R/'catalogue/agent-reviews/vibe-2026-appendix-a-agent-v1.json',root=R,for_approval=True)
assert len(prior['artifacts'])==270
snapshot=(R/'docs/ingestion/vibe-2026/browser-loader-v1/original-browser-snapshot.yml').read_text();assert "Run failed: Failed to construct 'URL': Invalid URL" in snapshot
out={'status':'pass-source-only-loader-amendment','exact_single_option_byte_delta':True,'old_worker_sha256':sha(old),'new_worker_sha256':sha(new),'old_qualification_sha256':sha(p1),'new_qualification_sha256':sha(p2),'qualification_changes_only':['root_receipt_path','source_files[web/controlled-time-worker.mjs].sha256'],'unchanged_production_pins':len(y['source_files'])-1,'current_source_pins_verified':len(y['source_files']),'unchanged_artifact_and_evidence_pins_verified':True,'prior_review_270_current_supporting_files_validated':True,'pure_url_checks':url_checks,'node_worker_syntax':'pass','actual_browser_recovery':'pending coordinator run; original failure retained','no_material_module_or_browser_calls':True}
with (O/'audit-results.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out,indent=2))
