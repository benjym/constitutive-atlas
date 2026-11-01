"""Record this actual separate agent's completed review; never change registry."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
F='docs/ingestion/lade-duncan-1975/fused-linear-v1/'
A='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
S='docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/'
D=OUT.relative_to(ROOT).as_posix()+'/'
MODEL='lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
report=D+'MODEL_REVIEW.md';text=(ROOT/report).read_text()
definition='models/research/implicit-path/'+MODEL+'.json'
artifacts={report,definition,'docs/models/'+MODEL+'.md','docs/AGENT_REVIEW_POLICY.md','docs/FORMULATION_CONTRACT.md','schemas/model-v0.3.schema.json','tools/provision_implicit_path_assets.py','tools/build_implicit_path_laboratory.py','tools/generate_implicit_path.py',D+'check_final_binding.py',D+'binding-check-results.json',D+'generated/models.hpp',D+'generated/models.json',D+'write_record.py'}
for name in ['README.md','source-receipt.json','check_policy.json','check_algebra.py','algebra-results.json','independent-review/README.md','independent-review/check_algebra.py','independent-review/algebra-results.json','independent-review/spectral-contract-results.json','candidate-v1/triaxial_reference.py']:artifacts.add(S+name)
for name in ['RESULTS.md','FINAL_SCOPE.md','POLICY.json','triaxial-policy.json','FIDELITY_POLICY.json','lifecycle-corrected-policy.json','SUPPLEMENT_POLICY.json','triaxial-reference-results.json','native-build-receipt.json','wasm-build-receipt.json','durable-evidence-v1/MANIFEST.json','durable-evidence-v1/saved-evidence.tar.gz','legacy-prerequisite-recovery-v1/RECOVERY.json']:artifacts.add(F+name)
for name in ['EXPECTED_F_BINDING.json','profile-install-v1/coordinator-install-v1/INSTALLED.json','profile-install-v1/coordinator-install-v1/generation-receipt.json','qualified-assets-v1/implicit-path-qualification.json','asset-provision-v1/INDEX.json','asset-provision-v1/compiled-assets-v1.tar.gz','asset-provision-v1/SOURCE_FREEZE-v2.json']:artifacts.add(A+name)
for name in ['full-native-review-receipt.json','saved-native-early-gates-review-receipt.json','saved-wasm-full-review-receipt.json','saved-wasm-chain-source-review-receipt.json','qualified-build-v1/build-review.json','recovery-review/review-receipt.json','durable-evidence-review/review-receipt.json','profile-preservation-review/review-receipt.json','asset-provision-review-v2/review-receipt.json','asset-provision-review-v2/qualified-assets-review-receipt.json']:artifacts.add(F+'independent-review/'+name)
expected=json.loads((ROOT/(A+'EXPECTED_F_BINDING.json')).read_bytes())
for name in expected['expected_runtime']['files']:artifacts.add('cpp/profiles/implicit-path-v1/'+name)
evidence={
 'source_provenance':[S+'source-receipt.json',S+'independent-review/README.md'],
 'equation_fidelity':[S+'README.md',S+'independent-review/algebra-results.json',F+'FINAL_SCOPE.md'],
 'conventions_dimensions':[definition,S+'independent-review/README.md'],
 'initialization_domain':[definition,F+'FINAL_SCOPE.md',F+'SUPPLEMENT_POLICY.json'],
 'integration_transactions':[F+'FINAL_SCOPE.md',F+'independent-review/full-native-review-receipt.json',F+'independent-review/saved-wasm-chain-source-review-receipt.json'],
 'independent_numerical_evidence':[S+'independent-review/algebra-results.json',S+'candidate-v1/triaxial_reference.py',F+'triaxial-reference-results.json',F+'independent-review/full-native-review-receipt.json',F+'RESULTS.md'],
 'backend_delivery':[F+'independent-review/qualified-build-v1/build-review.json',F+'independent-review/saved-wasm-full-review-receipt.json',F+'independent-review/saved-wasm-chain-source-review-receipt.json',D+'binding-check-results.json'],
 'applicability_claims':[F+'FINAL_SCOPE.md',F+'RESULTS.md','docs/models/'+MODEL+'.md'],
 'reproducibility_rights':[F+'independent-review/durable-evidence-review/review-receipt.json',F+'independent-review/recovery-review/review-receipt.json',A+'asset-provision-v1/INDEX.json',A+'asset-provision-v1/compiled-assets-v1.tar.gz',F+'independent-review/asset-provision-review-v2/qualified-assets-review-receipt.json']}
checklist=[]
for item,refs in evidence.items():
    reason=text.split('## '+item+'\n\n',1)[1].split('\n\n',1)[0]
    checklist.append({'id':item,'outcome':'pass','reason':reason,'evidence':[report+'#'+item,*refs]})
record={
 'schema_version':'0.1','kind':'agent-model-review','id':MODEL+'-agent-review-v1',
 'created_at':'2026-11-01T14:04:35Z','source_commit':'f4fce681aeec90c963ce69152b5e59b6094f8cc0',
 'model':{'id':MODEL,'path':definition,'sha256':'120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'},
 'status':'accepted',
 'reviewer':{'kind':'agent','name':'Independent Lade source and numerical reviewer','run_id':'/root/lade_source_review','independence_basis':'Actual separately dispatched run, distinct from /root model transcription/implementation. Personally reviewed all 17 original rendered pages, source/convention algebra, contract choices and exact saved numerical/backend evidence. Reconciles independent work actually performed throughout this run, not a fresh-context claim. Authored review scripts/findings, not the model or material implementation; no compiled artifacts executed by reviewer.'},
 'author_run_ids':['/root'],
 'scope':'Exact complete Lade–Duncan 1975 law in canonical v0.3 model120b93f3, with disclosed midpoint elasticity, endpoint local Eq19 plastic work, signed history carrier and generalized repeated-minimum choices. Fixed-frame small-strain compression-positive Mandel, zero-pore-pressure mechanical Cauchy stress; named Table1 preparations and frozen F parameter/protocol/native/Wasm API case matrices only. Exact installed generic F runtime acb8756e and accepted model/generated/artifact binding. Compiled-scope E5 approval; actual public packaging/preset/browser/live acceptance excluded.',
 'limitations':[
  'No postfailure continuation or general three-dimensional domain-event/convergence theorem; the repeated-minimum cluster-average generalized Jacobian is not a classical directional derivative.',
  'No arbitrary schema-parameter rectangle, initialization/history, cycles or custom browser input robustness claim. Named 60 kPa preparations differ from the 100 kPa schema example.',
  'Fixed small-strain/spatial zero-pore-pressure mechanical embedding only; no coupled/undrained, physical-time, finite-rotation or FE claim.',
  'Experimental calibration and measurement validation are absent. The supplied copyrighted original PDF remains private and is linked/hashed, not redistributed.',
  'Four fixed-control nonmonotonic trend diagnostics remain false; joint refinement, source bounds and all eleven numerical gates pass. Earlier failures/timeouts and original/recovered prerequisite outputs remain retained.',
  'Registry integration, actual asset restoration, public package/preset/actual-browser E7 and live E8 qualification remain separate guarded tasks. Deployment is not authorized.'],
 'blocking_findings':[],
 'artifacts':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in sorted(artifacts)],
 'checklist':checklist}
destination=ROOT/'catalogue/agent-reviews'/(MODEL+'-agent-v1.json')
assert not destination.exists(),'Never rewrite an existing review'
destination.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'path':destination.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'artifacts':len(artifacts)}))
