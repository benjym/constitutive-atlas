"""Source/reference/request/model identity checks; no candidate evaluation."""
from pathlib import Path
import hashlib,json,struct
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
from strict_observation_json import loads
s=Path(__file__).parent
read=lambda n:loads((s/n).read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is float:return struct.pack('>d',a)==struct.pack('>d',b)
 if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
 return a==b
def verify():
 assert sha(s/'reference/manifest.json')=='3c9cdca82c5c58d52f1aa1d19a879cd28bb9775aa470e540a972c4c5efd7c172'
 assert sha(s/'reference/source-input.json')=='cda24eaddca3dc2e6773d6bfb19030f4f446303964d2c64eecb230403f98841b'
 assert(s/'source-input.json').read_bytes()==(s/'reference/source-input.json').read_bytes()
 for name,pin in read('reference/manifest.json')['files'].items():assert sha(s/'reference'/name)==pin['sha256'],name
 for precision in ['280','360']:
  ref=read('reference/reference-p'+precision+'.json');assert ref['source_input_sha256']==sha(s/'source-input.json')
 source=read('source-input.json');paths={p['id']:p for p in source['paths']};requests=read('requests.json');original=read('reference/requests.json');assert len(requests)==len(original)==len(paths)==14
 for req,base in zip(requests,original):
  expected=dict(base,mode='run-controls',loading_version='laboratory-controls-0.1',controls_bits_csv=','.join(paths[base['id']]['controls_bits']))
  assert exact(req,expected),req['id']
  assert [float(x).hex()for x in req['initial'].split(',')]==source['initial']
  actual=dict(zip(read('models/mohr-coulomb.json')['parameters'],[float(x).hex()for x in req['parameters'].split(',')]))
  assert actual==source['parameters']
 specs=read('producer-specifications.json');assert len(specs)==14
 for row,req in zip(specs,requests):
  assert row['id']==req['id'];spec=row['specification'];path=paths[req['id']]
  assert set(spec)=={'model','parameters','initial','protocol','target','steps','cycles','integration_settings','loading'}
  assert spec['model']==req['model']
  for k in ['protocol','steps','cycles']:assert type(spec[k])is int and spec[k]==req[k]
  assert type(spec['target'])in(int,float)and struct.pack('>d',spec['target']).hex()==path['target_bits']
  for k in ['initial','parameters']:
   assert isinstance(spec[k],list)and all(type(v)in(int,float)for v in spec[k])
   assert [struct.pack('>d',v).hex()for v in spec[k]]==[struct.pack('>d',float(v)).hex()for v in req[k].split(',')]
  settings=spec['integration_settings'];keys=['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks']
  assert set(settings)==set(keys+['version','norm'])and settings['version']=='incremental-settings-0.1'and settings['norm']=='scaled_component_max'
  for i,(k,v)in enumerate(zip(keys,req['integration_settings'].split(','))):
   assert type(settings[k])in(int,float)and struct.pack('>d',settings[k]).hex()==struct.pack('>d',float(v)).hex()
   if i>=2:assert type(settings[k])is int
  l=spec['loading'];assert set(l)=={'version','encoding','producer','controls_bits'}and l['version']=='laboratory-controls-0.1'and l['encoding']=='ieee754-binary64-hex'
  assert exact(l['producer'],{'version':'laboratory-waveform-0.1','algorithm':path['producer'],'target_bits':path['target_bits'],'steps':path['steps'],'cycles':path['cycles']})
  assert l['controls_bits']==path['controls_bits']
 old=read('baseline-mc-model.json');current=read('models/mohr-coulomb.json')
 for key in ['name','description','status']:old.pop(key);current.pop(key)
 assert exact(old,current),'constitutive/source/convention delta'
 old=read('baseline-nine-models.json');new=read('generated/models.json');assert len(old['models'])==9 and len(new['models'])==10
 assert[newm for newm in new['models']if newm['id']!='mohr-coulomb']==old['models']
 for m in old['models']:
  assert sha(s/'models'/(m['id']+'.json'))==read('baseline-nine-definition-hashes.json')[m['id']]
 return {'passed':True,'requests':14,'reference_points':834,'metadata_only_mc_delta':True,'unchanged_nine_definitions':True,'candidate_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
