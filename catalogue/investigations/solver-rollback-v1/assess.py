"""Assess a future raw probe JSON; no compiled execution or policy adaptation."""
import json,pathlib,struct,sys
P=pathlib.Path(__file__).resolve().parent
bits=lambda x:struct.pack('>d',float(x)).hex()
def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key '+k)
  d[k]=v
 return d
load=lambda p:json.loads(pathlib.Path(p).read_text(),object_pairs_hook=unique)
def assess(raw):
 e=load(P/'expected.json');a=load(raw);errors=[]
 def check(ok,why):
  if not ok:errors.append(why)
 check(set(a)=={'version','rows','preparation'},'complete root fields')
 check(a.get('version')=='solver-rollback-observations-v1','version')
 rows=a.get('rows',[]);check([r.get('id') for r in rows]==[r['id'] for r in e['rows']],'ordered complete unique rows')
 for r,t in zip(rows,e['rows']):
  expected={k:v for k,v in t.items() if k not in ['state','time']};expected['state_bits']=None if t['state'] is None else list(map(bits,t['state']));expected['time_bits']=None if t['time'] is None else bits(t['time']);expected.update(e['all_rows'])
  check(json.dumps(r,sort_keys=True,allow_nan=False)==json.dumps(expected,sort_keys=True,allow_nan=False),t['id']+' full typed semantic row')
 rows=a.get('preparation',[]);check([r.get('id') for r in rows]==[r['id'] for r in e['preparation']],'ordered complete preparation rows')
 for r,t in zip(rows,e['preparation']):
  check(set(r)=={'id','ok','scratch_bits','inputs_bitwise_unchanged'},t['id']+' preparation fields')
  check(r.get('ok') is t['ok'] and r.get('inputs_bitwise_unchanged') is True,t['id']+' preparation status/input')
  expected=list(map(bits,t['scratch']));actual=r.get('scratch_bits',[])
  check(actual[:len(expected)]==expected and len(actual)==8,t['id']+' committed prefix/success scratch')
  if 'scratch_policy' not in t:check(actual==expected,t['id']+' complete scratch')
 return dict(version='solver-rollback-assessment-v1',passed=not errors,errors=errors)
if __name__=='__main__':
 result=assess(sys.argv[1]);print(json.dumps(result,indent=2));sys.exit(0 if result['passed'] else 1)
