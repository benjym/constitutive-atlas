"""Independent pure prospective source/reference check; never executes run.mjs."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,sys,tempfile
R=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(R));P=R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2'
from atlas.compiler import generate
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
if (Path(__file__).parent/'inputs.json').exists():
 for path,h in load(Path(__file__).parent/'inputs.json').items():assert sha(R/path)==h,path
f=load(P/'prospective-freeze-v2.json');assert len(f['files'])==173
for path,h in f['files'].items():assert sha(R/path)==h,path
assert sha(R/f['prior_plan']['path'])==f['prior_plan']['sha256']
a=(P/'run-initial.mjs.txt').read_text();b=(P/'run.mjs').read_text()
assert a.replace('.map(resolve)','.map(p=>resolve(p))').replace('prospective-freeze-v1.json','prospective-freeze-v2.json')==b
v1=load(P/'prospective-freeze-v1.json');assert v1['files']['docs/ingestion/barodesy-clay-2017/ncl-current-v2/run.mjs']==sha(P/'run-initial.mjs.txt')
accepted=load(R/'docs/reviews/common-scalar-functions-v1/actual-root-v1/source-freeze.json')['files']
relevant={p:h for p,h in f['files'].items() if p.startswith(('atlas/','cpp/','schemas/','models/','cmake/')) or p=='CMakeLists.txt'}
assert len(relevant)==158 and all(accepted.get(p)==h for p,h in relevant.items())
with tempfile.TemporaryDirectory(prefix='barodesy-ncl-review-generated-') as tmp:
 generate(tmp)
 assert (Path(tmp)/'models.json').read_bytes()==(R/f['catalogue']).read_bytes()==(R/f['wasm']/'generated/models.json').read_bytes()
catalogue=load(R/f['catalogue']);assert catalogue['sha256']==f['catalogue_hash'] and len(catalogue['models'])==14
model=load(R/'models/barodesy-clay-2017.json');assert sha(R/'models/barodesy-clay-2017.json')=='0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477'
assert next(m for m in catalogue['models'] if m['id']==model['id'])==model
artifacts=load(R/'docs/reviews/common-scalar-functions-v1/actual-root-v1/durable-artifacts.json')['artifacts']
for path in [f['native'],str(Path(f['wasm'])/'atlas.js'),str(Path(f['wasm'])/'atlas.wasm')]:
 record=next(x for x in artifacts if x['original_path']==path)
 assert sha(path)==sha(R/record['durable_path'])==record['sha256']
policy=load(R/f['policy']);requests=load(R/f['requests']);example=load(R/'docs/ingestion/barodesy-clay-2017/ncl-example-v1/example.json')
assert len(requests)==7 and [r['id'] for r in requests]==[c['id'] for c in policy['cases']]
default=[v for field in model['state'] for v in (field['initial'] if field['shape']=='sym' else [field['initial']])]
for request,case in zip(requests,policy['cases']):
 s=request['specification'];assert s['model']==model['id'] and s['parameters']==list(example['parameters'].values())
 expected=default if case['initial']=='unchanged-model-default' else [0]*6+[example['state']['e']] if case['initial']=='zero-stress-invalid' else example['state']['sigma']+[example['state']['e']]
 assert s['initial']==expected
 assert (s['protocol'],s['target'],s['steps'],s['cycles'])==(case['protocol'],case['target'],case['steps'],0)
 assert s['integration_settings']==dict(policy['settings'],**({'rate_tolerance':case['rate_tolerance']} if 'rate_tolerance' in case else {}))
 assert s['response_contract']=='stress-scope-0.1' and s['stress_scope']=='effective'
 controls=[0 if i==0 or s['target']==0 else s['target'] if i==s['steps'] else (s['target']*i)/s['steps'] for i in range(s['steps']+1)]
 assert s['loading']['controls_bits']==[struct.pack('>d',float(x)).hex() for x in controls]
node="""
import assert from 'node:assert/strict';import{readFileSync}from'node:fs';import{createLoading,normalizeLoading}from'./web/loading.mjs';import{validateScopedLaboratory}from'./web/laboratory-scope.mjs';
const freeze=JSON.parse(readFileSync(process.argv[1],'utf8'));const requests=JSON.parse(readFileSync(freeze.root+'/'+freeze.requests,'utf8')),catalogue=JSON.parse(readFileSync(freeze.catalogue,'utf8'));
for(const {specification:s}of requests){assert.deepEqual(createLoading(s),s.loading);assert.deepEqual(normalizeLoading(s),s.loading);validateScopedLaboratory(s,catalogue);}console.log('PASS: seven original producer controls/scoped specifications validated without engine.');
"""
r=subprocess.run(['node','--input-type=module','-e',node,str(P/'prospective-freeze-v2.json')],cwd=R,text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);print(r.stdout.strip())
r=subprocess.run(['node','--check',str(P/'run.mjs')],cwd=R,text=True,capture_output=True);assert r.returncode==0,r.stderr
spec=importlib.util.spec_from_file_location('original_ncl_assessor',R/f['assessor']);assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
old=assessor.assess(R/'docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1/results');assert old['passed'] is True
print('PASS:173pins/158relevant accepted runtime hashes/three exact durable artifacts/current14 regenerated catalogue; no build or compiled calls.')
print('PASS: unchanged seven requests/policy/example/defaults/control bits and original Decimal90 saved reference gate; initial callback/freeze-v1 bytes preserved.')
