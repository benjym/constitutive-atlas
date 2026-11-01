"""Entire final-verification chain over invented owned evidence only."""
from pathlib import Path
import json,tempfile,hashlib
HERE=Path(__file__).resolve().parent
prefix=(HERE/'check_synthetic_upload.py').read_text().split('checks=[]')[0]
exec(compile(prefix,str(HERE/'check_synthetic_upload.py'),'exec'))
def put(root,name,d):(root/name).write_text(json.dumps(d))
def change(root,name,fn):
 d=json.loads((root/name).read_text());fn(d);put(root,name,d)
def final_fixture(root):
 fixture(root);p=json.loads((root/'LIVE_POLICY-v3.json').read_text());p.update({'required_jobs':['native-mac','native-linux','wasm','wasm-linux','deploy'],'base_url':'https://example.test/','route':'index.html#laboratory?model=m','browser_presets':['dense','loose'],'increments_per_preset':400})
 result={'elapsed_ms':1,'ok':True,'points':[{'state':[-0.0,1]} for _ in range(401)]};controls={'initial':[-0.0],'target':-0.0};ref={'rows':[{'name':n,'controls':controls,'phases':[{'result':result}]} for n in p['browser_presets']]};raw=json.dumps(ref).encode();(root/'public-presets-v1.json').write_bytes(raw);p['reference_report_sha256']=sha(raw);put(root,'LIVE_POLICY-v3.json',p)
 c.upload();identity=json.loads((root/'uploaded-identity.json').read_text())
 jobs=[{'name':n,'databaseId':10+i,'status':'completed','conclusion':'success'} for i,n in enumerate(p['required_jobs'])];put(root,'release-run.json',{'databaseId':2,'headSha':'a'*40,'status':'completed','conclusion':'success','jobs':jobs})
 url='https://github.com/benjym/constitutive-atlas/actions/runs/2/job/14';put(root,'deployment.json',{'deployment':{'sha':'a'*40,'ref':'main','environment':'github-pages','url':'deployment-api-url'},'statuses':[{'state':'success','environment':'github-pages','environment_url':p['base_url'],'target_url':url,'log_url':url,'deployment_url':'deployment-api-url'}]})
 put(root,'live-assets.json',{'passed':True,'revision':'a'*40,'run':2,'assets':[{'path':'app.js','status':200,'expected':sha(b'app'),'observed':sha(b'app')}]})
 links=['engine-implicit-path/'+n for n in ['review.html','approval.json','review.json','m.json']]
 for n in p['browser_presets']:
  put(root,'browser-'+n+'-export.json',{'provenance':identity,'controls':controls,'result':result})
  put(root,'browser-'+n+'-state.json',{'url':p['base_url']+p['route'],'model':'m','exportDisabled':False,'stateRows':402,'plots':[{'distinctPoints':3,'distinctY':2} for _ in range(4)],'links':links})
 put(root,'browser-console.json',[])
mutations={
 'wrong-ci-run':lambda r:change(r,'release-run.json',lambda d:d.update(databaseId=3)),
 'duplicate-job':lambda r:change(r,'release-run.json',lambda d:d['jobs'].__setitem__(0,d['jobs'][1])),
 'wrong-deploy-run':lambda r:change(r,'deployment.json',lambda d:d['statuses'][0].update(target_url='wrong-run')),
 'wrong-deploy-sha':lambda r:change(r,'deployment.json',lambda d:d['deployment'].update(sha='b'*40)),
 'wrong-live-body':lambda r:change(r,'live-assets.json',lambda d:d['assets'][0].update(observed='0'*64)),
 'stale-inventory':lambda r:change(r,'tested-upload.json',lambda d:d.update({'app.js':'0'*64})),
 'stale-identity':lambda r:change(r,'uploaded-identity.json',lambda d:d.update(release_revision='b'*40)),
 'point-zero-sign':lambda r:change(r,'browser-dense-export.json',lambda d:d['result']['points'][0]['state'].__setitem__(0,0.0)),
 'point-type':lambda r:change(r,'browser-dense-export.json',lambda d:d['result']['points'][0]['state'].__setitem__(1,True)),
 'missing-result-field':lambda r:change(r,'browser-dense-export.json',lambda d:d['result'].pop('ok')),
 'wrong-controls-zero-sign':lambda r:change(r,'browser-dense-export.json',lambda d:d['controls'].update(target=0.0)),
 'console-error':lambda r:put(r,'browser-console.json',['error'])}
checks=[]
for name in ['valid',*mutations]:
 with tempfile.TemporaryDirectory(dir=HERE,prefix='synthetic-final-') as tmp:
  root=Path(tmp);final_fixture(root)
  if name!='valid':mutations[name](root)
  try:c.final()
  except (AssertionError,ValueError,KeyError):assert name!='valid','valid entire final chain rejected'
  else:assert name=='valid','invalid entire chain accepted: '+name
  checks.append({'case':name,'passed':True})
result={'source_sha256':sha(code),'checks':checks,'scope':'Wholly invented local owned evidence; actual CI/live/browser untouched'}
(HERE/'synthetic-final-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
