"""Replay rollout records and check current source identity; no backend calls."""
from pathlib import Path
import json,hashlib,struct,sys
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent;r=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read(s/'manifest.json').items():assert sha(s/n)==h,n
for n,h in read(s/'source-pins.json').items():assert sha(r/n)==h,n
root=read(s/'root-browser-results.json');assert root['status']=='passed'and len(root['pairs'])==101 and root['same_instance_wasm_export_import_replays']==90
package=read(s/'package-results.json');assert package['status']=='passed'and len(package['models'])==9
assert package['catalogue_hash']==root['catalogue_hash']
for row in package['models']:
 assert row['result']['ok']is True and len(row['result']['points'])==101
 assert row['specification']['loading']['version']=='laboratory-controls-0.1'
 assert row['result']['api_version']=='experimental-laboratory-controls-0.1'
exact=read(s/'ui-current-export.json');assert exact['schema_version']=='0.2'and exact['result']['ok']is True
assert read(s/'ui-legacy-import.json')['schema_version']=='0.1'
assert read(s/'preexisting-archive-coverage-failures.json')['count']==19
assert 'FAILED (failures=19)'in(s/'evidence.stderr.txt').read_text()
assert 'All 628 built experiments passed'in(s/'experiments.stdout.txt').read_text()
assert 'Reproducible · current'in(s/'ui-final-state.txt').read_text()
assert '100 increments'in(s/'ui-final-state.txt').read_text()
def loads(text):
 def number(kind,value):return ('binary64',kind,struct.pack('>d',float(value)).hex())
 return json.loads(text,parse_int=lambda v:number('integer',v),parse_float=lambda v:number('real',v))
a=loads((s/'root-browser-results.json.raw.json').read_text());b=loads((r/'catalogue/investigations/laboratory-q-cancellation-v1/post/backend-results.json.raw.json').read_text());assert len(a)==len(b)==382
for x,y in zip(a,b):
 assert x['role']==y['role']and x['name']==y['name']and x['args']==y['args']
 u=loads(x['raw']);v=loads(y['raw']);u.pop('elapsed_ms',None);v.pop('elapsed_ms',None);assert u==v
print(json.dumps({'saved_replay_passed':True,'current_source_match':True,'paired_cases':101,'raw_calls_exact_to_frozen_q_study_except_elapsed':382,'packaged_models':9,'packaged_experiments':628,'retained_preexisting_archive_coverage_failures':19,'candidate_calls':0},indent=2))
