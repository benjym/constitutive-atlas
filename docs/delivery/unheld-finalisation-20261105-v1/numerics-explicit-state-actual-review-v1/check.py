from pathlib import Path
import gzip,hashlib,json,math
O=Path(__file__).resolve().parent;N=O.parent;ROOT=N.parents[2];P=N/'numerics-explicit-state-actual-v2';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
launch=json.loads((P/'launch.json').read_text());receipt=json.loads((P/'observer/receipt.json').read_text());report=json.loads((P/'report.json').read_text());assert report['status']=='passed' and len(report['pairs'])==17
assert launch['argv']==receipt['argv'] and launch['source_sha256']==sha(R/'tools/test_numerics.mjs')=='8381f20d6523b28698bb0f951bbbf211161e1cf292091c1b96fb0841d057b146'
assert launch['observer_sha256']=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e' and launch['timeout']==1800
assert receipt['returncode']==receipt['reaped_returncode']==0 and receipt['mandatory_reap'] and receipt['status']=='passed' and receipt['cleanup_errors']==[]
for key in ['stdout','stderr','executable']:
 pin=receipt[key];f=Path(pin['path']);assert sha(f)==pin['sha256'] and f.stat().st_size==pin['bytes']
for artifact in launch['runtime_artifacts']:
 p=ROOT/artifact['retained'];assert sha(p)==artifact['sha256'] and p.stat().st_size==artifact['bytes']
rows=json.loads(gzip.decompress((R/'catalogue/investigations/update-tangent-v1/results.json.gz').read_bytes()))[:5];initial={r['model']:r['parent'] for r in rows}
numbers=0
# Exactly the unchanged original recursive numeric comparison; elapsed_ms is the sole excluded property.
def compare(a,b):
 global numbers
 if type(b) in [int,float]:
  assert type(a) in [int,float] and math.isfinite(a) and abs(a-b)<=1e-7*max(1,abs(b));numbers+=1;return
 if isinstance(b,list):
  assert isinstance(a,list) and len(a)==len(b)
  for x,y in zip(a,b):compare(x,y)
  return
 if isinstance(b,dict):
  assert isinstance(a,dict) and set(a)==set(b)
  for k in b:
   if k!='elapsed_ms':compare(a[k],b[k])
  return
 assert type(a)==type(b) and a==b
expected_names=[]
for row in rows:expected_names.extend(['configured-run/'+row['model'],'default-tangent/'+row['model'],'configured-tangent/'+row['model']])
expected_names+=['limited-run','invalid-settings'];assert [x['name'] for x in report['pairs']]==expected_names
settings={'version':'incremental-settings-0.1','norm':'scaled_component_max','residual_tolerance':1e-11,'rate_tolerance':1e-7,'max_iterations':60,'max_depth':14,'max_substeps':5000,'max_backtracks':8}
for pair in report['pairs']:
 a,b=pair['wasm'],pair['native'];compare(a,b);assert pair['returncode']==(0 if b['ok'] else 1)
 argv=pair['argv'];model=argv[argv.index('--model')+1];assert argv[argv.index('--initial')+1]==','.join(str(x) for x in initial[model])
 if pair['name'].startswith('configured-run/'):
  assert a['ok'] and b['ok'] and a['integration_settings']==settings and b['integration_settings']==settings
 elif '-tangent/' in pair['name']:
  assert a['ok'] and b['ok'] and a['tangent_ok'] and b['tangent_ok']
 elif pair['name']=='limited-run':assert not a['ok'] and not b['ok'] and len(a['points'])==len(b['points'])==1
 else:assert not a['ok'] and not b['ok'] and a['message']==b['message']=='invalid integration settings'
stop=N/'numerics-explicit-state-actual-v1/preflight-stop.json';assert stop.is_file();cwd=(P/'unrelated-pdf-35640.raw').read_text();assert 'n/Users/bmar5496/code/civl2410/book' in cwd;assert launch['active_compiler_or_material_processes_observed']==[] and len(launch['unrelated_identified_documentation_processes_preserved'])==1
result={'status':'PASS','pairs':17,'recursive_numeric_comparisons':numbers,'successful_configured_runs':5,'successful_tangents':10,'limited_failure_points':1,'invalid_failure':'invalid integration settings','exact_keys_except_elapsed_value':True,'source_sha256':launch['source_sha256'],'observer_mandatory_reap_exit0':True,'retained_v1_preflight_stop_sha256':sha(stop),'unrelated_pdf_cwd_evidence_sha256':sha(P/'unrelated-pdf-35640.raw'),'compiled_calls_by_reviewer':0}
(O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
