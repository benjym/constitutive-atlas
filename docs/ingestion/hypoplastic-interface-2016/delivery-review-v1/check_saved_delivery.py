"""Read/hash/reassess saved package/browser exports only; no runtime calls."""
from pathlib import Path
import json,hashlib,math,subprocess
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';OUT=Path(__file__).parent;B=P/'browser-v1';K=P/'package-v2';SITE=Path('/private/tmp/atlas-interface2016-delivery-v1/site-v2');R=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=read(K/'run.json');assert run['status']=='passed' and run['exit_code']==0 and run['source_post_unchanged'];assert len(run['source_pins'])==216
revision='dcc645785faa3c83d791fdad92e7f3a20cab9721';assert run['source_revision']==revision
for n,h in run['logs'].items():assert sha(K/n)==h
assert sha(K/'run_package.py')==run['wrapper_sha256'] and sha(K/'plan.json')==run['plan_sha256']
for n,h in run['source_pins'].items():assert sha(R/n)==h
manifest=read(K/'site-manifest.json');assert manifest['source_revision']==revision and len(manifest['entries'])==manifest['count']
for pin in manifest['entries']:assert sha(SITE/pin['path'])==pin['sha256'] and (SITE/pin['path']).stat().st_size==pin['size']
bm=read(B/'manifest.json');assert len(bm['entries'])==bm['count']==44
for pin in bm['entries']:assert sha(B/pin['path'])==pin['sha256'] and (B/pin['path']).stat().st_size==pin['bytes']
base=SITE/'material-point-interface2016/engine-path';identity=read(base/'identity.json');assert read(B/'displayed-identity.json')==identity
assert identity['definition_sha256']=='8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce'
assert identity['files']['review.json']=='13aa0f267736a9a5ad246e34461ead944fea5aa052ee74d2cec0ab3426a8ee0b'
assert identity['files']['engine.wasm']=='5bce95626e63474a1122d060e7f11262397d71fcab8cf87e82812b8166df41cb'
for n,h in identity['files'].items():assert sha(base/n)==h
served=read(B/'served-assets.json');assert served['passed'] and served['original_browser_http_errors']==[]
for e in served['assets']:assert e['status']==200 and sha(SITE/e['path'])==e['sha256']
assert read(B/'console.json')==[]
assert (B/'default.json').read_bytes()==(B/'reset.json').read_bytes()==(B/'replay.json').read_bytes()
# Replay offline author checker into NEW reviewer output; no engine import or material call.
out=OUT/'actual-exports-reassessment.json'
assessed=subprocess.run(['python3','-B',str(B/'check_actual_exports.py'),'--package',str(SITE),'--default',str(B/'default.json'),'--reset',str(B/'reset.json'),'--replay',str(B/'replay.json')],check=True,capture_output=True,text=True)
recheck=json.loads(assessed.stdout)
if out.exists():assert read(out)==recheck
else:out.write_text(assessed.stdout);assert recheck['state_stress_reference_comparisons']==66
# Independently strengthen all saved interior samples: exact stress binding, prescribed controls/coordinate and analytic density.
points=0;maxdensity=0.
for name in ['default','reset','replay']:
 doc=read(B/(name+'.json'));q=doc['request'];z0=q['context'];assert len(doc['result']['points'])==41
 for i,point in enumerate(doc['result']['points']):
  c=point['context'];s=c['state'];sn,sp,tx,tz,e=[s[k] for k in ['sigma_normal','sigma_plane','tau_x','tau_z','e']]
  assert point['observables']['stress']==[sn,sp,sp,math.sqrt(2)*tx,0.,math.sqrt(2)*tz]
  assert point['observables']['pressure']==(sn+2*sp)/3 and point['observables']['void_ratio']==e
  assert abs(c['coordinate']-(z0['coordinate']+q['progress']*i/40))<1e-14
  for k,v in c['controls'].items():assert abs(v-(z0['controls'][k]+(q['controls_end'][k]-z0['controls'][k])*i/40))<1e-14
  analytic=(1+z0['state']['e'])*math.exp(-(c['controls']['normal_strain']-z0['controls']['normal_strain']))-1;error=abs(e-analytic);assert error<2e-12;maxdensity=max(maxdensity,error);points+=1
for name,needle in [('invalid-state','Run failed: Path update rejected'),('stale-rejected','Import rejected: Imported model/engine/review identity differs'),('recovery','Completed prescribed interface path'),('latest-reset','Completed prescribed interface path'),('returned','Completed prescribed interface path')]:assert needle in (B/(name+'.txt')).read_text()
for name in ['invalidated','invalid-state','stale-rejected']:assert 'Export complete path run" [disabled]' in (B/(name+'.txt')).read_text()
assert read(B/'mobile-state-width.json')['scrollWidth']==375
support=read(K/'supported-package.json');assert support['status']=='passed' and len(support['ordinary'])==15 and len(support['named'])==1
db=read(K/'packaged-database.json');assert db['passed'] and len(db['tables'])==9 and all(v['all_old_rows_preserved'] for v in db['tables'].values())
qualification=read(B/'qualification.json');assert qualification['status']=='passed' and qualification['source_revision']==revision
result={'passed':True,'source_revision':revision,'package_exit':0,'seconds':run['end']-run['start'],'source_pins_unchanged':216,'site_manifest_files':manifest['count'],'browser_manifest_files':44,'served_asset_hashes':len(served['assets']),'prior_browser_GET_records':sum(x['browser_get_recorded'] for x in served['assets']),'exact_default_reset_replay':True,'frozen_initial_endpoint_comparisons':66,'allpoint_stress_binding_and_density_checks':points,'max_analytic_density_error':maxdensity,'supported_ordinary':15,'named_examples':1,'old_database_tables_preserved':9,'scope':'Independent saved-byte/evidence review only; no reviewer material/module/browser/build/remote calls; local E7, no E8/live claim.'}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
