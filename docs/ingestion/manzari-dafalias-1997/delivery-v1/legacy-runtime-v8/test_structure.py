"""Historical serialization and synthetic transport negatives, zero backend calls."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import copy,gzip,io,json,sys
from frozen_logic import D,P,load,ordinary_case,sha
import check_raw as check
import collect

RESULTS=[]
def reject(name,action):
 try:action()
 except (AssertionError,FileNotFoundError,ValueError,KeyError)as error:RESULTS.append({'case':name,'expected':'reject','observed':'rejected','message':str(error)})
 else:raise AssertionError('negative accepted: '+name)

def main():
 out=D/'structure-fixtures';out.mkdir(exist_ok=True)
 old=Path('/private/tmp/atlas-predictor-constraints-v1/md-native-report-v3')
 with gzip.open(old/'special.jsonl.gz','rt')as stream:original=json.loads(next(stream))
 replay=check.Replay(old,'native',original['argv'][0]);replay.calls=original['call_index'];replay.validate(original,original['request']);RESULTS.append({'case':'old-native-raw-positive','observed':'linked','source':'old predictor578 only'})
 def mutate(name,edit):
  record=copy.deepcopy(original);edit(record);reject(name,lambda:replay.validate(record,original['request']))
 mutate('request-parent',lambda r:r['request']['initial'].__setitem__(0,123))
 mutate('request-settings',lambda r:r['request']['settings'].__setitem__(0,0.1))
 mutate('request-increment',lambda r:r['request']['strain'].__setitem__(0,0.1))
 mutate('call-order',lambda r:r.__setitem__('call_index',1))
 mutate('wrong-returncode',lambda r:r.__setitem__('returncode',99))
 mutate('raw-garbage',lambda r:r.__setitem__('raw_stdout','garbage'))
 mutate('stdout-response-mismatch',lambda r:r['response'].__setitem__('message','contradiction'))
 mutate('wrong-artifact-argv',lambda r:r['argv'].__setitem__(0,'/wrong/artifact'))
 mutate('wrong-backend-argv',lambda r:r.__setitem__('argv',None))
 mutate('wrong-state-length',lambda r:(r['response'].__setitem__('state',[]),r.__setitem__('raw_stdout',json.dumps(r['response']))))
 mutate('harness-error',lambda r:(r['response'].__setitem__('harness_error','transport failed'),r.__setitem__('raw_stdout',json.dumps(r['response']))))
 mutate('response-input-echo',lambda r:(r['response']['initial'].__setitem__(0,123),r.__setitem__('raw_stdout',json.dumps(r['response']))))
 reject('duplicate-json',lambda:check.parse('{"ok":true,"ok":false}'))
 reject('nonfinite-json',lambda:check.parse('{"x":1e999}'))
 reject('missing-raw-file',lambda:replay.begin('does-not-exist.jsonl.gz'))
 replay.stream=io.StringIO('');reject('missing-call',lambda:replay.call(original['request'],None));replay.stream.close();replay.stream=None
 replay.stream=io.StringIO('{}\n');reject('excess-call',replay.end);replay.stream.close();replay.stream=None
 reject('report-mismatch',lambda:check.equal({'points':[]},{'points':[original['response']['state']]},'complete report reconstruction'))
 oldordinary=Path('/private/tmp/atlas-predictor-constraints-v1/ordinary-native-v6');oldreport=json.loads((oldordinary/'report.json').read_text());policy=json.loads((P/'ordinary-regression-v7/policy.json').read_text())
 for case,saved in zip(policy['cases'],oldreport['cases']):
  with gzip.open(oldordinary/(case['model']+'.jsonl.gz'),'rt')as stream:record=json.loads(next(stream));assert next(stream,None)is None
  actual=ordinary_case(case,record['response']);check.equal(actual,saved,'old ordinary exact decisions');bad=copy.deepcopy(saved);bad['checks']={};reject('missing-ordinary-checks-'+case['model'],lambda:check.equal(bad,actual,'ordinary complete decision'))
 RESULTS.append({'case':'all16-ordinary-decisions-positive','observed':'exact frozen case/check logic','source':'old predictor578 ordinary-v6 only'})
 artifact=out/'not-an-executable.txt';artifact.write_text('Synthetic transport artifact. Never executed.\n')
 originalmodule=load('execution-v3/run_native.py');collect.STUDY='legacy-md';audited=collect.audited_factory(originalmodule.Backend);assert audited.call is originalmodule.Backend.call
 native=out/'native';native.mkdir(exist_ok=True);instance=audited(SimpleNamespace(solver=str(artifact),wasm_engine=None),native);instance.close();check.verify_transport(native,'legacy-md','native',str(artifact.resolve()),0)
 class Worker:
  pid=12345
  stdin=io.StringIO()
  stdout=io.StringIO('{"ready":true}\n')
  def wait(self,timeout):return 0
 wasm=out/'wasm';wasm.mkdir(exist_ok=True)
 with patch.object(collect.subprocess,'Popen',return_value=Worker())as spawn:
  instance=audited(SimpleNamespace(solver=None,wasm_engine=str(artifact)),wasm);instance.close();assert spawn.call_count==1
 check.verify_transport(wasm,'legacy-md','wasm',str(artifact.resolve()),0)
 audit=json.loads((wasm/'transport.json').read_text())
 for name,edit in [('worker-exit',lambda a:a['worker'].__setitem__('exit_code',9)),('worker-ready',lambda a:a['worker'].__setitem__('ready_wire','{"ready":false}')),('worker-command',lambda a:a['worker']['command'].__setitem__(0,'wrong')),('worker-artifact',lambda a:a.__setitem__('artifact_sha256','0'*64)),('worker-counter',lambda a:a.__setitem__('call_count',1)),('worker-stderr-hash',lambda a:a['worker'].__setitem__('stderr_sha256','0'*64))]:
  bad=copy.deepcopy(audit);edit(bad);(wasm/'transport.json').write_text(json.dumps(bad));reject(name,lambda:check.verify_transport(wasm,'legacy-md','wasm',str(artifact.resolve()),0))
 (wasm/'transport.json').write_text(json.dumps(audit,indent=2)+'\n')
 RESULTS.append({'case':'mock-process-transport-positive','observed':'native and mocked Wasm audit verified','actual_spawned_processes':0})
 (D/'structure-results.json').write_text(json.dumps({'identity':'md1997-legacy-structure-tests-v8','compiled_calls':0,'builds':0,'actual_spawned_processes':0,'results':RESULTS},indent=2)+'\n')
 print(json.dumps({'checks':len(RESULTS),'compiled_calls':0}))
if __name__=='__main__':main()
