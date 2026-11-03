"""Pure path/version reversal and existing rejection corpus under v2 paths."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import runpy
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACKET=ROOT/'docs/ingestion/vibe-2026/controlled-path-refresh-v1'
old=json.loads((PACKET/'plan-v4.json').read_text())
new=json.loads((PACKET/'plan-v5.json').read_text())
projection=json.loads((HERE/'controlled-path-projection-v1.json').read_text())
source=(ROOT/'tools/qualify_controlled_path_refresh.py').read_bytes()
archive=(HERE/'preimages/controlled-path-execution-v1/tools/qualify_controlled_path_refresh.py').read_bytes()
assert hashlib.sha256(archive).hexdigest()==projection['live_helper_sha256']
assert hashlib.sha256(source).hexdigest()==projection['hypothetical_projected_helper_sha256']
reverse=source.decode()
for item in reversed(projection['helper_literal_projection']):
 assert reverse.count(item['after'])==item['occurrences']
 reverse=reverse.replace(item['after'],item['before'])
assert reverse.encode()==archive
added={p['path']:p['sha256'] for p in projection['added_closure_inputs']}
assert new['source_closure'].keys()-old['source_closure'].keys()==added.keys()
assert old['source_closure'].keys()<=new['source_closure'].keys()
changed={k for k in old['source_closure'] if old['source_closure'][k]!=new['source_closure'][k]}
assert changed=={'tools/qualify_controlled_path_refresh.py'}
for name,digest in added.items():
 assert new['source_closure'][name]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
restored=deepcopy(new)
assert restored['identity']=='controlled-path-refresh-plan-v5'
restored['identity']=old['identity']
for name in added:del restored['source_closure'][name]
restored['source_closure']['tools/qualify_controlled_path_refresh.py']=old['source_closure']['tools/qualify_controlled_path_refresh.py']
for row in restored['commands']:
 row['argv']=[a.replace('.local/controlled-path-refresh-v2/','.local/controlled-path-refresh-v1/').replace('docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/','docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1/') for a in row['argv']]
assert restored==old
assert (json.dumps(restored,indent=2)+'\n').encode()==(PACKET/'plan-v4.json').read_bytes()
for name,digest in new['source_closure'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
# Reuse the exact old pure rejection study. Only its fake fixture directory
# names change in memory; all assertions and original historical guard checks
# remain byte-identical. It never imports a compiled module or runs a build.
original=PACKET/'check_source.py'
text=original.read_text()
assert text.count("'execution-v1'")==1 and text.count("'execution-v1/norsand'")==1
text=text.replace("'execution-v1'","'execution-v2'").replace("'execution-v1/norsand'","'execution-v2/norsand'")
exec(compile(text,str(original),'exec'),{'__file__':str(original),'__name__':'__pure_rejection_projection__'})
print(json.dumps(dict(status='pass-exact-literal-and-plan-reversal',closure=len(new['source_closure']),added=added,changed_old_pins=sorted(changed),original_plan_reverse_bytes=True,original_helper_reverse_bytes=True,compiled_calls=0),indent=2))
