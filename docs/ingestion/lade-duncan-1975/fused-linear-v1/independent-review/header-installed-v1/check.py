from pathlib import Path
import json,hashlib,sys
H=Path(__file__).resolve().parent;R=H.parents[5];sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
from tools.build_implicit_path_laboratory import runtime_manifest
A=R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';I=A/'header-fix-v1/coordinator-install-v1';P=A/'header-fix-v1/preservation-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
installed=load(I/'INSTALLED.json');assert installed==load(I/'STATE.json') and installed['status']=='passed' and installed['checked_bindings']==19
assert installed['review_sha256']=='0881946431251e39327bc829e15aff866079f1a81f2bcec9ab52d2d588ffa604'
review=R/'docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/header-preservation-v2/review-receipt.json';assert sha(review)==installed['review_sha256']
w=load(P/'APPLY_WHITELIST.json');plan=load(P/'PROPOSAL.json');expected=w['metadata_writes']+[w['source_replacement']]
assert len(installed['operations'])==len(expected)==14
assert {r['original_path']:r for r in installed['operations']}=={r['original_path']:r for r in expected}
payloads={r['original_path']:P/r['candidate'] for r in plan['maps']}
payloads.update({r['canonical_archive']:P/r['snapshot'] for r in plan['archives']});payloads['web/app.js']=P/plan['source']['future_copy']
for row in installed['operations']:assert sha(R/row['original_path'])==sha(payloads[row['original_path']])==row['new_sha256']
assert [r['original_path'] for r in installed['operations'][:3]]==[r['original_path'] for r in w['metadata_writes'] if r['operation']=='create_canonical_snapshot']
assert installed['operations'][-1]['original_path']=='web/app.js'
for row in plan['checks']:checked_receipt(R,row['document'],row['original_path'],row['old_sha256'])
canonical=R/'catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json';record=validate_review(canonical,R,True);entry=approval_entry(canonical,R)
assert [e for e in load(R/'catalogue/approved-models.json')['models'] if e['model_id']==record['model']['id']]==[entry]
expected_binding=load(A/'EXPECTED_F_BINDING.json');assert runtime_manifest()==expected_binding['expected_runtime']
for name,h in expected_binding['expected_runtime']['files'].items():assert sha(R/'cpp/profiles/implicit-path-v1'/name)==h
before=load(A/'actual-package-v1/EXECUTION_SOURCE_FREEZE.json');now=load(A/'actual-package-v2/EXECUTION_SOURCE_FREEZE.json')
for name in ['contract','engine','laboratory','runner','worker']:
 path='web/implicit-path-'+name+'.mjs';assert before['files'][path]==now['files'][path]==sha(R/path)
index=load(A/'asset-provision-v1/INDEX.json')
for name,h in index['files'].items():assert sha(R/'.local/lade-main-atlas-v1/implicit-path'/name)==h
result=dict(status='passed',installed_operations=14,actual_preserved_bindings=19,scientific_approval='accepted exact review remains valid and registry exact',runtime_files=29,unchanged_web_components=5,restored_lade_assets=5,app_sha256=sha(R/'web/app.js'),scope='Actual saved installation source/provenance only; package-v2/browser not assessed')
(H/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
