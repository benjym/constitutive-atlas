"""Independently assess saved actual results/bindings. Never load compiled modules."""
from pathlib import Path
import json,hashlib,sys,math,subprocess,tempfile
W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');O=Path(__file__).resolve().parent;P=W/'docs/ingestion/vibe-2026/controlled-path-refresh-v1';E=P/'execution-v1';sys.path.insert(0,str(W))
from atlas.compiler import generate
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
plan=load(P/'plan-v4.json');checks=[];statistics={};allinputs=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def finite(v):return type(v) in (float,int) and math.isfinite(v)
def entry(p):return dict(path=str(p.relative_to(W)),sha256=sha(p),bytes=p.stat().st_size)
check(sha(P/'plan-v4.json')=='8098b8b8cf2863823035277b704a4d4659589020273ae7492c7d12a9e5d1f09b','same accepted prospective plan')
for n,h in plan['source_closure'].items():check(sha(W/n)==h,'actual current source closure '+n)
run=load(E/'run.json');check(run['plan_sha256']==sha(P/'plan-v4.json'),'actual run uses accepted plan')
previous=0;commandrows=[]
for row in plan['commands']:
 p=E/(row['id']+'.receipt.json');r=load(p);log=W/r['log']['path']
 check(r['returncode']==0,row['id']+' genuine zero exit')
 check(r['plan_sha256']==sha(P/'plan-v4.json'),row['id']+' exact plan binding')
 check(r['argv']==[x.replace('$ROOT',str(W)) for x in row['argv']],row['id']+' original exact command args')
 check(sha(log)==r['log']['sha256'],row['id']+' immutable raw stdout/stderr log')
 check(r['started_unix']>=previous and r['finished_unix']>=r['started_unix'],row['id']+' sequential nonoverlapping observations');previous=r['finished_unix']
 commandrows.append(dict(id=row['id'],receipt=entry(p),log=entry(log)));allinputs.extend([entry(p),entry(log)])
check(len(commandrows)==22,'all22 frozen commands observed and passed')
contracts=(E/'contracts.log').read_text();check('Ran 25 tests' in contracts and 'OK (skipped=3)' in contracts,'original contract suite 22pass plus3 optional native-state tests explicitly skipped')
for key in ['norsand','interface2016']:
 engine=E/key/'engine';pending=load(engine/'qualification-pending.json');b=pending['binding']
 check(pending['implementation_run']==run['implementation_run'],key+' actual implementation identity')
 check(pending['status']=='passed-original-backend-gates-pending-independent-review',key+' no claimed preexisting build acceptance')
 check(b['plan']==dict(path='docs/ingestion/vibe-2026/controlled-path-refresh-v1/plan-v4.json',sha256=sha(P/'plan-v4.json')),key+' exact prospective plan')
 check(b['source_closure']==plan['source_closure'],key+' entire248pin closure exact')
 check(b['model_sha256']==sha(W/plan['definitions'][key][0]),key+' approved model exact')
 for group,root in [('artifacts',engine),('generated',engine/'generated'),('build_metadata',engine),('results',W),('commands',W)]:
  for n,h in b[group].items():
   p=root/n;check(sha(p)==h,key+' exact actual '+group+' '+n);allinputs.append(entry(p))
 check(b['generated']==b['native_generated'],key+' native/Wasm generated hashes identical')
 for name,h in b['native_generated'].items():check(sha(W/'.local/controlled-path-refresh-v1'/f'{key}-native'/'generated'/name)==h,key+' native generated actual retained build '+name)
 with tempfile.TemporaryDirectory(prefix='independent-generation-',dir=O) as tmp:
  generate(tmp,[W/p for p in plan['definitions'][key]])
  for n,h in b['generated'].items():check(sha(Path(tmp)/n)==h,key+' current compiler independently regenerates exact '+n)
 for backend in ['native','wasm']:
  entries=load(engine/'build-metadata'/backend/'compile_commands.json');api=[x for x in entries if str(x['file']).endswith('path_api.cpp')]
  check(len(api)==1,key+' '+backend+' actual generated translation unit')
  cmd=api[0].get('command',' '.join(api[0].get('arguments',[])))
  check('-fno-fast-math' in cmd and '-ffp-contract=off' in cmd,key+' '+backend+' original strict floating compiler flags')
  check(str(W) in cmd,key+' '+backend+' exact checkout compiler command')
 allinputs.append(entry(engine/'qualification-pending.json'))
 check(pending['gates']==plan['gates'][key] and b['model']==plan['models'][key],key+' exact original gate inventory and model')
 check(set(b['artifacts'])=={'native/'+plan['native_library'],'atlas_path_capability.mjs','atlas_path_capability.wasm'},key+' exact complete native/Wasm artifact set')
 check(set(b['generated'])=={'path_catalogue.json','path_models.hpp','path_api.cpp'},key+' exact generated source set')
 check(set(b['commands'])=={str(Path('docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1')/(row['id']+ext)) for row in plan['commands'] for ext in ['.receipt.json','.log']},key+' complete22commands and22logs bound')
 resultnames={'native.json','wasm.json'} if key=='norsand' else {'native.json','wasm.json','native-check.json','wasm-check.json','parity.json'}
 check(set(b['results'])=={str(Path('docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1')/key/n) for n in resultnames},key+' complete original result and checker report set')
 check(set(b['build_metadata'])=={'build-metadata/'+backend+'/'+n for backend in ['native','wasm'] for n in ['CMakeCache.txt','compile_commands.json']},key+' complete native/Wasm build metadata')
 # Independently assess every output from saved actual C ABI requests.
 native=load(E/key/'native.json');wasm=load(E/key/'wasm.json')
 reqfile=W/('docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json' if key=='norsand' else 'docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-requests.json')
 req=load(reqfile);check(native['request_sha256']==wasm['request_sha256']==sha(reqfile),key+' both actual reports exact frozen request input')
 check(native['library_sha256']==b['artifacts']['native/'+plan['native_library']],key+' actual native report exact library')
 check(wasm['module_sha256']==b['artifacts']['atlas_path_capability.mjs'] and wasm['wasm_sha256']==b['artifacts']['atlas_path_capability.wasm'],key+' actual Wasm report exact module and binary')
 count=58 if key=='norsand' else 59
 check(len(native['rows'])==len(wasm['rows'])==len(req['requests'])==count,key+' complete case count')
 if key=='norsand':
  stats=[]
  for backend,report in [('native',native),('wasm',wasm)]:
   errors=[];success=0;rejected=0
   for q,r in zip(req['requests'],report['rows']):
    check(r['id']==q['id'] and type(r['status']) is int and r['status']==q['expected_status'],key+' '+backend+' exact status '+q['id'])
    check(len(r['state'])==len(q['state']) and len(r['observables'])==q['observable_count'] and all(map(finite,r['state']+r['observables']+[r['coordinate']])),key+' '+backend+' finite full output '+q['id'])
    if not r['status']:
     rejected+=1;check(r['state']==[-1234567.]*len(q['state']) and r['observables']==[-1234567.]*q['observable_count'] and r['coordinate']==-7654321.,key+' '+backend+' exact failed sentinels '+q['id']);continue
    success+=1;err=max(abs(x-y) for x,y in zip(r['state'],q['expected_state']))
    if 'expected_observables' in q:err=max(err,max(abs(x-y)/s for x,y,s in zip(r['observables'],q['expected_observables'],q['observable_scales'])))
    bound=2e-7 if q.get('analytical') else 2e-11
    check(err<=bound,key+' '+backend+' original independent component bound '+q['id']);errors.append(err)
    check(r['coordinate']==q['coordinate']+q['progress'],key+' '+backend+' exact coordinate '+q['id'])
    if q['progress']==0:check(r['state']==q['state'],key+' '+backend+' zero-progress state exact '+q['id'])
   check((success,rejected)==(40,18),key+' '+backend+'40success18refusal');stats.append(dict(backend=backend,success=success,rejected=rejected,max_error=max(errors)))
  parity=[]
  for q,a,z in zip(req['requests'],native['rows'],wasm['rows']):
   check(a['id']==z['id'] and a['status']==z['status'],'NorSand all status parity '+q['id'])
   if a['status']:
    err=max([abs(x-y) for x,y in zip(a['state'],z['state'])]+[abs(x-y)/s for x,y,s in zip(a['observables'],z['observables'],q['observable_scales'])]);check(err<=2e-11,'NorSand original state/observable parity bound '+q['id']);parity.append(err)
  statistics[key]=dict(backends=stats,max_parity_error=max(parity))
 else:
  X=W/'docs/ingestion/hypoplastic-interface-2016';expect=load(X/'implementation-v1/backend-expectations.json');frozen=load(X/'execution-v1/source-freeze-v2.json');stats=[]
  check(expect['requests_sha256']==sha(reqfile) and expect['source_reference_sha256']==sha(X/'implementation-v1/references.json'),'interface original independent expected source bindings')
  for backend,report in [('native',native),('wasm',wasm)]:
   rows={r['id']:r for r in report['rows']};check(len(rows)==count and set(rows)==set(expect['expected']),'interface '+backend+' exact unique case ID set');errors=[];rejected=0
   for q in req['requests']:
    r=rows[q['id']];e=expect['expected'][q['id']]
    check(type(r['status']) is int and r['status']==e['status'],'interface '+backend+' exactstatus '+q['id'])
    check(len(r['state'])==5 and len(r['observables'])==8 and all(map(finite,r['state']+r['observables']+[r['coordinate']])),'interface '+backend+'finitefulloutputs '+q['id'])
    if not e['status']:
     rejected+=1;check(r['state']==[-1234567.]*5 and r['observables']==[-1234567.]*8 and r['coordinate']==-7654321.,'interface '+backend+'refusal rollback sentinels '+q['id']);continue
    err=max([abs(x-y)/s for x,y,s in zip(r['state'],e['state'],expect['state_scales'])]+[abs(x-y)/s for x,y,s in zip(r['observables'],e['observables'],[100000.]*7+[1.])]);check(err<=expect['scaled_tolerance'],'interface '+backend+' original full independent endpoint bound '+q['id']);errors.append(err)
    sn,sp,tx,tz,v=r['state'];bound=[sn,sp,sp,math.sqrt(2)*tx,0.,math.sqrt(2)*tz,(sn+2*sp)/3,v]
    check(r['observables']==bound and r['coordinate']==e['coordinate'],'interface '+backend+' exact state/stress/coordinate bindings '+q['id'])
   for a,z in expect['repeat_pairs']:check(all(rows[a][n]==rows[z][n] for n in ['state','observables','coordinate']),'interface '+backend+'exact frozen repeat '+a)
   check(all(rows['recovery-after-trial-budget'][n]==rows['x_shear-segment1-repeat1'][n] for n in ['state','observables','coordinate']),'interface '+backend+'exact rollback recovery')
   stats.append(dict(backend=backend,success=count-rejected,rejected=rejected,max_scaled_error=max(errors)))
  parity=[]
  for a,z in zip(native['rows'],wasm['rows']):
   check(a['id']==z['id'] and a['status']==z['status'] and a['coordinate']==z['coordinate'],'interface exactfullstatuscoordinate parity '+a['id'])
   err=max([abs(x-y)/s for x,y,s in zip(a['state'],z['state'],frozen['state_scales'])]+[abs(x-y)/s for x,y,s in zip(a['observables'],z['observables'],frozen['observable_scales'])]);check(err<=frozen['parity_scaled_absolute'],'interface original full-state/stress parity '+a['id']);parity.append(err)
  statistics[key]=dict(backends=stats,max_scaled_parity_error=max(parity))
(O/'actual-results.json').write_text(json.dumps(dict(identity='independent-current-controlled-path-actual-build-assessment-v1',scope='saved actual results only; no new compiled/model calls',checks=checks,count=len(checks),statistics=statistics,commands=commandrows,inputs=list({p['path']:p for p in allinputs}.values()),compiled_calls=0,cleanup='Two temporary current-source generation directories removed after exact hash comparison.'),indent=2)+'\n')
print('Independent saved-result checks:',len(checks));print(json.dumps(statistics,indent=2))
