"""Verify frozen source continuity, raw assessment and recorded browser comparison."""
from pathlib import Path
import json,hashlib,importlib.util
s=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('clay2013_complete_example',s/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
actual=m.assess();assert actual['pass']is True and actual==read(s/'assessment.json')
old=s.parent/'clay2013-preview-v1';assert read(old/'assessment.json')['pass']is False
for n,h in read(s/'parent-manifest.json').items():
 if n.startswith(('frozen/','models/','generated/')):assert sha(s/n)==h,n
for backend,reuse in read(s/'artifact-reuse.json')['backend'].items():
 assert sha(old/backend/'receipt.json')==reuse['receipt_sha256'];assert read(old/backend/'receipt.json')==reuse['receipt']
 parent=reuse['receipt'];assert parent['manifest_sha256']==sha(s/'parent-manifest.json')
 assert read(s/backend/'receipt.json')['artifacts']==parent['artifacts']
a=read(old/'requests.json');b=read(s/'requests.json');assert len(a)==18 and len(b)==20
for i in list(range(10))+list(range(11,18)):assert a[i]==b[i],i
new=dict(a[10]);new.update(id='actual-consumer-default',initial=a[0]['initial']);assert new==b[10]
legacy=dict(a[10]);legacy.update(id='legacy-100kPa-drained-incompatible',expected_ok=False);assert legacy==b[18]
recovery=dict(new);recovery.update(id='consumer-default-after-legacy-failure',same_result_as='actual-consumer-default');assert recovery==b[19]
p=read(old/'acceptance.json');q=read(s/'acceptance.json');assert p['success_gates']==q['success_gates']and p['parity']==q['parity']
raw=m.decode(next(x for x in read(s/'wasm/journal.json')if x['id']=='actual-consumer-default')['raw']);browser=read(s/'browser/export.json');assert browser['result']['ok']is True;assert m.physical(raw,'run')==m.physical(browser['result'],'run')
assert read(s/'browser/comparison.json')['pass']is True
for n,h in read(s/'results-manifest.json').items():assert sha(s/n)==h,n
print(json.dumps({'frozen_assessment_pass':True,'original_v1_default_gate_still_failed':True,'unchanged_original_nondefault_cases':17,'unchanged_numerical_budgets':True,'exact_runtime_source_and_artifact_reuse':True,'exact_browser_physical_channels':True,'requests_per_backend':20,'successful_caller_points_per_backend':actual['caller_points_per_backend'],'scientific_admission':False},indent=2))
