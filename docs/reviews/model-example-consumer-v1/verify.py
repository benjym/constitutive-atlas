"""Check retained consumer inputs/exports; no fresh browser or scientific claim."""
from pathlib import Path
import hashlib,json
s=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
for name,pin in read(s/'before-manifest.json')['files'].items():assert sha(s/'before'/name)==pin,name
pins=read(s/'after-manifest.json');prior=read(s.parent/'seven-model-lab-integration/integration-pins.json')
for name,pin in pins.items():
 if name.startswith('/private/tmp/'):
  if name.endswith('/generated/models.json'):assert sha(s/'descriptor.json')==pin
  else:assert prior['artifacts'][name]==pin
 elif name=='acceptance.json':assert sha(s/name)==pin
 else:assert sha(s/'after'/name)==pin
for name,pin in read(s/'evidence-manifest.json').items():assert sha(s/name)==pin,name
models=read(s/'descriptor.json')['models'];assert len(models)==7
c,l,i,r=[read(s/(name+'-run.json'))for name in ['custom','loaded','imported','reset']]
a,b=c['specification'],l['specification']
assert all(x['result']['ok']is True for x in [c,l,i,r])
assert a['parameters']==[100000,40000000,.25]and a['initial']==[150000,125000,125000,0,0,0,.7]
assert b['parameters']==[100000,30000000,.25]and b['initial']==[100000,100000,100000,0,0,0,.7]
assert a['protocol']==0 and a['target']==.002 and a['steps']==20 and a['integration_settings']['rate_tolerance']==2e-6
for k in ['protocol','target','steps','cycles','integration_settings']:assert a[k]==b[k]
assert a==i['specification']
z=r['specification'];assert z['parameters']==b['parameters']and z['initial']==b['initial']
assert z['protocol']==1 and z['steps']==100 and z['target']==.01 and z['integration_settings']['rate_tolerance']==1e-6
points=0
for model in models:
 doc=read(s/'seven-model-browser'/(model['id']+'-run.json'));spec=doc['specification'];assert doc['result']['ok']is True
 assert spec['model']==model['id']and doc['catalogue_hash']==read(s/'descriptor.json')['sha256']
 assert spec['initial']==[v for f in model['state']for v in(f['initial']if f['shape']=='sym'else[f['initial']])]
 for value,p in zip(spec['parameters'],model['parameters'].values()):assert abs(value-p['default'])<=1e-14*max(1,abs(p['default']))
 assert len(doc['result']['points'])==101;points+=101
assert 'Errors: 0, Warnings: 0' in(s/'console.txt').read_text()
print(json.dumps({'retained_evidence_pass':True,'example_restore':True,'loading_and_settings_preserved':True,'exact_import_specification':True,'complete_reset':True,'shipped_models':len(models),'default_browser_points':points,'engine_rebuilt':False,'candidate_installed':False,'deployment':False},indent=2))
