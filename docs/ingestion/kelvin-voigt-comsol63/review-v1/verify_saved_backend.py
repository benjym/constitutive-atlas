"""Read-only independent reviewer verification of saved qualification; no compiled calls."""
from pathlib import Path
import hashlib,importlib.util,json,sys
D=Path(__file__).resolve().parent;B=D.parent;Q=B/'execution-v3';ROOT=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(Q));import study
study.verify_freeze()
freeze=json.loads((B/'build-v2/freeze.json').read_text())
for p,h in freeze['pins'].items():assert sha(B/p)==h,p
for p,h in freeze['configurations'].items():assert sha(ROOT/p)==h,p
receipt=json.loads((B/'build-v2/build-receipt.json').read_text())
assert sha(B/'build-v2/freeze.json')==receipt['release_configuration_freeze_sha256']
for p,h in receipt['files'].items():assert sha(ROOT/p)==h,p
for p,h in receipt['logs'].items():assert sha(B/'build-v2'/p)==h,p
source=json.loads((B/'build-v1/source-freeze.json').read_text())
for p,h in source['files'].items():assert sha(ROOT/'source'/p)==h,p
assert sha(B/'build-v1/source-freeze.json')==receipt['source_freeze_sha256']
for name in ['models.json','models.hpp']:assert (ROOT/'native-release/generated'/name).read_bytes()==(ROOT/'wasm-release/generated'/name).read_bytes()
descriptor=json.loads((B/'build-v2/native-descriptor.json').read_text());assert descriptor['sha256']=='059a30503294e9ea762e93bc318148617a66bb66fa2ba91b5191960ef10dbdb5'
cases=json.loads((Q/'cases.json').read_text())['cases'];raw={};reports={}
for backend in ['native','wasm']:
 rows=json.loads((Q/(backend+'-raw.json')).read_text());assert len(rows)==43
 actual=study.assess(cases,rows);saved=json.loads((Q/(backend+'-report.json')).read_text());assert actual==saved,backend
 for case,row in zip(cases,rows):
  for call in row['calls']:
   response=json.loads(call['stdout'])
   assert response['ok']==case['ok']
   if response['ok'] and case['kind']!='observe':assert response['model']==study.M and response['catalogue_hash']==descriptor['sha256']
 raw[backend]=rows;reports[backend]=actual
# Full structured responses include point side/time, all state/strain/rate/stress,
# null transition masks, settings and failure messages; parity alone is not a reference.
full_equal=sum(json.loads(n['calls'][0]['stdout'])==json.loads(w['calls'][0]['stdout']) for n,w in zip(raw['native'],raw['wasm']))
assert full_equal==43
for n,w in zip(raw['native'],raw['wasm']):
 if 'observation'in n:assert json.loads(n['observation'])==json.loads(w['observation'])
assert json.loads((Q/'parity-report.json').read_text())=={'passed':True,'cases':43,'maximum_primary_value_difference':0.0}
a=reports['native'];r={'identity':'kelvin-voigt-independent-saved-backend-audit-v1','reviewer_run':'/root/kelvin_scientific_review','compiled_calls_by_reviewer':0,'all_passed':True,'source_files_verified':len(source['files']),'build_type':'Release','model_sha256':source['model_sha256'],'catalogue_sha256':descriptor['sha256'],'cases_per_backend':43,'repeated_calls_per_backend':86,'negative_recovery_pairs_per_backend':8,'full_structured_responses_equal':full_equal,'preset_strain_error':a['errors']['creep-preset']['strain'],'tau20_strain_error':a['errors']['creep-tau20.0']['strain'],'coarse_strain_error':a['errors']['refine-coarse']['strain'],'fine_strain_error':a['errors']['refine-fine']['strain'],'directional_partials':a['directional_partial_relative_errors'],'passive_covariance_error_Pa':a['passive_basis_covariance_error_Pa'],'limitations':['Native requests run in separate processes; persistent-instance recovery is established by the single-instance Wasm collector','No actual browser or live-site evidence is asserted by this review']}
out=json.dumps(r,indent=2)+'\n';p=D/'saved-backend-check-results.json'
if p.exists():assert p.read_text()==out,'Refuse differing overwrite'
else:p.write_text(out)
print(out,end='')
