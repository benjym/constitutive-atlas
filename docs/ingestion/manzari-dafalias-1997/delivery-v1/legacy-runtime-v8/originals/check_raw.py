"""Read-only raw transport linkage. Never invokes a compiler, solver or Wasm."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse,gzip,hashlib,json,math,sys
from frozen_logic import D,P,sha,frozen,load,ordinary_case

def pairs(items):
 result={}
 for key,value in items:
  assert key not in result,'duplicate JSON key: '+key
  result[key]=value
 return result

def parse(text):
 value=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda token: (_ for _ in ()).throw(AssertionError('nonfinite token: '+token)))
 finite(value);return value

def finite(value):
 if isinstance(value,float):assert math.isfinite(value),'nonfinite number'
 elif isinstance(value,list):
  for child in value:finite(child)
 elif isinstance(value,dict):
  for child in value.values():finite(child)

def equal(actual,expected,label):
 assert json.dumps(actual,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(expected,sort_keys=True,allow_nan=False,separators=(',',':')),label

def vector(value,size,label):
 assert isinstance(value,list)and len(value)==size and all(type(v)in[int,float]and math.isfinite(v)for v in value),label

def csv(values):return ','.join(str(v)for v in values)

def argv_for(request,artifact,folder,index):
 argv=[str(Path(artifact).resolve()),'--mode',request['mode'],'--model',request['model'],'--parameters',csv(request['parameters']),'--initial',csv(request['initial']),'--integration-settings',csv(request['settings'])]
 mode=request['mode']
 if mode in ['integrate','linearize']:argv+=['--strain',csv(request['strain'])]
 elif mode=='run-controls':argv+=['--protocol',str(request['protocol']),'--laboratory-controls-file',str((folder/'controls'/('call-'+str(index)+'.txt')).resolve()),'--response-contract','stress-scope-0.1']
 elif mode=='run':argv+=['--protocol',str(request['protocol']),'--target',str(request['target']),'--steps',str(request['steps']),'--cycles','0','--response-contract','stress-scope-0.1']
 else:raise AssertionError('unsupported mode')
 return argv

class Replay:
 def __init__(self,folder,backend,artifact):
  self.folder=Path(folder).resolve();self.backend=backend;self.artifact=artifact;self.calls=0;self.stream=None;self.controls=[];self.inventory={}
 def begin(self,name):
  assert self.stream is None
  path=self.folder/name;self.inventory[name]=sha(path);self.stream=gzip.open(path,'rt',encoding='utf-8')
 def end(self):
  assert next(self.stream,None)is None,'excess raw call';self.stream.close();self.stream=None
 def call(self,request,unused):
  line=next(self.stream,None);assert line is not None,'missing raw call'
  record=parse(line);self.calls+=1;self.validate(record,request);return record['response']
 def validate(self,record,request):
  assert set(record)=={'call_index','request','argv','returncode','elapsed_seconds','raw_stdout','stderr','response'},'raw record fields'
  assert type(record['call_index'])is int and record['call_index']==self.calls,'global call order'
  equal(record['request'],request,'exact frozen request/chain parent')
  assert type(record['elapsed_seconds'])in[int,float]and math.isfinite(record['elapsed_seconds'])and record['elapsed_seconds']>=0,'elapsed time'
  assert isinstance(record['raw_stdout'],str)and isinstance(record['stderr'],str),'transport text'
  response=parse(record['raw_stdout']);equal(record['response'],response,'raw stdout/response mismatch')
  assert isinstance(response,dict)and type(response.get('ok'))is bool and 'harness_error'not in response,'transport/harness error'
  assert type(record['returncode'])is int,'return code type'
  expected_rc=(0 if response['ok']else 1)if self.backend=='native'else 0
  assert record['returncode']==expected_rc,'transport/material return code'
  if self.backend=='native':
   equal(record['argv'],argv_for(request,self.artifact,self.folder,self.calls),'native argv/artifact binding')
   if request['mode']=='run-controls':
    path=self.folder/'controls'/('call-'+str(self.calls)+'.txt');assert path.read_text()==','.join(request['controls_bits']),'control wire bits';self.controls.append(str(path.relative_to(self.folder)))
  else:assert self.backend=='wasm'and record['argv']is None,'Wasm per-call argv'
  # Generic CLI/C ABI echoes bind the actual response to its submitted inputs.
  for key in ['model','parameters','initial','strain']:
   if key in response:assert response[key]==request[key],'response input echo: '+key
  if 'integration_settings'in response:
   settings=response['integration_settings'];assert settings==dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'],request['settings']))),'response settings echo'
  if 'protocol'in response:assert response['protocol']==request['protocol'],'response protocol echo'
  if 'loading'in response and request['mode']=='run-controls':assert response['loading']['controls_bits']==request['controls_bits'],'response controls bits echo'
  size=len(request['initial'])
  if 'state'in response:vector(response['state'],size,'response state layout')
  if 'points'in response:
   assert isinstance(response['points'],list),'response points'
   for point in response['points']:
    vector(point.get('state'),size,'point state');vector(point.get('strain'),6,'point strain');assert type(point.get('control'))in[int,float]and math.isfinite(point['control']),'point control'


def identity(folder,report,study,historical):
 if historical:
  assert study=='md'and sha(folder/'report.json')=='efce4a7b9e73d3bafe471672a1bbfd50540531658f1596372d9df85145d9a45c','exact old native-v3 report only'
  base=P/'execution-v3';backend='native';artifact=report['identity']['artifact_path'];assert report['identity']['artifact_sha256']=='25d976375238865ec43b8b4f512e6b76fbfef7f67bed9b125d5db1523f76db40','old artifact'
 else:
  pre=load('runtime-rebind-v5/preflight.py');current=pre.check();binding=parse((folder/'runtime-binding.json').read_text());assert binding['identity']=='md1997-raw-link-runtime-binding-v7','new collector binding identity'
  for key in ['source_freeze_sha256','source_directory','source_files','full_freeze_sha256','rebind_manifest_sha256']:equal(binding[key],current[key],'source binding '+key)
  assert binding['v5_preflight_identity']==current['identity']and binding['study']==study and binding['subset']==[]and binding['delegate_returncode']==0,'collector process outcome'
  assert binding['report_sha256']==sha(folder/'report.json')and binding['raw_link_manifest_sha256']==sha(D/'manifest.json'),'saved report/collector hash'
  assert sha(folder/'coordinator-build-receipt.json')==binding['coordinator_build_receipt_sha256'],'external receipt hash'
  actual=pre.build_binding(folder/'coordinator-build-receipt.json',binding['backend'],binding['artifact_path'])
  for key in ['backend','artifact_path','artifact_sha256','generated_catalogue_sha256','wasm_sha256','build_log_sha256']:equal(binding[key],actual[key],'artifact binding '+key)
  delegate=D/'collect.py';original=P/('resolution-study-v4/run_native.py'if study=='md'else 'ordinary-regression-v7/run.py')
  assert binding['delegate_path']==str(delegate)and binding['delegate_sha256']==sha(delegate)and binding['original_harness_path']==str(original)and binding['original_harness_sha256']==sha(original),'actual/original delegate identity'
  command=binding['delegate_command'];assert len(command)==9 and Path(command[0]).is_absolute()and Path(command[0]).resolve()==Path(sys.executable).resolve()and command[1:]==['-B',str(delegate),'--study',study,'--wasm-engine'if binding['backend']=='wasm'else '--solver',binding['artifact_path'],'--output',str(folder)],'collector command'
  base=P/('resolution-study-v4'if study=='md'else 'ordinary-regression-v7');backend=binding['backend'];artifact=binding['artifact_path']
 if study=='md':
  ident=report['identity'];assert ident['backend']==backend and ident['artifact_path']==artifact and ident['artifact_sha256']==sha(artifact),'MD artifact identity'
  for key,name in [('requests_sha256','requests.json'),('policy_sha256','POLICY.md'),('manifest_sha256','manifest.json')]:assert ident[key]==sha(base/name),'MD original identity '+key
  assert ident['model_sha256']==parse((base/'requests.json').read_text())['model_sha256']and ident['harness_only_no_constitutive_kernel']is True
  if backend=='wasm':assert ident['wasm_binary_sha256']==sha(Path(artifact).with_suffix('.wasm')),'MD payload identity'
  assert set(ident)=={'backend','artifact_path','artifact_sha256','model_sha256','requests_sha256','policy_sha256','manifest_sha256','harness_only_no_constitutive_kernel'}|({'wasm_binary_sha256'}if backend=='wasm'else set()),'exact MD identity fields'
  equal(parse((folder/'identity.json').read_text()),ident,'identity sidecar')
 else:
  assert report['identity']=='md1997-ordinary-regression-v7'and report['backend']==backend and report['artifact_sha256']==sha(artifact),'ordinary backend identity'
  assert report['policy_sha256']==sha(base/'policy.json')and report['manifest_sha256']==sha(base/'manifest.json'),'ordinary original identity'
 return base,backend,artifact


def verify_transport(folder,study,backend,artifact,calls):
 audit=parse((folder/'transport.json').read_text());expected={'identity':'md1997-raw-transport-v7','backend':backend,'artifact_path':artifact,'artifact_sha256':sha(artifact),'original_call_sha256':sha(P/'execution-v3/run_native.py'),'collector_sha256':sha(D/'collect.py'),'worker':None,'closed':True,'call_count':calls}
 if backend=='wasm':
  worker=audit.get('worker');assert isinstance(worker,dict),'worker audit'
  script=P/('resolution-study-v4/run_wasm.mjs'if study=='md'else 'execution-v3/run_wasm.mjs');stderr=folder/'worker-stderr.txt'
  expected['worker']={'command':['node',str(script),'--worker','--engine',artifact],'pid':worker.get('pid'),'ready_wire':worker.get('ready_wire'),'exit_code':0,'stderr_path':str(stderr),'stderr_sha256':sha(stderr)}
  assert type(worker.get('pid'))is int and worker['pid']>0,'worker PID';equal(parse(worker['ready_wire']),{'ready':True},'worker handshake')
 equal(audit,expected,'complete actual transport audit')
 return sha(folder/'transport.json')


def verify(folder,study,historical=False):
 frozen();folder=Path(folder).resolve();report=parse((folder/'report.json').read_text());base,backend,artifact=identity(folder,report,study,historical);replay=Replay(folder,backend,artifact)
 if study=='md':
  plan=parse((base/'requests.json').read_text());expected_files=[c['id']+'.jsonl.gz'for c in plan['cases']]+['special.jsonl.gz'];module=load(str(base.relative_to(P))+'/run_native.py');results={}
  reconstructed={'identity':report['identity'],'cases':results}
  for case in plan['cases']:
   replay.begin(case['id']+'.jsonl.gz');results[case['id']]=module.run_case(plan,case,replay,None);replay.end()
  replay.begin('special.jsonl.gz');reconstructed['special']=module.special(plan,replay,None,results);replay.end();reconstructed['call_count']=replay.calls
 else:
  policy=parse((base/'policy.json').read_text());expected_files=[case['model']+'.jsonl.gz'for case in policy['cases']];cases=[]
  for case in policy['cases']:
   req={'mode':'run','model':case['model'],'parameters':case['parameters'],'initial':case['initial'],'settings':case['integration_settings'],'protocol':case['protocol'],'target':case['target'],'steps':case['steps'],'cycles':case['cycles']}
   replay.begin(case['model']+'.jsonl.gz');response=replay.call(req,None);replay.end();cases.append(ordinary_case(case,response))
  reconstructed={'identity':'md1997-ordinary-regression-v7','backend':backend,'artifact_sha256':sha(artifact),'policy_sha256':sha(base/'policy.json'),'manifest_sha256':sha(base/'manifest.json'),'cases':cases,'passed':len(cases)==len(policy['cases'])and all(c['passed']for c in cases)}
 equal(report,reconstructed,'complete report reconstruction from raw transport')
 if study=='ordinary':assert reconstructed['passed']is True,'original ordinary acceptance gates'
 assert sorted(str(p.relative_to(folder))for p in folder.rglob('*.jsonl.gz'))==sorted(expected_files),'exact raw filename inventory'
 assert sorted(str(p.relative_to(folder))for p in (folder/'controls').rglob('*')if p.is_file())==sorted(replay.controls),'exact control filename inventory'
 transport_hash=None if historical else verify_transport(folder,study,backend,artifact,replay.calls)
 return {'identity':'md1997-raw-link-verification-v7','passed_raw_linkage':True,'study':study,'backend':backend,'historical_structure_only':historical,'report_sha256':sha(folder/'report.json'),'source_binding':'old predictor578 receipt126d9bc3; NOT new qualification'if historical else 'current control582 receipt4bdaf4c5','calls':replay.calls,'cases':len(plan['cases'])if study=='md'else len(cases),'raw_files':replay.inventory,'transport_sha256':transport_hash,'compiled_calls_by_checker':0,'scope':'transport linkage only; unchanged source/parity/ordinary gates and independent acceptance still required'}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('folder');parser.add_argument('--study',choices=['md','ordinary'],required=True);parser.add_argument('--historical-native-v3',action='store_true');parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);assert not out.exists(),'preserve prior checks'
 try:result=verify(args.folder,args.study,args.historical_native_v3)
 except Exception as error:
  out.write_text(json.dumps({'identity':'md1997-raw-link-verification-v7','passed_raw_linkage':False,'error':type(error).__name__+': '+str(error),'compiled_calls_by_checker':0},indent=2)+'\n');raise
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
