"""Read-only Git/source projection; writes design evidence only, never live inputs."""
from pathlib import Path
import hashlib
import json
import subprocess
from copy import deepcopy
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
UPSTREAM = 'ac22788b918a47c837e61ddd76bde5894b35cc5e'
BASE = '31125e2e809dad1af8dd30805af7b8c2937197d4'
PACKET = 'docs/ingestion/vibe-2026/controlled-path-refresh-v1/'
helper_path = ROOT/'tools/qualify_controlled_path_refresh.py'
source = helper_path.read_text()
sha = lambda b:hashlib.sha256(b).hexdigest()
changes = [
    ("PLAN = PACKET/'plan-v4.json'", "PLAN = PACKET/'plan-v5.json'"),
    ("identity='controlled-path-refresh-plan-v4'", "identity='controlled-path-refresh-plan-v5'"),
    ("PACKET/'execution-v1'", "PACKET/'execution-v2'"),
    (".local/controlled-path-refresh-v1/", ".local/controlled-path-refresh-v2/"),
]
projected = source
replacements = []
for before,after in changes:
    count = projected.count(before)
    assert count > 0
    replacements.append(dict(before=before,after=after,occurrences=count))
    projected = projected.replace(before,after)
reverse = projected
for before,after in reversed(changes):
    reverse = reverse.replace(after,before)
assert reverse == source
assert "INTERFACE+'execution-v1/check_parity_v2.py'" in projected
assert "INTERFACE+'execution-v1/source-freeze-v2.json'" in projected
old = json.loads((ROOT/PACKET/'plan-v4.json').read_text())
new = deepcopy(old)
new['identity'] = 'controlled-path-refresh-plan-v5'
new['source_closure']['tools/qualify_controlled_path_refresh.py'] = sha(projected.encode())
added=[]
for name in ['models/s-clay1.json','tests/fixtures/current-sixteen-sclay1-v1.json']:
    blob=subprocess.check_output(['git','show',UPSTREAM+':'+name],cwd=ROOT)
    assert name not in old['source_closure']
    added.append(dict(path=name,sha256=sha(blob),bytes=len(blob)))
    new['source_closure'][name]=sha(blob)
new['source_closure']=dict(sorted(new['source_closure'].items()))
for row in new['commands']:
    row['argv']=[a.replace('.local/controlled-path-refresh-v1/','.local/controlled-path-refresh-v2/').replace(PACKET+'execution-v1/',PACKET+'execution-v2/') for a in row['argv']]
restored=deepcopy(new)
restored['identity']=old['identity']
for pin in added:del restored['source_closure'][pin['path']]
restored['source_closure']['tools/qualify_controlled_path_refresh.py']=old['source_closure']['tools/qualify_controlled_path_refresh.py']
for row in restored['commands']:
    row['argv']=[a.replace('.local/controlled-path-refresh-v2/','.local/controlled-path-refresh-v1/').replace(PACKET+'execution-v2/',PACKET+'execution-v1/') for a in row['argv']]
assert restored==old
core = subprocess.check_output(['git','diff','--name-only',BASE,UPSTREAM,'--','atlas','schemas','cpp','cmake'],cwd=ROOT,text=True).splitlines()
assert core==[]
data=dict(status='design-only-not-an-executable-qualification-plan',upstream_commit=UPSTREAM,base_commit=BASE,live_helper_sha256=sha(source.encode()),hypothetical_projected_helper_sha256=sha(projected.encode()),helper_literal_projection=replacements,original_interface_gates_still_execution_v1=True,upstream_core_changes=core,added_closure_inputs=added,old_closure_count=len(old['source_closure']),hypothetical_new_closure_count=len(new['source_closure']),full_plan_reverse_structure_identity=True,all_numeric_cases_gates_settings_and_other_old_pins_unchanged=True,requires_merged_checkout_recompute_and_independent_review=True,compiled_calls=0,live_input_writes=0)
with (HERE/'controlled-path-projection-v1.json').open('x') as output:json.dump(data,output,indent=2);output.write('\n')
print(json.dumps(data,indent=2))
