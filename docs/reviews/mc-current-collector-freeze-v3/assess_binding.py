"""Current source/reference/request identity only; no material calls."""
from pathlib import Path
import hashlib,json,struct,sys
from strict_observation_json import loads
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).resolve().parent;r=s.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:loads((s/n).read_bytes())
def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is float:return struct.pack('>d',a)==struct.pack('>d',b)
 if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
 return a==b
def verify():
 from importlib import import_module
 sys.path.insert(0,str(r));receipt=import_module('atlas.evidence').checked_receipt
 pins=read('source-pins.json')
 for n,h in pins['sources'].items():receipt(r,(s/'source-pins.json').relative_to(r).as_posix(),n,h)
 source=read('source-input.json');original=read('reference/requests.json');reqs=read('requests.json');specs=read('contracts.json');paths={x['id']:x for x in source['paths']}
 assert len(original)==len(reqs)==len(specs)==len(paths)==14
 for req,base,item in zip(reqs,original,specs):
  path=paths[req['id']]
  assert exact(req,dict(base,mode='run-controls',loading_version='laboratory-controls-0.1',controls_bits_csv=','.join(path['controls_bits'])))
  spec=item['specification'];assert item['id']==req['id'] and spec['response_contract']=='stress-scope-0.1' and spec['stress_scope']=='effective'
  assert spec['loading']['controls_bits']==path['controls_bits'] and spec['model']==req['model']
  for key in ['parameters','initial']:assert [float(x).hex()for x in req[key].split(',')]==[float(x).hex()for x in spec[key]]
  for key in ['protocol','steps','cycles','target']:assert spec[key]==req[key] and type(spec[key])is type(req[key])
 assert read('producer-specifications.json')==specs
 catalogue=read('catalogue.json');assert catalogue==read('generated/models.json') and len(catalogue['models'])==12
 assert catalogue['sha256']==hashlib.sha256(json.dumps(catalogue['models'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 old=read('../mc-current-contract-preflight-v2/prior-mc.json');new=read('models/mohr-coulomb.json')
 assert {k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}<={'name','description','status'}
 for f in (r/'models').glob('*.json'):assert f.read_bytes()==(s/'models'/f.name).read_bytes()
 assert len(list((s/'models').glob('*.json')))==12
 for precision in ['280','360']:
  ref=read('reference/reference-p'+precision+'.json');assert ref['source_input_sha256']==sha(s/'source-input.json')
 return {'passed':True,'requests':14,'models':12,'unchanged_canonical_models':11,'candidate_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
