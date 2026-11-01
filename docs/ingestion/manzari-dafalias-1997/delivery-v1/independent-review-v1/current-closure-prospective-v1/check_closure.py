from pathlib import Path
import json,hashlib,subprocess,tempfile
D=Path(__file__).resolve().parent;P=D.parents[1];ROOT=D.parents[5]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'source-freeze-v2.json')=='3122d681c32357cea15d9171ebfacca9ad793c749014166dac1a5aa5bea62a98'
assert sha(P/'ordinary-regression-policy-v2.json')=='32c703545a611d82c2680c9f1345b5678cefefe996004302457f0582a17b5ec0'
f=json.loads((P/'source-freeze-v2.json').read_text());policy=json.loads((P/'ordinary-regression-policy-v2.json').read_text());src=Path(f['source_directory']);checks=[]
assert len(f['source_files'])==576
for name,h in f['source_files'].items():assert sha(src/name)==h,name
actual={str(x.relative_to(src)) for x in src.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
assert actual==set(f['source_files']),{'extra':list(actual-set(f['source_files'])),'missing':list(set(f['source_files'])-actual)}
checks.append({'kind':'source-receipt-bindings','count':576,'passed':True})
names=[n for n in f['source_files'] if n not in f['additional_files']]
queries=''.join(f["base_revision"]+':'+n+'\n' for n in names)
r=subprocess.run(['git','cat-file','--batch'],input=queries.encode(),capture_output=True,check=True,cwd=ROOT).stdout
pos=0
for name in names:
 end=r.index(b'\n',pos);header=r[pos:end].split();assert len(header)==3,(name,header);size=int(header[2]);data=r[end+1:end+1+size];assert data==(src/name).read_bytes(),name;pos=end+size+2
assert pos==len(r)
checks.append({'kind':'committed-base-byte-equality','revision':f['base_revision'],'files':len(names),'passed':True})
for n,h in f['additional_files'].items():assert sha(src/n)==h
assert sha(src/'models/manzari-dafalias-1997-constant-m-be-v1.json')==sha(P/'manzari-dafalias-1997-constant-m-be-v1.json')
assert sha(src/'models/ramberg-osgood-ansys242.json')==sha(ROOT/'models/ramberg-osgood-ansys242.json')
checks.append({'kind':'exact-two-additions','files':f['additional_files'],'passed':True})
models={json.loads(x.read_text())['id']:(x,json.loads(x.read_text())) for x in (src/'models').glob('*.json')}
assert len(models)==16 and set(models)=={x['model'] for x in policy['cases']}
old=json.loads((P/'ordinary-regression-policy-v1.json').read_text())
assert all(x==next(c for c in policy['cases'] if c['model']==x['model']) for x in old['cases'])
for c in policy['cases']:
 path,m=models[c['model']];assert sha(path)==c['definition_sha256'];assert c['parameters']==[x['default'] for x in m['parameters'].values()]
 initial=[]
 for s in m['state']:initial.extend(s['initial'] if isinstance(s['initial'],list) else [s['initial']])
 assert c['initial']==initial,c['model'];assert c['protocol']==1 and c['target']==.01 and c['steps']==100 and c['cycles']==0
checks.append({'kind':'complete-policy-exact-defaults','count':16,'prior13unchanged':True,'newmodels':sorted(set(models)-{x['model'] for x in old['cases']}),'passed':True})
generated=src.parent/'generated-current-closure-v2'
assert sha(generated/'models.json')==policy['generated_catalogue_sha256']
g=json.loads((generated/'models.json').read_text());assert len(g['models'])==16
assert {m['id']:m for m in g['models']}=={k:v[1] for k,v in models.items()}
with tempfile.TemporaryDirectory(dir=D) as tmp:
 result=subprocess.run(['python3','-B','-m','atlas.compiler',tmp],cwd=src,text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 for n in ['models.json','models.hpp']:assert (Path(tmp)/n).read_bytes()==(generated/n).read_bytes(),n
checks.append({'kind':'exact-source-only-regeneration','models':16,'models_json_sha256':sha(generated/'models.json'),'models_hpp_sha256':sha(generated/'models.hpp'),'embedded_catalogue_sha256':g['sha256'],'passed':True})
(D/'closure-checks.json').write_text(json.dumps({'reviewer':'/root/md1997_review','compiled_calls':0,'passed':True,'checks':checks},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'source_files':576,'ordinary_models':16}))
