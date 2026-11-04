from pathlib import Path
import json,hashlib,csv,math
R=Path(__file__).resolve().parent;N=R.parent;P=N/'browser-v1';A=P/'artifacts';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append(n)
def clean(v):
 if isinstance(v,dict):return{k:clean(x)for k,x in v.items()if k!='elapsed_ms'}
 if isinstance(v,list):return[clean(x)for x in v]
 return v
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
def result(name):
 s=(A/name).read_text();return json.JSONDecoder().raw_decode(s[s.index('### Result')+len('### Result'):].lstrip())[0]
m=json.loads((P/'manifest.json').read_text());ck('98manifest members',len(m['files'])==98)
for row in m['files']:ck(row['path'],sha(P/row['path'])==row['sha256']and(P/row['path']).stat().st_size==row['bytes'])
frozen=N.parent/'unheld-finalisation-20261102-v1/baseline-five-browser-final-matrix-v1/browser-requests.json';requests=json.loads(frozen.read_text())
for r in requests:
 model=r['model'];cfg=json.JSONDecoder().raw_decode((A/('model-'+model+'.js')).read_text()[len('const cfg='):])[0];observed=result('model-'+model+'.js.result.txt')
 for kind,key in [('default','default_and_reset_request'),('parameter','parameter_edit'),('initial','initial_edit')]:
  doc=json.loads((A/(model+'-'+kind+'.json')).read_text());expected=r[key]if kind=='default'else r[key]['specification'];ck(model+' exact '+kind,doc['specification']==expected)
 param=json.loads((A/(model+'-parameter.json')).read_text())
 for kind in ['default','parameter','initial','latest','replay','mobile']:
  doc=json.loads((A/(model+'-'+kind+'.json')).read_text());finite(doc);ck(model+' finite101 '+kind,doc['result']['ok']is True and len(doc['result']['points'])==101 and doc['catalogue_hash']=='beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575')
  if kind in ['replay','mobile']:ck(model+' exact '+kind,clean(doc)==clean(param))
 ck(model+' rapidlatest wins',json.loads((A/(model+'-latest.json')).read_text())['specification']==r['default_and_reset_request'])
 if cfg['parameter_edit']['selector']=='#param-phi':ck(model+' degrees radians',abs(cfg['parameter_edit']['ui_value']*math.pi/180-cfg['parameter_edit']['backend_value'])<1e-15)
 for item in observed['hashes']:
  if '/definitions/'in item['url']:expected=sha(W/'models'/(model+'.json'))
  elif item['url'].endswith('approved-models.json'):expected=sha(W/'catalogue/approved-models.json')
  else:expected=sha(W/'catalogue/agent-reviews'/(model+'-v03-agent-v1.json'))
  ck(model+' HTTPexact '+item['url'],item['status']==200 and item['sha256']==expected)
 ck(model+' actualprofile/technical disclosure',bool(observed['profile'])and cfg['review_id']in observed['technical'] and'Matches current definition bytes'in observed['technical'])
 doc=json.loads((A/(model+'-default.json')).read_text());csvrows=list(csv.DictReader((A/(model+'-default.csv')).open()));ck(model+' csv101',len(csvrows)==101)
 for row,point in zip(csvrows,doc['result']['points']):
  ck(model+' csvPa',float(row['effective_mean_stress_Pa'])==point['p']and float(row['effective_signed_deviatoric_stress_Pa'])==point['q_signed']and row['stress_scope']=='effective'and row['pore_pressure_availability']=='unavailable'and row['pore_pressure_change_Pa']=='')
for entry in json.loads((W/'catalogue/laboratory-examples.json').read_text())['examples']:
 doc=json.loads((A/('named-'+entry['id']+'.json')).read_text());replay=json.loads((A/('named-'+entry['id']+'-replay.json')).read_text());packaged=json.loads((W/entry['document_path']).read_text());ck('namedexact '+entry['id'],clean(doc)==clean(replay)==clean(packaged))
negative=result('negative-mobile.js.result.txt');ck('crossmodel invalidation','cross-model-example-invalidated'in negative['checks']);ck('wrongcatalogue input preservation','wrong-catalogue-import-rejected-inputs-preserved'in negative['checks']);ck('all5mobile profile navigation',len([x for x in negative['checks']if x.startswith('mobile-profile-to-lab:')])==5)
ck('console0', 'Total messages: 0 (Errors: 0, Warnings: 0)'in(A/'console.raw').read_text())
print(json.dumps({'status':'PASS','count':len(checks),'checks':checks,'browser_or_compiled_launches':0,'frozen_requests_sha256':sha(frozen),'browser_manifest_sha256':sha(P/'manifest.json')},indent=2))
