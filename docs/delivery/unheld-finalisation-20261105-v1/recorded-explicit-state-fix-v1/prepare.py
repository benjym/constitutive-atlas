from pathlib import Path
import json,hashlib,gzip
P=Path(__file__).resolve().parent
W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def h(b):return hashlib.sha256(b).hexdigest()
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
legacy={'linear-elastic':'33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041','drucker-prager':'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877','modified-cam-clay':'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14','hypoplastic-sand-vw96':'1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61','hypoplastic-sand-igs97':'83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'}
flat=lambda m:[v for f in m['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
states={};proof=[]
for mid,sha in legacy.items():
 old=W/f'catalogue/source-snapshots/{sha}/models/{mid}.json';new=W/f'models/{mid}.json'
 a,b=old.read_bytes(),new.read_bytes();assert h(a)==sha
 states[mid]=flat(json.loads(a));assert states[mid]==flat(json.loads(b))
 for key,src in [('legacy',old),('current',new)]:save(P/f'evidence/{key}/{mid}.json',src.read_bytes())
 proof.append({'model':mid,'legacy_sha256':sha,'current_sha256':h(b),'flattened_initial':states[mid]})
old=(W/'tools/test_recorded.mjs').read_text()
needle='  for(const {request:s} of [...retained,...restartRetained,{request:example}]){'
replacement='  // Preserve the retained legacy requests; make their formerly implicit fixture states explicit.\n  const retainedInitialExamples='+json.dumps(states,separators=(',',':'))+';\n  for(const {request:retainedRequest} of [...retained,...restartRetained,{request:example}]){\n   const s=retainedRequest.initial?retainedRequest:{...retainedRequest,initial:[...retainedInitialExamples[retainedRequest.model]]};'
assert old.count(needle)==1
new=old.replace(needle,replacement)
save(P/'original/tools/test_recorded.mjs',old.encode());save(P/'proposed/tools/test_recorded.mjs',new.encode())
for path in ['web/recorded.mjs','web/numerics.mjs','cpp/main.cpp','cpp/include/atlas/solver.hpp','tools/test_ensemble_wasm.mjs','web/ensemble.mjs','web/recorded-worker.mjs','tools/test_wasm.mjs','tools/test_browser_loading.mjs','tools/test_scoped_parity.mjs','tools/test_supported_package.mjs','.github/workflows/qualification.yml']:
 save(P/'evidence/source'/path,(W/path).read_bytes())
for stem in ['recorded-replay-api-v1','recorded-restarts-v1']:
 path=f'catalogue/investigations/{stem}/responses.json.gz';save(P/'evidence'/path,(W/path).read_bytes())
for name in ['recorded-linear-elastic-run.json','recorded-dp-restart-run.json']:save(P/'evidence/protocols'/name,(W/'protocols'/name).read_bytes())
save(P/'evidence/default-equivalence.json',(json.dumps(proof,indent=2)+'\n').encode())
log=Path('docs/delivery/unheld-finalisation-20261105-v1/publication-v1/followup-failure-v1/linux-raw.log')
save(P/'failure-reference.json',(json.dumps({'path':str(log),'sha256':h(log.read_bytes()),'locators':[1148,1151]},indent=2)+'\n').encode())
row={'path':'tools/test_recorded.mjs','preimage_sha256':h(old.encode()),'sha256':h(new.encode()),'bytes':len(new.encode()),'proposal':'proposed/tools/test_recorded.mjs'}
save(P/'source-delta.json',(json.dumps({'files':[row]},indent=2)+'\n').encode())
