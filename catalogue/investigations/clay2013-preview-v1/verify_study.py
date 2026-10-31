"""Verify retained failure evidence; never turns the failed admission gate green."""
from pathlib import Path
import importlib.util,json,hashlib
s=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('clay2013_frozen_assessment',s/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
actual=m.assess();assert actual==m.read(s/'assessment.json')
assert actual['pass']is False
assert set(actual['errors'])=={b+'/actual-browser-default '+k for b in ('native','wasm')for k in ('status','success message')}
requests=m.read(s/'requests.json');request=next(r for r in requests if r['id']=='actual-browser-default')
assert request['expected_ok']is True # retained prospective success gate, still failed
initial=list(map(float,request['initial'].split(',')))
for backend in ('native','wasm'):
 rows=m.read(s/backend/'journal.json');row=next(r for r in rows if r['id']==request['id']);r=m.decode(row['raw'])
 assert r['ok']is False and r['message']=='control or constitutive solve failed at step 1; last committed point retained'
 assert r['initial']==initial and r['parameters']==list(map(float,request['parameters'].split(',')))
 assert len(r['points'])==1
 point=r['points'][0];assert list(map(m.bits,point['state']))==list(map(m.bits,initial))
 assert point['strain']==[0]*6 and point['control']==0 and point['p']==100000 and point['q']==0
 assert row['request']==request
for n,pin in m.read(s/'default-diagnostics-v1/manifest.json').items():assert m.sha(s/'default-diagnostics-v1'/n)==pin
identity=m.read(s/'default-diagnostics-v1/identity.json');receipt=m.read(s/'native/receipt.json')
assert identity['sha256']==receipt['artifacts']['atlas_laboratory_preview']['sha256']
assert identity['original_manifest_sha256']==m.sha(s/'manifest.json')
assert identity['script_sha256']==m.sha(s/'default-diagnostics-v1/atlas-clay2013-diagnose.py')
print(json.dumps({'evidence_integrity':True,'prospective_admission_gate_pass':False,'default_failure_retained_in_both_backends':True,'compiled_artifact_binding':True,'requests_per_backend':18,'public_candidate_installed':False},indent=2))
