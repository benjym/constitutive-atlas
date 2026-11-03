"""Source checks for the restricted sequential workflow; no YAML module execution."""
from pathlib import Path
import json,hashlib,re,ast
R=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');O=Path(__file__).resolve().parent
p=R/'.github/workflows/controlled-time.yml';s=p.read_text();checks=[]
def check(x,label):
 if not x:raise AssertionError(label)
 checks.append(label)
check(s.count('    runs-on:')==1,'single execution job')
check('matrix:' not in s,'no parallel job matrix')
check('continue-on-error' not in s,'no failure bypass')
check('contents: read' in s,'read-only repository permission')
check('cancel-in-progress: false' in s,'no cancellation of active qualification for newer run')
builds=[x.strip() for x in s.splitlines() if x.strip().startswith('cmake --build')]
check(len(builds)==4,'exactly four explicit builds')
for x in builds:check('--target atlas_controlled_time_capability --parallel 1' in x,'single named serial target '+x.split()[2])
markers=['Build synthetic native target serially','Qualify all six synthetic native groups with corrected corpus','Build exact VIBE native target serially','Qualify native 32 rates and eight full sampled histories first','Build matching synthetic Wasm target serially','Qualify matching synthetic Wasm corpus and transactional gates','Build exact VIBE Wasm target serially','Qualify Wasm model against independent references and exact native peer']
positions=[s.index(x) for x in markers];check(positions==sorted(positions),'native-first strict qualification dependency order')
check(s.count('run_native_v2.py --execute -v')==1,'all six native groups selected through corrected source-only wrapper')
check(s.count('run_wasm_v2.mjs --execute')==1 and 'node --experimental-vm-modules ' in s,'matching corrected Wasm wrapper explicit execution')
check(s.count('--plan docs/ingestion/vibe-2026/controlled-time-ci-v1/plan-v3.json')==1,'native uses portable plan')
check(s.count('plan-v3.json')==2,'native and Wasm use same portable plan')
check(s.count('numerical-qualification-v1/source-manifest-v2.json')==2,'model collectors retain exact reviewed source freeze')
check('"$RUNNER_TEMP/controlled-time-ci/wasm-model" "$RUNNER_TEMP/controlled-time-ci/native-model"' in s,'Wasm requires exact native peer')
check(s.count('if: always()')==2,'failure capture and artifact upload always run')
check('actions/upload-artifact@v4' in s and '${{ runner.temp }}/controlled-time-ci/' in s,'raw failure logs and output receipts retained')
check('compile_commands.json' in s and 'CMakeCache.txt' in s and '/generated/' in s,'generated/build provenance retained')
check(s.count('set -euo pipefail')==s.count('      run: |-'),'every run block checks subprocess failure through tee')
check(all('tee ' in block for block in s.split('      run: |-')[1:]),'all source/build/test/capture run phases tee to durable log')
check('libatlas_controlled_time_capability.so' in s and 'atlas_controlled_time_capability.wasm' in s and 'atlas_controlled_time_capability.mjs' in s,'actual native and Wasm engines retained')
helper=R/'tools/check_controlled_time_ci.py';ast.parse(helper.read_text())
(O/'workflow-results.json').write_text(json.dumps(dict(scope='source wiring only; no workflow/build/material execution',checks=checks,count=len(checks),workflow_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),compiled_calls=0),indent=2)+'\n')
print('Workflow source checks:',len(checks))
