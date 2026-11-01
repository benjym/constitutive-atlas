"""Independent prospective checks: source, pure tests, JS mock responses; no Wasm."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile
from unittest.mock import patch
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
PACKET=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args):
 r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
 assert r.returncode==0,(args,r.stdout,r.stderr)
 return r.stdout
if (Path(__file__).parent/'inputs.json').exists():
 for p,h in json.loads((Path(__file__).parent/'inputs.json').read_text()).items():assert sha(ROOT/p)==h,p
for p,h in json.loads((PACKET/'source-bindings-v2.json').read_text()).items():assert sha(ROOT/p)==h,p
sidecar=json.loads((PACKET/'source-archive-map.json').read_text())
for p,h in sidecar['documents'].items():assert sha(ROOT/p)==h,p
for item in sidecar['entries']:assert sha(ROOT/item['archived_path'])==item['sha256']
print(command(['node','--test','tests/test_maxwell_atlas_contract.mjs','tests/test_maxwell_atlas_runtime.mjs']))
presets=json.loads(command(['node','--input-type=module','-e',"import {preset,presetNames,solver} from './web/maxwell-atlas-contract.mjs';console.log(JSON.stringify({solver,presets:Object.fromEntries(presetNames.map(n=>[n,preset(n)]))}));"]))
cases=json.loads((ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text())['cases']
assert len(cases)==24
mapping={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}
for name,caseid in mapping.items():
 source=json.loads((ROOT/f'examples/maxwell/{name}.json').read_text())
 assert source==next(c['specification'] for c in cases if c['id']==caseid)
 assert presets['presets'][name]==dict(source,solver=presets['solver'])
 assert all(presets['solver'][k]==v for k,v in source['solver'].items())
print('PASS: 24 unchanged cases; all four exact sources normalize only by complete fixed solver defaults.')
saved=json.loads((ROOT/'docs/ingestion/maxwell-itasca900/atlas-integration-v1/browser-exports/browser-relaxation.json').read_text())
for mode in ['malformed','replay-mismatch']:
 with tempfile.TemporaryDirectory(prefix='maxwell-review-js-') as tmp:
  folder=Path(tmp);(folder/'generated').mkdir()
  catalogue={'sha256':saved['provenance']['catalogue_hash']}
  (folder/'generated/models.json').write_text(json.dumps(catalogue))
  (folder/'identity.json').write_text(json.dumps(saved['provenance']))
  module='export default async function(){let calls=0;return {ccall(name){if(name===\"atlas_describe\")return '+json.dumps(json.dumps(catalogue))+';calls++;'
  if mode=='malformed':module+='return \"{malformed\";'
  else:module+='const result='+json.dumps(saved['result'])+';if(calls===2){result.points.at(-1).state[0]+=1;result.points.at(-1).observables[0]+=1;}return JSON.stringify(result);'
  module+='}};}'
  (folder/'maxwell.js').write_text(module)
  output=folder/'presets.json'
  r=subprocess.run(['node','tools/test_maxwell_public_presets.mjs',str(folder),str(output),str(folder/'identity.json')],cwd=ROOT,text=True,capture_output=True)
  assert r.returncode!=0
  observations=json.loads(Path(str(output)+'.raw.json').read_text())
  assert observations[0]['function']=='atlas_describe'
  assert len(observations)==(2 if mode=='malformed' else 3)
  if mode=='malformed':assert observations[-1]['stdout']=='{malformed'
  else:assert 'Replayed complete result differs' in r.stderr
  assert not output.exists()
print('PASS: JS mock malformed first response and consistent replay mutation fail with every raw observation retained.')
spec=importlib.util.spec_from_file_location('maxwell_ci_review',ROOT/'tools/check_maxwell_ci.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory(prefix='maxwell-review-python-') as tmp:
 output=Path(tmp)/'timeout'
 with patch.object(mod,'bundle',return_value={'mock':'pure'}),patch.object(mod.subprocess,'run',side_effect=subprocess.TimeoutExpired(['mock'],120,output=b'partial stdout',stderr=b'partial stderr')):
  try:mod.run(Path(tmp)/'unused-build',output)
  except subprocess.TimeoutExpired:pass
  else:raise AssertionError('timeout accepted')
 records=json.loads((output/'commands.json').read_text());assert records[-1]['timeout'] is True and records[-1]['stdout']=='partial stdout'
 assert not (output/'report.json').exists()
 paths=json.loads((output/'inputs.json').read_text())['files']
 for p in ['tools/build_maxwell_laboratory.py','tests/test_maxwell_atlas_contract.mjs','tests/test_maxwell_atlas_runtime.mjs',*[f'examples/maxwell/{n}.json' for n in mapping]]:assert p in paths,p
 try:mod.run(Path(tmp)/'unused-build',output)
 except ValueError:pass
 else:raise AssertionError('existing output accepted')
print('PASS: pure injected timeout retains logs, emits no pass report, binds expanded inputs and refuses existing evidence.')
