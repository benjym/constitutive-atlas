"""Read-only preservation inventory and exact original emitter/input provenance."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
BASE='31125e2e809dad1af8dd30805af7b8c2937197d4'
def sha(b):return hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('receipt_scan',ROOT/'docs/ingestion/s-clay1/delivery-v2/claim-preservation-v1/scan.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
scan.TARGETS={'tests/test_catalogue.py','tests/test_controlled_time.py','atlas/cli.py','atlas/initialization.py'}
scan.EXCLUDE_PARTS.add('full-python-contracts-v1')
fast_spec=importlib.util.spec_from_file_location('fast_inventory',P/'fast_inventory.py');fast=importlib.util.module_from_spec(fast_spec);fast_spec.loader.exec_module(fast)
inventory=fast.inventory(ROOT,scan);(P/'bindings-before-v1.json').write_text(json.dumps(inventory,indent=2)+'\n')
baseline=ROOT/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/baseline';models=json.loads((baseline/'models.json').read_text())['models'];original=[]
for line in subprocess.check_output(['git','ls-tree',BASE+':models'],cwd=ROOT,text=True).splitlines():
 meta,name=line.split('\t');mode,kind,blob=meta.split()
 if kind!='blob' or not name.endswith('.json'):continue
 path='models/'+name;raw=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT);model=json.loads(raw)
 assert model==next(m for m in models if m['id']==model['id'])
 original.append({'path':path,'sha256':sha(raw),'git_blob':blob,'archived_path':'catalogue/source-snapshots/'+sha(raw)+'/'+path})
assert len(original)==len(models)==15
emitter=subprocess.check_output(['git','show',BASE+':atlas/compiler.py'],cwd=ROOT);prior=ROOT/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/preimages/base-31125e2e8/atlas/compiler.py';assert emitter==prior.read_bytes()
plan={'kind':'prospective-full-python-contracts-v1','historical_commit':BASE,'historical_emitter':{'path':'atlas/compiler.py','sha256':sha(emitter),'existing_preimage':str(prior.relative_to(ROOT)),'archived_path':'catalogue/source-snapshots/'+sha(emitter)+'/atlas/compiler.py'},'historical_models':original,'original_expected_output_pins':json.loads((baseline/'manifest.json').read_text()),'preservation':'Archive exact live test preimages and all changed maps; add per-document exact source/test redirects only with full old map-consumer closure. Preserve original receipts/assessments.','catalogue_contract':'Ordinary membership exact all_models; explicit index.html controlled_time route with physical_time/controlled_ode + exact independently approved definition/review/evidence. DBexecutable=int(id in all_models); VIBEapproveddefinition exact; realcandidate remains0,NULL. No broad approvedunion.','generation_contract':'Oldhash loop unchangedexpected on frozen31125 emitter/all15rawmodelglob; currentcompiler strict16fixture/liveglob/metadata coverage. New ownedhelper validates exactreceipt/Gitcontext; unknown/missing/corrupt bindings reject.','negative_gates':['unknown historicalcontext','missing receiptbinding','corrupt or missingarchive','forged/missing/stalecontrolledtimeapproval','ordinarygeneratorrejectscontrolledprofile','current16modelcoverage'],'owned_shared_paths':['tests/test_catalogue.py','tests/test_controlled_time.py'],'method':'Puretests/sourcegeneration/SQLite/savedreports only, subprocessmaterialcalls forbidden.'}
(P/'plan-v1.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'plan_sha256':sha((P/'plan-v1.json').read_bytes()),'historical_models':len(original),'emitter_sha256':sha(emitter),'primary_bindings':len(inventory['primary_references']),'secondary_bindings':len(inventory['secondary_source_map_references'])}))
