from pathlib import Path
import gzip,hashlib,json,math
O=Path(__file__).resolve().parent;N=O.parent;ROOT=N.parents[2];R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');P=N/'recorded-explicit-state-actual-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
launch=json.loads((P/'launch.json').read_text());receipt=json.loads((P/'observer/receipt.json').read_text());report=json.loads((P/'report.json').read_text());assert report['ok'] and len(report['pairs'])==46
assert launch['source_sha256']==sha(R/'tools/test_recorded.mjs')=='64ce5390fedda14aaff03a44ee6794ced587be4359e7ae6b4fb92457eec0a459';assert launch['observer_sha256']=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e' and launch['argv']==receipt['argv']
for artifact in launch['runtime_artifacts']:
 f=ROOT/artifact['retained'];assert sha(f)==artifact['sha256'] and f.stat().st_size==artifact['bytes']
assert receipt['returncode']==receipt['reaped_returncode']==0 and receipt['mandatory_reap'] and receipt['status']=='passed' and receipt['cleanup_errors']==[]
for key in ['executable','stdout','stderr']:
 pin=receipt[key];f=Path(pin['path']);assert sha(f)==pin['sha256'] and f.stat().st_size==pin['bytes']
retained=json.loads(gzip.decompress((R/'catalogue/investigations/recorded-replay-api-v1/responses.json.gz').read_bytes()));restarts=json.loads(gzip.decompress((R/'catalogue/investigations/recorded-restarts-v1/responses.json.gz').read_bytes()));requests=[x['request'] for x in retained+restarts]+[json.loads((R/'protocols/recorded-dp-restart-run.json').read_text())]
proof=json.loads((N/'recorded-explicit-state-fix-v1/evidence/default-equivalence.json').read_text());defaults={x['model']:x['flattened_initial'] for x in proof};assert len(requests)==46
nums=0
# Original recorded checker compares every key, including counters, at1e-9; nothing excluded.
def compare(a,b):
 global nums
 if type(b) in [int,float]:
  assert type(a) in [int,float] and math.isfinite(a) and abs(a-b)<=1e-9*max(1,abs(b));nums+=1;return
 if isinstance(b,list):
  assert isinstance(a,list) and len(a)==len(b)
  for x,y in zip(a,b):compare(x,y)
  return
 if isinstance(b,dict):
  assert isinstance(a,dict) and set(a)==set(b)
  for k in b:compare(a[k],b[k])
  return
 assert type(a)==type(b) and a==b
for original,pair in zip(requests,report['pairs']):
 expected=original if original.get('initial') else dict(original,initial=defaults[original['model']]);assert pair['request']==expected
 a,b=pair['wasm'],pair['native'];compare(a,b)
 for key in ['failed_knot','material_trials','attempted_substeps','finite_difference_probes']:assert a[key]==b[key]
 assert a['ok']==b['ok']
 # Preserve optional restart response settings and all status/diagnostic fields exactly via compare.
freeze=json.loads((N/'current16-qualification-plan-v1/source-freeze-v1.json').read_text());assert sha(N/'current16-qualification-plan-v1/source-freeze-v1.json')=='eaf7ee22f2605dd2d4e366fa1c6a97ee33f46f16a8884c02a540903dba1af8d3';changed={}
for item in freeze['inputs']:
 p=Path(item['path']);actual=sha(p)
 if actual!=item['sha256']:
  relative=p.relative_to(R).as_posix();changed[relative]={'original':item['sha256'],'current':actual};archive=R/'catalogue/source-snapshots'/item['sha256']/relative;assert sha(archive)==item['sha256']
assert set(changed)=={'tools/test_numerics.mjs','tools/test_recorded.mjs'} and len(freeze['inputs'])==796
assert changed['tools/test_numerics.mjs']['current']=='8381f20d6523b28698bb0f951bbbf211161e1cf292091c1b96fb0841d057b146' and changed['tools/test_recorded.mjs']['current']==launch['source_sha256']
result={'status':'PASS','pairs':46,'missing_states_adapted':35,'explicit_requests_preserved':11,'recursive_numeric_comparisons':nums,'relative_budget':1e-9,'all_object_keys_compared':True,'exact_counter_comparisons':184,'observer_exit0_mandatory_reap':True,'unchanged_frozen_inputs':794,'historical_frozen_inputs':796,'declared_test_only_deltas':changed,'compiled_calls_by_reviewer':0}
(O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
