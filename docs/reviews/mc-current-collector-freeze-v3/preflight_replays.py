from pathlib import Path
import json,copy,tempfile
from assess_replays import assess
from assess_binding import verify
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent;verify();read=lambda n:json.loads((s/n).read_text())
requests=read('requests.json');rows=read('source-ideal.json');specs=read('producer-specifications.json');bad=read('rejection-requests.json');calls=[];replays=[];failures=[]
def args(req):
 base=[req['model'],req['parameters'],req['initial'],req['protocol']]
 return base+([req['controls_bits_csv'],req['integration_settings']]if req['mode']=='run-controls'else[req['target'],req['steps'],req['cycles'],req['integration_settings']])
def call(name,raw,req=None,status=0):calls.append({'name':name,'args':[]if req is None else args(req),'raw':raw,'process':{'status':status,'signal':None,'error':None,'stderr':''}})
call('atlas_describe',rows[0]['raw'])
for row,spec,req in zip(rows[1:],specs,requests):
 result=json.loads(row['raw']);exported={'schema_version':'atlas-laboratory-export-0.2','catalogue_hash':result['catalogue_hash'],'specification':spec['specification'],'result':result}
 replays.append({'id':req['id'],'specification':spec['specification'],'exported':exported,'imported':spec['specification'],'raw':row['raw']})
 for _ in range(2):
  call('atlas_describe',rows[0]['raw']);call('atlas_run_controls_scope_with_settings',row['raw'],req)
recovery=next(req for req in requests if req['id']==bad['recovery_request_id']);raw=next(row['raw']for row in rows if row['id']==recovery['id'])
for req in bad['cases']:
 failure=json.dumps({'ok':False,'message':'source-ideal rejection','points':[]});failures.append({'id':req['id'],'request':req,'raw':failure,'recovery_raw':raw})
 call('atlas_run_controls_scope_with_settings'if req['mode']=='run-controls'else'atlas_run_scope_with_settings',failure,req,1);call('atlas_describe',rows[0]['raw']);call('atlas_run_controls_scope_with_settings',raw,recovery)
original={'journal.json':rows,'replays.json':replays,'rejections.json':failures,'calls.json':calls}
fixture=s/'synthetic';fixture.mkdir(exist_ok=True)
for name,value in original.items():(fixture/name).write_text(json.dumps(value,indent=2)+'\n')
negatives=[]
with tempfile.TemporaryDirectory(prefix='atlas-mc-replay-ideal-')as tmp:
 p=Path(tmp)
 def save(data):
  for n,value in data.items():(p/n).write_text(json.dumps(value)+'\n')
 save(original);ideal=assess(p,'native')
 def reject(label,mutate):
  data=copy.deepcopy(original);mutate(data);save(data)
  try:assess(p,'native')
  except Exception:negatives.append(label)
  else:raise RuntimeError('false pass '+label)
 reject('missing call',lambda d:d['calls.json'].pop())
 reject('wrong API name',lambda d:d['calls.json'][2].update(name='atlas_run_scope_with_settings'))
 reject('wrong model argument',lambda d:d['calls.json'][2]['args'].__setitem__(0,'linear-elastic'))
 reject('boolean protocol argument',lambda d:d['calls.json'][2]['args'].__setitem__(3,False))
 reject('wrong control bits argument',lambda d:d['calls.json'][2]['args'].__setitem__(4,'0000000000000000'))
 reject('wrong settings argument',lambda d:d['calls.json'][2]['args'].__setitem__(5,'1,1,1,1,1,1'))
 reject('wrong raw binding',lambda d:d['calls.json'][2].update(raw='{}'))
 reject('boolean process status',lambda d:d['calls.json'][2]['process'].update(status=False))
 reject('wrong imported target',lambda d:d['replays.json'][0]['imported'].update(target=.02))
 reject('wrong export version',lambda d:d['replays.json'][0]['exported'].update(schema_version='0.1'))
 reject('wrong export catalogue',lambda d:d['replays.json'][0]['exported'].update(catalogue_hash='wrong'))
 reject('truncated exported result',lambda d:d['replays.json'][0]['exported'].update(result={'model':'mohr-coulomb','api_version':'experimental-laboratory-scope-0.1','catalogue_hash':read('generated/models.json')['sha256']}))
 reject('fabricated exported stress',lambda d:d['replays.json'][0]['exported']['result']['points'][1]['state'].__setitem__(0,1e9))
 reject('wrong export model',lambda d:d['replays.json'][0]['exported']['result'].update(model='wrong'))
 reject('changed export producer',lambda d:d['replays.json'][0]['exported']['specification']['loading']['producer'].update(algorithm='wrong'))
 reject('missing recovery',lambda d:d['rejections.json'][0].pop('recovery_raw'))
 reject('wrong rejection request',lambda d:d['rejections.json'][0]['request'].update(initial=''))
 reject('wrong replay ID',lambda d:d['replays.json'][0].update(id='wrong'))
(s/'preflight-replay-results.json').write_text(json.dumps({'passed':True,'source_ideal':ideal,'negative_checks':len(negatives),'rejected_corruptions':negatives,'compiled_calls':0},indent=2)+'\n');print('14ideal replay/12recovery/93raw call bindings and',len(negatives),'corruptions pass')
