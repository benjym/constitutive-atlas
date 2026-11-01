"""Saved final-browser, exact-source closure and preservation checks only."""
from pathlib import Path
import json,hashlib,importlib.util,sys,subprocess
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'docs/ingestion/hill-abaqus2025';RELEASE=Path('/private/tmp/atlas-hill-release-v2');B=BASE/'delivery-v1/browser-v3'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('review_oracle',BASE/'source-v1/check_algebra.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
report=load(B/'report.json');extra=load(B/'extra-report.json');assert len(report['checks'])==24 and all(report['checks'].values());assert len(extra['checks'])==7 and all(extra['checks'].values())
for k in ['page_errors','console_errors','request_failures']:assert report[k]==[]
keys=['p_ref','K','Gmod','sigma_y','F','Gh','Hh','L','M','N'];comparisons=0;worst=[0.,0.];docs={}
for kind in ['preset','changed','initial','reset','replay','shear','latest']:
 doc=load(B/('hill-v3-browser-'+kind+'.json'));docs[kind]=doc;request=doc['request'];state=request['initial'][:6];assert doc['ok'];assert len(doc['points'])==len(request['increments'])+1
 for de,point,record in zip(request['increments'],doc['points'][1:],doc['records']):
  reference=oracle.endpoint(dict(zip(keys,request['parameters'])),state,de,precision=100);assert point['state']==record['response']['state']
  for i,(actual,expected) in enumerate(zip(point['state'],reference)):
   error=abs(actual-float(expected));assert error<=(.01+1e-10*abs(float(expected)) if i<6 else 1e-9);comparisons+=1;worst[i==6]=max(worst[i==6],error)
  state=reference[:6]
assert docs['preset']==docs['reset'];assert docs['changed']==docs['replay'];assert docs['latest']==extra['latest_result'];assert docs['latest']['request']['parameters'][4]==1.2
freeze=load(BASE/'execution-v1/source-freeze-v2.json');closure=load(BASE/'ci-v1/original-source-closure.json');assert len(closure['files'])==len(freeze['files'])==96
for row in closure['files']:
 assert freeze['files'][row['original_path']]==row['sha256'];assert sha(RELEASE/row['archived_path'])==row['sha256']
preserve=load(BASE/'delivery-v1/preservation-v1/preservation-result.json');assert preserve['all_checked_receipt_pairs_passed'];assert preserve['receipt_checks']==409
for p,h in preserve['files'].items():assert sha(RELEASE/p)==h['after']
assert sha(RELEASE/'tests/test_j2_main_routing.mjs')==sha(Path(__file__).parent/'test_j2_main_routing-proposed.mjs')
sys.path.insert(0,str(RELEASE))
from atlas.evidence import checked_receipt
pairs=load(BASE/'delivery-v1/preservation-v1/receipt-checks.json')
for row in pairs:checked_receipt(RELEASE,Path(row['document']),row['path'],row['sha256'])
for doc in set(row['document'] for row in pairs):
 old=subprocess.check_output(['git','show','dd7de01f:'+doc],cwd=ROOT)
 assert (RELEASE/doc).read_bytes()==old,doc

print(json.dumps(dict(passed=True,compiled_calls=0,final_browser_core_checks=24,final_browser_extra_checks=7,state_comparisons=comparisons,max_stress_error_Pa=worst[0],max_gamma_error=worst[1],preserved_checked_receipt_pairs=409,original_receipts_unchanged=True,original_reviewed_source_files=96,installed_routing_proposal_exact=True,exact_reset_and_replay=True,final_startup_errors=[]),indent=2))
