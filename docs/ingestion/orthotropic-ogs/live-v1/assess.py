"""Assess saved actual browser exports and exact fetched bytes; no compiled execution."""
import json,hashlib,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
def read(n):return json.loads((H/(n+'.json')).read_text())
def log(n):return json.loads((H/(n+'.log')).read_text().split('### Result\n',1)[1].split('\n###',1)[0])
refs=read('references');count=0;straincount=0
for name in ['default','custom']:
 d=read(name);f=refs['fixtures'][name];assert d['ok'] and len(d['points'])==4
 for key in ['parameters','initial','increments']:assert d['request'][key]==f[key],(name,key)
 assert d['request']['settings']==[1e-11,1e-6,60,0,1,20]
 for p,r in zip(d['points'],f['points']):
  assert p['step']==r['step'] and len(p['state'])==6 and len(p['strain'])==6
  for a,e in zip(p['state'],r['state']):assert abs(a-e)<=1e-6,(name,p['step'],a,e);count+=1
  for a,e in zip(p['strain'],r['strain']):assert abs(a-e)<=1e-15,(name,p['step'],a,e);straincount+=1
public=json.loads((ROOT/'docs/ingestion/orthotropic-ogs/execution-v1/references.json').read_text())['cases']
for i,p in enumerate(read('default')['points'][1:]):
 r=next(c for c in public if c['id']==f'public-{i}')
 for a,e in zip(p['state'],r['expected_state']):assert abs(a-e)<=1e-6;count+=1
assert read('default')==read('replayed')==read('reset')==read('after-merged-switch');assert read('custom')==read('custom-fresh')
assert log('browser-catalogue')['actualCatalogueCardAndExplore']
merged=log('browser-merged-preservation');assert len(merged['checks'])==2 and all(x['selectable'] and x['panelVisible'] for x in merged['checks'])
latest=read('latest');assert latest['ok'] and len(latest['request']['increments'])==2 and len(latest['points'])==3
if len(sys.argv)!=2:raise SystemExit('usage: assess.py EXACT_TESTED_CI_UPLOAD_DIRECTORY')
site=Path(sys.argv[1]);handoff=read('release-handoff');assert handoff['commit']=='d1c3a19409adaa32791c105429a4167e5bac9d9d' and handoff['explicitCoordinatorGo'] and handoff['ciAllSuccess'] and handoff['pagesSuccess'];assert site.resolve()==Path(handoff['extractedUpload']).resolve()
binding=log('browser-assets-links-layout');assert binding['identity']==read('default')['provenance'];assert binding['identity']['model_sha256']=='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14'
assert len(binding['assets'])==13
for asset in binding['assets']:assert asset['status']==200 and hashlib.sha256((site/asset['path']).read_bytes()).hexdigest()==asset['sha256'],asset['path']
assert all(x['status']==200 for x in binding['links']);assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (H/'browser-console.log').read_text()
for p,h in read('prospective-freeze')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
r={'ok':True,'stateReferenceComparisons':count,'allSixStrainComparisons':straincount,'exactDefaultResetReplay':True,'exactCustomFreshRun':True,'latestTwoRowRequest':True,'exactFetchedPackageAssets':len(binding['assets']),'sourceLinksHTTP200':len(binding['links']),'cleanConsole':True,'prospectiveFreezeUnchanged':True,'mergedLadeMaxwellSelectable':True,'exactRevision':handoff['commit']}
(H/'assessment.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
