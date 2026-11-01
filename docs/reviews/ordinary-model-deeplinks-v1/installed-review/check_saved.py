from pathlib import Path
import json,hashlib,sys,subprocess
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/ordinary-model-deeplinks-v1';O=P/'installed-review';sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
plan=read(P/'installation-plan-v1.json');res=read(P/'installation-result-v1.json');scan=read(P/'source-binding-scan-v2.json');assert sha(P/'source-binding-scan-v2.json')==plan['source_scan_sha256'];assert res['passed']and res['plan_sha256']==sha(P/'installation-plan-v1.json')and res['script_sha256']==sha(P/'apply_installation.py')
assert len(plan['redirected_pairs'])==23 and len(plan['unchanged_original_documents'])==17
for p,h in res['installed_files'].items():assert sha(R/p)==h,p
for p,x in plan['replacements'].items():assert sha(R/p)==x['sha256']==sha(R/x['candidate'])
for p,h in plan['unchanged_original_documents'].items():assert sha(R/p)==h,p
for p,h in plan['prior_paths'].items():assert sha(R/'catalogue/source-snapshots'/h/p)==h and (R/'catalogue/source-snapshots'/h/p).read_bytes()==(P/'prior-source'/p).read_bytes()
for p,m in plan['maps'].items():
 assert read(R/p)==m
 if plan['map_before'][p]:
  old=read(R/'catalogue/source-snapshots'/plan['map_before'][p]/p);assert all(m['documents'].get(k)==v for k,v in old['documents'].items())and all(e in m['entries']for e in old['entries'])
 for d,h in m['documents'].items():assert sha(R/d)==h,d
 for e in m['entries']:assert sha(R/e['archived_path'])==e['sha256'],e
for row in plan['redirected_pairs']:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
counts={}
for k in ['primary_references','secondary_source_map_references']:
 rows=[r for r in scan[k]if r['original_path']in plan['prior_paths']and r['resolution']!='unresolved'];counts[k]=len(rows)
 for row in rows:
  assert sha(R/row['document'])==row['document_sha256'],row['document']
  if row['resolution'].endswith('sidecar-entry'):assert sha(R/'catalogue/source-snapshots'/row['sha256']/row['original_path'])==row['sha256']
  else:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256'],row
assert sha(P/'independent-review/receipt.json')=='844b3eb6c9086e49fd167f757e0e9b6bff9f503de9f973b26894f424709500e2'
original_inputs=read(P/'independent-review/inputs.json')
for p,h in original_inputs.items():assert sha(checked_receipt(R,str((P/'independent-review/inputs.json').relative_to(R)),p,h))==h,p
pure=[]
for c in read(P/'installed-pure-checks-v1.json'):
 z=subprocess.run(c['command'],cwd=R,text=True,capture_output=True);assert z.returncode==c['exit_code']==0 and z.stdout==c['stdout']and z.stderr==c['stderr'];pure.append(json.loads(z.stdout)['checks'])
m=read(P/'candidate-package-v1.json');site=Path(m['path']);prior=read(R/'docs/ingestion/barodesy-clay-2017/root-registration-v1/package-manifest-v2.json')['files'];assert len(m['files'])==954 and set(m['files'])==set(prior)
assert [p for p in m['files']if m['files'][p]!=prior[p]]==['app.js']
for p,x in m['files'].items():assert sha(site/p)==x['sha256']and(site/p).stat().st_size==x['bytes'],p
assess=read(P/'candidate-browser-assessment-v1.json')
for p,h in assess['files'].items():assert sha(R/p)==h,p
assets=read(P/'candidate-browser/fetched-assets-v2.json');assert len(assets)==7
for a in assets:assert a['status']==200 and a['sha256']==m['files'][a['path']]['sha256']and a['size']==m['files'][a['path']]['bytes']
failed=[x for x in read(P/'candidate-browser/fetched-assets-v1.json')if x['status']==404];assert len(failed)==3 and all(x['path'].startswith('generated/')for x in failed)
nav=read(P/'candidate-browser/navigation-v2.json');states=nav['states'];assert len(states)==10 and nav['pageErrors']==[]
assert [s['model']for s in states[:3]]==['linear-elastic','barodesy-clay-2017','linear-elastic']
assert all(s['model']=='linear-elastic'and s['toast']for s in states[3:6]);assert [s['model']for s in states[6:]]==['maxwell-itasca900-zero-spin-ode','j2-linear-isotropic-hardening-be','barodesy-clay-2017','linear-elastic']
assert [s['ordinaryVisible']for s in states[6:]]==[False,False,True,True]
assert [s['visibleLaboratories']for s in states[6:9]]==[['laboratory','maxwell-laboratory'],['laboratory','j2-material-laboratory'],['laboratory']]
assert states[:9]==read(P/'candidate-browser/navigation-v1.json')['states']
initial=read(P/'candidate-browser/initial-load.json');assert initial['model']=='barodesy-clay-2017'and initial['ordinaryVisible']and not initial['exportDisabled']
doc=read(P/'candidate-browser/direct-barodesy.json');q=next(x for x in read(R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2/results/requests.json')if x['id']=='unchanged-default-drained');w=next(x for x in read(R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2/results/wasm.json')if x['id']==q['id']);assert doc['specification']==q['specification'];clean=lambda x:{k:v for k,v in x.items()if k!='elapsed_ms'};assert clean(doc['result'])==clean(w['result'])
js="""import{readFileSync}from'node:fs';import assert from'node:assert/strict';import{parseLaboratoryDocument}from'./web/laboratory-document.mjs';const p='docs/reviews/ordinary-model-deeplinks-v1',read=x=>JSON.parse(readFileSync(x)),site=read(p+'/candidate-package-v1.json').path,d=read(p+'/candidate-browser/direct-barodesy.json');assert.deepEqual(parseLaboratoryDocument(JSON.stringify(d),read(site+'/models.json')),d.specification);console.log('PASS: actual candidate browser export full public parser; no compiled calls');"""
z=subprocess.run(['node','--input-type=module','-e',js],cwd=R,text=True,capture_output=True);assert z.returncode==0,z.stderr
print(json.dumps({'passed':True,'additive_maps':len(plan['maps']),'prior_archives':len(plan['prior_paths']),'immutable_original_documents':17,'redirected_pairs':23,'prior_successful_affected_primary':counts['primary_references'],'prior_successful_affected_secondary':counts['secondary_source_map_references'],'installed_pure_checks':pure,'candidate_package_files':954,'actual_saved_navigation_states':10,'actual_saved_asset_hashes':7,'full_barodesy_result_equal_qualified_current_except_elapsed':True,'retained_wrong_path_404_probes':3,'reviewer_compiled_calls':0,'reviewer_browser_actions':0,'normal_installed_package_reviewed':False},indent=2))
