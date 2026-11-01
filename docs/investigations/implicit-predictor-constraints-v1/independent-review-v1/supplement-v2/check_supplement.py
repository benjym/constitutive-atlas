import copy,hashlib,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1]; C=P/'coordinator-v1'; script=C/'check_fixture_v2.py'; req=json.loads((P/'requests.json').read_text()); byid={c['id']:c for c in req['cases']}; seq=req['cases']+[byid[n] for pair in req['recovery_pairs'] for n in pair]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
artifact=D/'synthetic-artifact.txt';artifact.write_text('Synthetic text only. Never executed.\n')
keys=req['settings_order']; reports=[]
for backend in ['native','wasm']:
 r={'status':'passed','backend':backend,'engine_path':str(artifact),'engine_sha256':h(artifact),'request_sha256':h(P/'requests.json'),'rows':[]};previous=None
 for original in seq:
  c=copy.deepcopy(original)
  if c['id'] in ['unload','reload','hold']:c['initial']=previous['state']
  ok=c['expected']['ok']; response={'ok':ok,'state':copy.deepcopy(c['expected']['state'] if ok else c['initial']),'model':c['model'],'parameters':c['parameters'],'initial':c['initial'],'strain':c['strain'],'integration_settings':dict(zip(keys,c['integration_settings'])),'diagnostics':{'partition_committed':ok,'increment_fractions':[1] if ok else []}}
  row={'request':c,'response':response,'stdout':json.dumps(response)}
  if backend=='wasm':row['wire']=json.dumps({'raw':row['stdout']})
  else:
   csv=lambda v:','.join(format(x,'.17g') for x in v)
   row['command']=[str(artifact.resolve()),'--mode','integrate','--model',c['model'],'--parameters',csv(c['parameters']),'--initial',csv(c['initial']),'--strain',csv(c['strain']),'--integration-settings',csv(c['integration_settings'])]
  r['rows'].append(row);previous=response
 reports.append(r)
results=[]
def run(label,pair,expect):
 paths=[]
 for backend,r in zip(['native','wasm'],pair):
  p=D/(label+'-'+backend+'.json');p.write_text(json.dumps(r));paths.append(p)
 out=D/(label+'-checks.json');code=None
 with patch.object(sys,'argv',[str(script),str(paths[0]),str(paths[1]),'--output',str(out)]):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:code=ex.code
  except Exception as ex:code='exception:'+str(ex)
 passed=json.loads(out.read_text())['passed'] if out.exists() else False
 results.append({'case':label,'expected_pass':expect,'passed':passed,'exit':code,'expectation_met':passed==expect})
 assert passed==expect,label
run('ideal',copy.deepcopy(reports),True)
def mutate(label,fn):
 pair=copy.deepcopy(reports);fn(pair);run(label,pair,False)
def both(fn):return lambda pair:[fn(r) for r in pair]
def refresh(r,i):
 r['rows'][i]['stdout']=json.dumps(r['rows'][i]['response'])
 if r['backend']=='wasm':r['rows'][i]['wire']=json.dumps({'raw':r['rows'][i]['stdout']})
mutate('equal-empty',both(lambda r:r.update(rows=[])))
mutate('equal-misbound',both(lambda r:r.update(request_sha256='wrong')))
mutate('equal-label',lambda p:p[1].update(backend='native'))
mutate('artifact',both(lambda r:r.update(engine_sha256='wrong')))
mutate('exact-request',both(lambda r:r['rows'][0]['request']['parameters'].__setitem__(0,200)))
mutate('raw-divergence',lambda p:p[0]['rows'][0]['response']['state'].__setitem__(0,4))
mutate('wire-divergence',lambda p:p[1]['rows'][0].update(wire=json.dumps({'raw':'{}'})))
mutate('chain',both(lambda r:r['rows'][2]['request']['initial'].__setitem__(6,99)))
def response_mutation(i,fn):
 def modify(r):fn(r['rows'][i]['response']);refresh(r,i)
 return both(modify)
mutate('decision',response_mutation(7,lambda r:r.update(ok=True)))
mutate('rollback',response_mutation(5,lambda r:r['state'].__setitem__(7,.001)))
mutate('partition',response_mutation(0,lambda r:r['diagnostics'].update(increment_fractions=[.5,.5])))
mutate('commit',response_mutation(0,lambda r:r['diagnostics'].update(partition_committed=False)))
mutate('nonfinite',response_mutation(0,lambda r:r['state'].__setitem__(0,float('nan'))))
mutate('overflow',lambda p:p[0]['rows'][0].update(stdout='{"ok":true,"state":[1e999]}'))
mutate('malformed-row',both(lambda r:r['rows'].__setitem__(0,None)))
mutate('malformed-rows',both(lambda r:r.update(rows={})))
mutate('echo-settings',response_mutation(0,lambda r:r['integration_settings'].update(max_depth=2)))
mutate('bool-decision',response_mutation(0,lambda r:r.update(ok=1)))
mutate('analytic',response_mutation(0,lambda r:r['state'].__setitem__(6,.001)))
# Original parity remains required and passes ideal valid evidence.
oldout=D/'original-ideal-checks.json'
with patch.object(sys,'argv',[str(P/'check_parity.py'),str(D/'ideal-native.json'),str(D/'ideal-wasm.json'),'--output',str(oldout)]):
 try:runpy.run_path(str(P/'check_parity.py'),run_name='__main__')
 except SystemExit as ex:assert ex.code==0
assert json.loads(oldout.read_text())['status']=='passed'
(D/'checks.json').write_text(json.dumps({'compiled_calls':0,'inputs':{str(p):h(p) for p in [script,C/'FIXTURE-CHECK-POLICY-v2.md',P/'requests.json',P/'check_parity.py']},'results':results},indent=2)+'\n')
