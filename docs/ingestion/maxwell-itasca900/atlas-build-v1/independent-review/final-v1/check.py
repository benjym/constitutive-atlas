"""Saved-evidence replay only: never configures, builds, loads or executes compiled artifacts."""
import ast,hashlib,importlib.util,json,math,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
BASE=ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1';OBS=BASE/'observations';D=Path('/private/tmp/atlas-maxwell-current-v1/source')
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text())
results=load(BASE/'results.json');binding=results['binding'];mf=load(BASE/'results-manifest.json')['files']
for n,h in mf.items():assert sha((ROOT/n).read_bytes())==h,n
# Exact original source freeze, current runtime bytes and archived source bytes.
f=load(BASE/'freeze.json');rows={x['path']:x for x in f['files']}
for n,row in rows.items():
 b=(D/n).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes'],n
for n,h in f['runtime_source_manifest']['files'].items():assert sha((ROOT/n).read_bytes())==sha((D/n).read_bytes())==h,n
assert binding['source_manifest_sha256']==f['runtime_source_manifest']['sha256']
assert binding['model_sha256']==sha((D/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json').read_bytes())
assert binding['reference_policy_sha256']==sha((D/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_bytes())
prior=BASE/'independent-review';assert load(prior/'receipt.json')['decision']=='accepted'
for n,x in load(prior/'manifest.json')['files'].items():assert sha((ROOT/n).read_bytes())==x['sha256'],n
# All commands/logs frozen; only explicitly recorded cache environment retry differs.
commands=load(BASE/'prospective-commands.json');planhash=sha((BASE/'prospective-commands.json').read_bytes());ex=BASE/'execution'
for key,cmd in commands['commands'].items():
 r=load(ex/(key+'.json'));assert r['command']==cmd and r['cwd']==commands['cwd'] and r['plan_sha256']==planhash,key
 assert r['log_sha256']==sha((ex/(key+'.log')).read_bytes())
 assert r['exit_code']==(2 if key=='wasm_build' else 0),key
failure=(ex/'wasm_build.log').read_text();assert 'PermissionError' in failure and 'symbol_lists' in failure and '.lock' in failure
retry=load(ex/'wasm_build_retry.json');cache=load(ex/'wasm-cache-retry-freeze.json')
assert retry['command']==cache['command']==commands['commands']['wasm_build']
assert retry['environment_override']==cache['environment_override']=={'EM_CACHE':cache['destination_cache']}
assert cache['cwd']==commands['cwd'] and cache['source_flags_or_gate_changes'] is False
assert retry['exit_code']==0 and retry['log_sha256']==sha((ex/'wasm_build_retry.log').read_bytes())
for n,h in cache['initial_cache_files'].items():assert sha((Path(cache['destination_cache'])/n).read_bytes())==h,n
assert all(x['exit_code']==0 for x in load(ex/'toolchain.json'))
assert load(ex/'native_transactions.json')['started_unix']+load(ex/'native_transactions.json')['elapsed_seconds']<load(ex/'wasm_configure.json')['started_unix']
# Exact archive member set and bytes; read as data only.
archive=results['artifact_archive'];assert sha((ROOT/archive['path']).read_bytes())==archive['sha256']
with tarfile.open(ROOT/archive['path'],'r:gz') as tf:
 members=tf.getmembers();assert len(members)==len(archive['members'])==13
 assert {m.name for m in members}==set(archive['members'])
 saved={}
 for m in members:
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  b=tf.extractfile(m).read();row=archive['members'][m.name]
  assert len(b)==row['bytes'] and sha(b)==row['sha256'];assert b==(D.parent/m.name).read_bytes();saved[m.name]=b
 assert saved['native/generated/models.json']==saved['wasm/generated/models.json']
 assert saved['native/generated/models.hpp']==saved['wasm/generated/models.hpp']
 cat=json.loads(saved['wasm/generated/models.json']);assert cat['models']==[load(D/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json')]
 assert binding['catalogue_file_sha256']==sha(saved['wasm/generated/models.json'])
 assert binding['module_sha256']==sha(saved['wasm/maxwell.js']) and binding['wasm_sha256']==sha(saved['wasm/maxwell.wasm'])
 assert saved['wasm/maxwell.wasm'][:4]==b'\0asm'
 for backend in ['native','wasm']:
  flags=saved[backend+'/CMakeFiles/atlas_maxwell_solver.dir/flags.make'].decode();cfg=saved[backend+'/CMakeCache.txt'].decode()
  assert '-O3 -DNDEBUG -std=gnu++20' in flags and 'CMAKE_BUILD_TYPE:STRING=Release' in cfg
  assert str(D/'cmake/maxwell') in cfg
# Replay unchanged analytical assessor and reconstruct endpoint-dependent expected cases in memory.
sys.path.insert(0,str(D))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
package=module('final_maxwell_package',ROOT/'tools/build_maxwell_laboratory.py')
assert package.source_manifest()==f['runtime_source_manifest']
assert sha(json.dumps(cat['models'],sort_keys=True,separators=(',',':')).encode())==cat['sha256']
assert cat['sha256'].encode() in saved['wasm/generated/models.hpp']
checks=module('final_maxwell_checks',D/'tests/test_maxwell.py')
transactions=module('final_transactions',D/'docs/ingestion/maxwell-itasca900/integration-v1/check_transactions.py')
cases=load(D/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')['cases'];assert len(cases)==24
errors={};raw={};restarts={}
for backend in ['native','wasm']:
 main=load(OBS/(backend+'-raw.json'));errors[backend]=checks.assess_rows(cases,main)
 tc=transactions.cases_for(OBS/(backend+'-raw.json'));assert len(tc)==14
 assert tc==load(OBS/(backend+'-transaction-cases.json'))['cases']
 tr=load(OBS/(backend+'-transactions-raw.json'));te=transactions.assess(tc,tr)
 report=load(OBS/(backend+'-transactions.json'));assert report['passed'] is True and report['errors_Pa']==te and report['recovery_pairs']==6 and report['actual_endpoint_restarts']==2
 restarts[backend]=[]
 for ident,parent in [('restart-creep','creep-schedule'),('restart-relax','relaxation-schedule')]:
  c=next(c for c in tc if c['id']==ident);end=json.loads(next(r for r in main if r['id']==parent)['calls'][0]['stdout'])['points'][-1]
  s=c['specification'];assert s['initial']==end['state'] and s['initial_strain']==end['strain'] and s['initial_strain_rate']==end['strain_rate'] and s['start_time']==end['time']
  restarts[backend].append(s['start_time'])
 assert restarts[backend]==[4,8]
 assert sum(len(r['calls']) for r in main+tr)==76
 # Catalogue identity, explicit six-component states/strains/rates and transition null shape.
 for row in main+tr:
  for call in row['calls']:
   d=json.loads(call['stdout'])
   if d.get('ok'):
    assert d['catalogue_hash']==cat['sha256']
    assert len(d['initial'])==6
    for p in d.get('points',[]):
     assert len(p['state'])==len(p['strain'])==len(p['strain_rate'])==6
     assert all(x is None or type(x) in (int,float) and math.isfinite(x) for x in p['strain_rate'])
 raw[backend]=(main,tr)
# Use only the unchanged parity function/constants; omit its output-writing top-level loop.
source=(D/'docs/ingestion/maxwell-itasca900/integration-v1/compare_backends_v2.py').read_text();tree=ast.parse(source);prefix=[]
for node in tree.body:
 if isinstance(node,ast.For):break
 prefix.append(node)
ns={'__file__':str(D/'docs/ingestion/maxwell-itasca900/integration-v1/compare_backends_v2.py')};exec(compile(ast.Module(body=prefix,type_ignores=[]),'<saved-parity-function>','exec'),ns)
for ni,wi in zip(raw['native'],raw['wasm']):
 assert len(ni)==len(wi)
 for n,w in zip(ni,wi):
  assert n['id']==w['id'] and len(n['calls'])==len(w['calls'])==2
  for nc,wc in zip(n['calls'],w['calls']):assert nc['returncode']==wc['returncode'];ns['compare'](json.loads(nc['stdout']),json.loads(wc['stdout']))
p={'passed':True,'numeric_comparisons':ns['COUNT'],'maximum_stress_difference_Pa':ns['MAX_STRESS'],'maximum_strain_or_rate_difference':ns['MAX_STRAIN']}
assert p==load(OBS/'parity-results-v2.json')==results['parity']
# Four actual CLI results, complete source echo and independent reference policy.
preset_errors={}
for n,cid in commands['preset_mapping'].items():
 c=next(c for c in cases if c['id']==cid);s=load(D/'examples/maxwell'/f'{n}.json');d=load(BASE/'presets'/f'{n}.json')
 assert s==c['specification']==d['specification'];preset_errors[n]=checks.assess(c,d)
 for key in ['model','parameters','initial','initial_strain','initial_strain_rate','start_time','segments']:assert d[key]==s[key]
 assert d['catalogue_hash']==cat['sha256']
assert (BASE/'presets/creep.json').read_bytes()==(OBS/'cli-creep-result.json').read_bytes()
assert load(OBS/'native-transactions.json')['CLI_replay_exact'] is True
review_dir=Path(__file__).resolve().parent
assert load(review_dir/'cli-first.json')==load(review_dir/'cli-replay.json')==load(OBS/'cli-creep-result.json')
assert str(D/'cpp/include') in (review_dir/'wasm-includes_CXX.rsp').read_text()
assert str(D/'cpp/main.cpp.o') in (review_dir/'wasm-objects1.rsp').read_text()
assert json.loads(load(OBS/'native-transactions.json')['untimed_rejection_raw'])['ok'] is False
assert set(results['gates'])=={'native_references','wasm_references','transactions','parity','presets'} and all(v is True for v in results['gates'].values())
print(json.dumps({'passed':True,'saved_evidence_hashes':len(mf),'runtime_source_files':101,'archive_members':13,'cache_initial_files':len(cache['initial_cache_files']),'raw_calls_per_backend':76,'native_cli_presets':4,'main_max_errors_Pa':{b:{'direct':max(e[c['id']] for c in cases if c['ok'] and c['kind']=='direct'),'schedule_excluding_coarse_diagnostic':max(e[c['id']] for c in cases if c['ok'] and c['kind']=='schedule' and c['id']!='refine-coarse'),'coarse_diagnostic':e['refine-coarse'],'fine_refinement':e['refine-fine']} for b,e in errors.items()},'preset_errors_Pa':preset_errors,'restart_start_times':restarts,'parity':p,'reviewer_builds':0,'reviewer_compiled_calls':0},indent=2))
