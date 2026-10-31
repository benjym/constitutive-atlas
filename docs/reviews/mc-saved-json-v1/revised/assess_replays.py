"""Bind saved raw observations, actual CAPI arguments, exports and recovery."""
from pathlib import Path
import sys,json,struct
from assess_paths import load,finite
from strict_observation_json import loads
from assess_binding import exact,verify
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent
bits=lambda v:struct.pack('>d',finite(v)).hex()
def export_equal(a,b):
 if type(a)in(int,float)and type(b)in(int,float):return bits(0 if a==0 else a)==bits(0 if b==0 else b)
 if type(a)is not type(b):return False
 if isinstance(a,list):return len(a)==len(b)and all(export_equal(x,y)for x,y in zip(a,b))
 if isinstance(a,dict):return set(a)==set(b)and all(export_equal(a[k],b[k])for k in a)
 return a==b
def physical(r):return {k:v for k,v in r.items()if k!='elapsed_ms'}
def assess(directory):
 d=Path(directory);requests=load(s/'requests.json');bad=load(s/'rejection-requests.json');catalogue=load(s/'generated/models.json');rows=load(d/'journal.json');replays=load(d/'replays.json');failures=load(d/'rejections.json');calls=iter(load(d/'calls.json'));expected=load(s/'producer-specifications.json')
 assert len(rows)==15 and len(replays)==14 and len(failures)==12
 def consume(name,raw,req=None):
  loads(raw)  # Validate every raw call, including describe and otherwise unused fields.
  c=next(calls);assert c['name']==name and c['raw']==raw
  a=c['args']
  if req is None:assert a==[];return
  assert type(a[0])is str and a[0]==req['model']and type(a[3])is int and a[3]==req['protocol']
  for i,key in [(1,'parameters'),(2,'initial')]:
   assert type(a[i])is str
   x=[]if a[i]==''else a[i].split(',');y=[]if req[key]==''else req[key].split(',')
   assert len(x)==len(y)and all(bits(float(u))==bits(float(v))for u,v in zip(x,y))
  if name=='atlas_run_controls_with_settings':assert len(a)==6 and a[4]==req['controls_bits_csv'];setting=a[5]
  else:
   assert len(a)==8 and bits(a[4])==bits(req['target'])
   assert type(a[5])is int and a[5]==req['steps']and type(a[6])is int and a[6]==req['cycles'];setting=a[7]
  assert type(setting)is str
  x=setting.split(',');y=req['integration_settings'].split(',');assert len(x)==len(y)==6
  assert all(bits(float(u))==bits(float(v))for u,v in zip(x,y))
  if 'process'in c:assert type(c['process']['status'])is int and c['process']['status']in[0,1]
 consume('atlas_describe',rows[0]['raw'])
 for row,replay,req,spec in zip(rows[1:],replays,requests,expected):
  assert row['id']==replay['id']==req['id']==spec['id']
  assert exact(replay['specification'],spec['specification'])and exact(replay['imported'],spec['specification'])
  exported=replay['exported'];assert set(exported)=={'schema_version','catalogue_hash','specification','result'}
  assert exported['schema_version']=='0.2'and exported['catalogue_hash']==catalogue['sha256']
  assert exact(exported['specification'],spec['specification'])
  assert export_equal(exported['result'],loads(row['raw'])), 'export result does not preserve complete computed response'
  assert exported['result']['model']==req['model']and exported['result']['api_version']=='experimental-laboratory-controls-0.1'and exported['result']['catalogue_hash']==catalogue['sha256']
  consume('atlas_run_controls_with_settings',row['raw'],req);consume('atlas_run_controls_with_settings',replay['raw'],req)
  a=loads(row['raw']);b=loads(replay['raw']);assert exact(physical(a),physical(b))
 recovery=next(req for req in requests if req['id']==bad['recovery_request_id']);baseline=loads(next(row['raw']for row in rows if row['id']==recovery['id']))
 for row,req in zip(failures,bad['cases']):
  assert row['id']==req['id']and exact(row['request'],req)
  consume('atlas_run_controls_with_settings'if req['mode']=='run-controls'else'atlas_run_with_settings',row['raw'],req)
  failed=loads(row['raw']);assert failed['ok']is False
  assert 'points'not in failed or isinstance(failed['points'],list)and len(failed['points'])==0
  consume('atlas_run_controls_with_settings',row['recovery_raw'],recovery)
  actual=loads(row['recovery_raw']);assert exact(physical(actual),physical(baseline))
 assert next(calls,None)is None
 return {'passed':True,'export_import_replays':14,'rejection_recovery_pairs':12,'raw_calls_bound':53,'candidate_calls':0}
if __name__=='__main__':verify();print(json.dumps(assess(sys.argv[1]),indent=2))
