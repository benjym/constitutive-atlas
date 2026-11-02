"""Assess the actual live Chrome download against exact native controls and frozen source oracle."""
from pathlib import Path
import json,subprocess,hashlib,math
parse=json.loads
def loads(s):
 value=parse(s,parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
 def finite(x):
  if isinstance(x,float):assert math.isfinite(x)
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,list):
   for v in x:finite(v)
 finite(value);return value
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
B=Path('/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-live-v1')
p=loads((B/'default.json').read_text());accepted=loads((Path('/Users/bmar5496/code/constitutive-atlas/output/playwright/barodesy-sand-v3/default.json')).read_text());assert p['schema_version']=='atlas-laboratory-export-0.2' and p['result']['ok'];s=p['specification'];assert s==accepted['specification']
controls=B/'default-controls.txt';controls.write_text(','.join(s['loading']['controls_bits']));settings=s['integration_settings'];cmd=['/private/tmp/atlas-ramberg-osgood-delivery-v1/build-ramberg-native/atlas_solver','--mode','run-controls','--model',s['model'],'--parameters',','.join(map(str,s['parameters'])),'--initial',','.join(map(str,s['initial'])),'--protocol',str(s['protocol']),'--integration-settings',','.join(str(settings[k]) for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks']),'--laboratory-controls-file',str(controls),'--response-contract','stress-scope-0.1'];r=subprocess.run(cmd,capture_output=True,text=True);(B/'default-native.txt').write_text(r.stdout);assert r.returncode==0;native=loads(r.stdout);assert native['ok']
def scaled(a,b):
 if isinstance(a,dict):
  assert a.keys()==b.keys();return max([scaled(a[k],b[k]) for k in a]+[0.])
 if isinstance(a,list):
  assert len(a)==len(b);return max([scaled(x,y) for x,y in zip(a,b)]+[0.])
 if isinstance(a,(float,int)) and not isinstance(a,bool):return abs(a-b)/max(1.,abs(a),abs(b))
 assert a==b;return 0.
difference=scaled(native['points'],p['result']['points']);assert difference<=1e-10
ref=loads((PARENT/'references.json').read_text())['protocol-1-monotonic'];assert len(ref['points'])==len(p['result']['points']);errs=[0.,0.,0.]
for a,b in zip(p['result']['points'],ref['points']):
 vals=[max(abs(a['state'][i]-b[i]) for i in range(3)),abs(a['state'][6]-b[3]),max(abs(a['strain'][i]-b[i+4]) for i in range(3))];errs=[max(x,y) for x,y in zip(errs,vals)]
assert all(x<=v for x,v in zip(errs,[5,2e-7,2e-7]))
browser=loads((B/'live-browser.json').read_text());assert browser['run']['model']=='barodesy-sand' and browser['run']['curves']>0;assert browser['navigation']['related_model']=='#catalogue/barodesy-clay-2017' and browser['navigation']['laboratory_model']=='barodesy-sand';assert {x['href'] for x in browser['profile']['links']}=={'./evidence-records/catalogue/agent-reviews/barodesy-sand-agent-v1.json','./evidence-records/catalogue/agent-reviews/definitions/barodesy-sand-agent-v1.json','./evidence-records/catalogue/approved-models.json'};assert not browser['errors'] and not browser['warnings'];assert len(browser['profile']['links'])==3 and not browser['profile']['technicalOpen'];assert all(x['status']==200 for x in browser['fetched']);assert browser['mobile']['width']==browser['mobile']['scrollWidth']==390 and browser['mobile']['dialogWidth']<=390
artifact=loads((HERE/'artifact-receipt.json').read_text());site=Path(artifact['local_site']);cat=loads((site/'models.json').read_text());assert p['catalogue_hash']==cat['sha256']
for x in browser['fetched']:
 assert hashlib.sha256((site/x['path']).read_bytes()).hexdigest()==x['sha256']
report={'pass':True,'points':len(p['result']['points']),'exact_native_points':native['points']==p['result']['points'],'maximum_scaled_native_error':difference,'native_gate':1e-10,'independent_reference_max_stress_void_strain':errs,'independent_reference_budgets':[5,2e-7,2e-7],'catalogue_hash':cat['sha256'],'actual_live_url':'https://benjym.github.io/constitutive-atlas/#laboratory?model=barodesy-sand','profile_and_reachable_review_links':True,'mobile_no_horizontal_overflow':True,'console_errors':0,'console_warnings':0}
(HERE/'live-browser-assessment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
