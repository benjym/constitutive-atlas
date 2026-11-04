"""Independent saved actual guard assessment; no process or artifact execution."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,tarfile,importlib.util,datetime
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent;P=B/'current-profile-guard-replay-preparation-v1';A=B/'current-profile-guard-replay-actual-v1';S=Path('/private/tmp/atlas-md1997-integrated-v1');checks=[]
def deny(event,args):
 if event in ('subprocess.Popen','os.system','os.posix_spawn','os.exec','os.fork'):raise RuntimeError('FORBIDDEN independent saved-only assessment')
sys.addaudithook(deny)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def check(n,ok):
 if not ok:raise RuntimeError(n)
 checks.append({'name':n,'passed':True})
check('actual packet exact',sha(A/'manifest.json')=='b568dd6aaeb27f714d559aa40ce88904e724d4ed683949da5ac30205cee2d184')
for n,h in read(A/'manifest.json')['files'].items():check('packet '+n,sha(A/n)==h)
inv=read(A/'archive-inventory.json');base=Path(inv['source'])
check('complete68member archive',inv['members']==len(inv['files'])==68)
with tarfile.open(A/'complete-actual-guards.tar.gz','r:gz') as tar:
 members=tar.getmembers();check('only canonical unique files',len(members)==68 and len({m.name for m in members})==68 and all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members))
 check('exact archive set',{m.name for m in members}==set(inv['files']))
 for m in members:
  data=tar.extractfile(m).read();v=inv['files'][m.name]
  check('archive '+m.name,len(data)==v['bytes']==m.size and hashlib.sha256(data).hexdigest()==v['sha256'] and (base/m.name).read_bytes()==data)
 check('899939 compressed archive bytes',(A/'complete-actual-guards.tar.gz').stat().st_size==899939)
plan=read(P/'plan.json');results=read(A/'results.json')
check('accepted plan pins',results['plan_review_manifest_sha256']=='99e944c84ae2e0d2051f05d2641595d69f3739a1fb3e07d9b59e2a9a6882b6f9' and results['plan_packet_manifest_sha256']=='7cca111279dd0c98475021676feb0f02e72f6dd1a1b29b731707c94110a11e8f')
spec=importlib.util.spec_from_file_location('saved_only_guard_runner',P/'run_one.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
preflight=r.verify(plan);check('current read-only preflight',preflight==read(P/'saved-preflight.json')['summary'])
processes=[]
for op in plan['operations']:
 profile=op['profile'];folder=Path(op['operation_directory']);row=read(folder/'process.json');processes.append(row)
 check(profile+' exact whole operation',row['operation']==op and row['packet_manifest_sha256']==results['plan_packet_manifest_sha256'])
 check(profile+' completed true integer exit0',row['passed'] is True and type(row['returncode']) is int and row['returncode']==0 and row['errors']==[] and not row.get('timeout'))
 check(profile+' unchanged pre/post',row['pre']==row['post']==preflight and results['operations'][profile]['pre']==results['operations'][profile]['post']==preflight)
 start=datetime.datetime.fromisoformat(row['start_utc']);end=datetime.datetime.fromisoformat(row['end_utc']);check(profile+' lifecycle',end>=start and type(row['elapsed_seconds']) in (float,int) and row['elapsed_seconds']>=0)
 for channel in ['stdout.raw','stderr.raw']:
  v=row[channel];check(profile+' binary '+channel,v['path']==str(folder/channel) and sha(folder/channel)==v['sha256'] and (folder/channel).stat().st_size==v['bytes'])
 for n,h in row['retained_outputs'].items():check(profile+' retained output '+n,sha(folder/n)==h)
 check(profile+' exact process pin',sha(folder/'process.json')==results['operations'][profile]['process_sha256'])
 check(profile+' original output gates',r.validate_outputs(op)==row['output_assessment']==results['operations'][profile]['output_assessment'])
 check(profile+' empty stderr',(folder/'stderr.raw').read_bytes()==b'')
check('serial operation timestamps',datetime.datetime.fromisoformat(processes[0]['end_utc'])<datetime.datetime.fromisoformat(processes[1]['start_utc']))
# The existing Python assessors are source-only. Do not call run/bundle/main.
sys.path.insert(0,str(S))
spec=importlib.util.spec_from_file_location('independent_saved_maxwell_assessor',S/'tests/test_maxwell.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
out=base/'maxwell/output';cases=read(S/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')['cases'];raw=read(out/'raw.json');report=read(out/'report.json')
errors=t.assess_rows(cases,raw)
check('24 original case assessments exact',len(cases)==len(raw)==24 and errors==report['reference_errors_Pa'])
check('48 complete calls',sum(len(x['calls']) for x in raw)==48 and all(len(x['calls'])==2 for x in raw))
for case,row in zip(cases,raw):check('case identity '+case['id'],row['id']==case['id'])
presets=read(out/'presets.json');mapping={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}
check('four exact named presets',[x['name'] for x in presets]==list(mapping))
for row in presets:
 case=next(c for c in cases if c['id']==mapping[row['name']]);source=read(S/'examples/maxwell'/(row['name']+'.json'))
 check('preset controls '+row['name'],source==case['specification'] and row['controls']=={**source,'solver':row['controls']['solver']} and all(row['controls']['solver'].get(k)==v for k,v in source['solver'].items()))
 check('full replay '+row['name'],row['result']==row['replayed_result'])
 check('analytical preset '+row['name'],t.assess(case,row['result'])==report['preset_errors_Pa'][row['name']])
commands=read(out/'commands.json');op=plan['operations'][0]
expected=[['node','--test','tests/test_maxwell_atlas_contract.mjs','tests/test_maxwell_atlas_runtime.mjs'],['node','tools/test_maxwell_wasm.mjs',str(Path(op['build'])/'maxwell.js'),str(S/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json'),str(out/'raw.json')],['node','tools/test_maxwell_public_presets.mjs',op['build'],str(out/'presets.json'),str(out/'identity.json')]]
for i,(row,argv) in enumerate(zip(commands,expected)):check('exact Node child '+str(i),row['command']==argv and type(row['returncode']) is int and row['returncode']==0 and row['timeout_seconds']==120 and row['stderr']=='' and not row.get('timeout'))
check('21 interface/lifecycle tests no skipped/cancelled','ℹ tests 21' in commands[0]['stdout'] and 'ℹ pass 21' in commands[0]['stdout'] and all('ℹ '+n+' 0' in commands[0]['stdout'] for n in ['fail','cancelled','skipped','todo']))
check('actual48 stdout declaration',commands[1]['stdout']=='Saved 48 raw calls from one Maxwell Wasm module.\n')
check('actual four public presets full replay declaration',commands[2]['stdout']=='PASS: four actual public presets, complete result validation and exact recomputed replay.\n')
check('top report exact stdout',read(base/'maxwell/stdout.raw')==report)
check('NorSand builder exact silent stdout',(base/'norsand/stdout.raw').read_bytes()==b'')
result={'identity':'independent-current-guard-actual-assessment-v1','reviewer_run':'/root/md1997_final_review','accepted':True,'passed':len(checks),'checks':checks,'preflight':preflight,'Maxwell_frozen_calls':48,'Maxwell_public_calls':8,'Maxwell_interface_tests':21,'NorSand':'guarded packaging only, original58+58 study retained not rerun','reviewer_compiled_calls':0,'builds':0}
(D/'current-guard-actual-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['accepted','passed','reviewer_compiled_calls']}))
