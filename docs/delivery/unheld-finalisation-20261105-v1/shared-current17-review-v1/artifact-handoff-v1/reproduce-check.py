"""Readonly exact evidence checks; no artifact/tool invocation."""
from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;O=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/shared640-artifact-binding-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=json.loads((O/'handoff.json').read_text());checks=[]
def ok(v,n):
 if not v:raise AssertionError(n)
 checks.append(n)
def verify(p):ok(sha(Path(p['path']))==p['sha256'],'pin '+p['path']);ok(Path(p['path']).stat().st_size==p['bytes'],'size '+p['path'])
for p in list(h['artifacts'].values())+list(h['build_tools'].values())+h['raw_provenance']:verify(p)
for row in h['retention_map']:
 verify(row['original']);verify(row['retained']);ok(row['original']['sha256']==row['retained']['sha256'],'durable byte equality '+row['original']['path'])
for row in h['actual_dependency_source_bindings']:verify(row['retained640_source'])
for backend in('native','wasm'):
 b=h['builds'][backend];ok(b['returncode']==b['configure_returncode']==0,'genuine recovered statuses '+backend)
 ok(b['original_build_terminal']['exitCode']==0 and b['original_configure_terminal']['exitCode']==0,'original terminal statuses '+backend)
 ok(b['argv'][b['argv'].index('--target')+1]=='atlas_solver'and b['argv'][b['argv'].index('--parallel')+1]=='1','original serial solver argv '+backend)
 for p in h['generated'][backend].values():verify(p)
 verify(b['current_object']);verify(b['current_scalar_library']);verify(b['resolved_compiler'])
for name,digest in h['source_sha256'].items():ok(sha(Path(h['source_context_manifest']['path']).parent/'source'/name)==digest,'late current808 source '+name)
ok(len(h['source_sha256'])==808,'current808 count')
ok(h['prior_inventory']['count']==146 and h['prior_inventory']['matching_current640']==145,'historical146145match')
ok(h['prior_inventory']['not_in808']==['tests/test_solver.cpp'],'original numerical-only source absentcontext disclosed')
ok(h['cpp_main']['historical146_prebuild_covered']is False,'no fabricated cppmain prebuildhash')
ok(h['cpp_main']['current640']['sha256']==h['cpp_main']['retained702']['sha256'],'702640 cppmain exact')
ok(h['known_original_failed_build_terminal']['exitCode']==2,'original wasm failure preserved')
ok(h['historical_source_HEAD_observation']['revision']=='30234bb0dd5995f49d3aaba669aaf9baa1336e3d','historical30234 HEAD not relabeled640')
ok(h['measurement_time_utc']and h['provenance_class'].startswith('late-readonly'),'late class explicit')
for role in('wasm','module'):
 row=h['published_wasm_equality'][role];verify(row['retained_actual_uploaded_asset']);ok(row['borrowed_build']['sha256']==row['retained_actual_uploaded_asset']['sha256']==row['upload_manifest_row']['sha256'],'actual uploaded '+role+' equal build')
for backend in('native','wasm'):ok(h['generated'][backend]['json']['sha256']==h['actual_http_catalogue']['sha256'],'generated17 equals actual HTTP '+backend)
old=json.loads((O/'raw/prior-numerical/source-before.json').read_text());after=json.loads((O/'raw/prior-numerical/source-after.json').read_text());ok(old==after,'genuine original146 beforeafter equal')
(Q/'reproduced-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'no_executable_invocation':True,'no_prebuild_provenance_fabricated':True},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
