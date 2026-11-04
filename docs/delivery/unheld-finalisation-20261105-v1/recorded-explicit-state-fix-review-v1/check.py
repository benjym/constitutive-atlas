from pathlib import Path
import gzip,hashlib,json
O=Path(__file__).resolve().parent;P=O.parent/'recorded-explicit-state-fix-v1';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'manifest.json')=='58b3c848b576de9625e0f47802c5f01a05a3bf58729b65670b3a0c236d812a9c'
for x in json.loads((P/'manifest.json').read_text())['files']:assert sha(P/x['path'])==x['sha256'] and (P/x['path']).stat().st_size==x['bytes']
delta=json.loads((P/'source-delta.json').read_text())['files'];assert len(delta)==1 and delta[0]['path']=='tools/test_recorded.mjs';assert sha(R/'tools/test_recorded.mjs')==delta[0]['preimage_sha256']=='45133e86775c8c8aafb2d4421b6e52b5ae61afea55179a0ba77784721803321e';assert sha(P/'proposed/tools/test_recorded.mjs')==delta[0]['sha256']=='64ce5390fedda14aaff03a44ee6794ced587be4359e7ae6b4fb92457eec0a459'
old=(P/'original/tools/test_recorded.mjs').read_text();assert old==(R/'tools/test_recorded.mjs').read_text();new=(P/'proposed/tools/test_recorded.mjs').read_text();start='  // Preserve the retained legacy requests;';end='   const {controls,knots}=recordedWire(s)'
assert new[:new.index(start)]+"  for(const {request:s} of [...retained,...restartRetained,{request:example}]){\n"+new[new.index(end):]==old
mapline=next(x for x in new.splitlines() if x.strip().startswith('const retainedInitialExamples='));state_map=json.loads(mapline.split('=',1)[1].rstrip(';'))
proof=json.loads((P/'evidence/default-equivalence.json').read_text());assert set(state_map)=={x['model'] for x in proof}
for row in proof:
 for kind,version in [('legacy','0.1'),('current','0.3')]:
  modelpath=P/'evidence'/kind/(row['model']+'.json');assert sha(modelpath)==row[kind+'_sha256'];m=json.loads(modelpath.read_text());assert m['schema_version']==version
  flat=[v for f in m['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])];assert flat==row['flattened_initial']==state_map[row['model']]
 allcurrent=R/'models'/(row['model']+'.json');assert sha(allcurrent)==row['current_sha256']
requests=[]
for path in ['catalogue/investigations/recorded-replay-api-v1/responses.json.gz','catalogue/investigations/recorded-restarts-v1/responses.json.gz']:
 assert (P/'evidence'/path).read_bytes()==(R/path).read_bytes();requests.extend(x['request'] for x in json.loads(gzip.decompress((R/path).read_bytes())))
p='protocols/recorded-dp-restart-run.json';assert (P/'evidence'/p).read_bytes()==(R/p).read_bytes();requests.append(json.loads((R/p).read_text()))
assert len(requests)==46;missing=[x for x in requests if 'initial' not in x];explicit=[x for x in requests if 'initial' in x];assert len(missing)==35 and len(explicit)==11;assert all(x['initial'] for x in explicit)
assert all(x['model'] in state_map for x in missing)
assert "retainedRequest.initial?retainedRequest:{...retainedRequest,initial:[...retainedInitialExamples[retainedRequest.model]]}" in new
assert 'Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(b))' in new
assert "['failed_knot','material_trials','attempted_substeps','finite_difference_probes']" in new
result={'status':'PASS','manifest_members':36,'only_added_loop_adapter':True,'all_other_bytes_gates_unchanged':True,'original_pair_count':46,'missing_initial_requests':35,'preserved_explicit_requests':11,'legacy_current_state_map_exact':5,'original_1e9_inverse_comparison_budget_unchanged':True,'original_fixtures_unchanged':True,'compiled_calls_by_reviewer':0}
(O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
