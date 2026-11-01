from pathlib import Path
import json,math,struct,hashlib
p=Path(__file__).resolve().parent
a=json.loads((p/'export-original.json').read_text());b=json.loads((p/'export-replayed.json').read_text());e=json.loads((p/'export-edited-undrained.json').read_text())
counts={'binary64_values':0,'scalar_values':0}
def exact(x,y):
 assert type(x)==type(y),(type(x),type(y))
 if isinstance(x,dict):
  assert x.keys()==y.keys()
  for k in x:exact(x[k],y[k])
 elif isinstance(x,list):
  assert len(x)==len(y)
  for u,v in zip(x,y):exact(u,v)
 elif isinstance(x,float):
  assert math.isfinite(x) and math.isfinite(y)
  assert struct.pack('>d',x)==struct.pack('>d',y)
  counts['binary64_values']+=1
 else:
  assert x==y
  counts['scalar_values']+=1
for d in (a,b,e):
 assert d['schema_version']=='atlas-laboratory-export-0.2'
 assert d['specification']['model']=='hypoplastic-clay-2013'
 assert d['result']['ok'] and len(d['result']['points'])==101
 assert all(len(x['state'])==7 and len(x['strain'])==6 for x in d['result']['points'])
exact(a['catalogue_hash'],b['catalogue_hash']);exact(a['specification'],b['specification'])
ar={k:v for k,v in a['result'].items() if k!='elapsed_ms'};br={k:v for k,v in b['result'].items() if k!='elapsed_ms'}
exact(ar,br)
assert e['specification']['parameters'][-1]==0.21 and e['specification']['initial'][-1]==0.81
assert e['specification']['protocol']==2 and e['specification']['target']==0.002
s=p.parents[4]/'.local/clay2013-current-delivery-v1/site'
# The immutable package manifest is checked against actual local package bytes.
manifest=json.loads((p.parent/'PACKAGE_MANIFEST.json').read_text())['files']
for n,item in manifest.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==item['sha256'],n
cat=json.loads((s/'models.json').read_text())
assert a['catalogue_hash']==b['catalogue_hash']==e['catalogue_hash']==cat['sha256']
supported=json.loads((p.parent/'supported-package.json').read_text())
row=next(x for x in supported['ordinary'] if x['id']=='hypoplastic-clay-2013')
exact(a['result']['points'],row['result']['points'])
print(json.dumps({'status':'pass','exact_replay_points':101,'persistent_components_per_point':7,'compared':counts,'ignored_replay_fields':['result.elapsed_ms'],'package_files_unchanged':len(manifest),'catalogue_hash':cat['sha256'],'browser_to_current_package_gate_points_exact':True,'edited_undrained':{'nu':0.21,'e':0.81,'target':0.002,'steps':100,'points':101}},indent=2))
