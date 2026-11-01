import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[5];b=root/'docs/ingestion/original-cam-clay/integration-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());manifest=read(b/'package-manifest-final-v1.json');site=Path(manifest['package_path'])
for f,h in manifest['files'].items():assert sha(site/f)==h,f
mid='original-cam-clay-sw-electronic-log-recovery-v1';modelhash='637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34';reviewhash='a02f6524ee34d98d293453973aec3598251c34adc5ffd9b18082d19edfe0b790'
assert (site/'app.js').read_bytes()==(root/'web/app.js').read_bytes()
e=read(site/'evidence.json');rows=[r for r in e['agent_reviews'] if r['catalogue_id']==mid];assert len(rows)==1;r=rows[0]
assert r['status']=='accepted' and r['definition_current'] and r['registered_approval_id'];assert r['definition_sha256']==r['current_definition_sha256']==modelhash
assert sha(site/r['definition_path'])==modelhash;assert sha(site/'evidence-records'/r['record_path'])==r['record_sha256']==reviewhash
reg=read(site/'evidence-records/catalogue/approved-models.json');ap=[x for x in reg['models'] if x['id']==r['registered_approval_id']];assert len(ap)==1;assert ap[0]['definition']['sha256']==modelhash and ap[0]['review']['sha256']==reviewhash
assert (site/'evidence-records/catalogue/approved-models.json').read_bytes()==(root/'catalogue/approved-models.json').read_bytes()
dossier='docs/models/'+mid+'.md';assert (site/dossier).read_bytes()==(root/dossier).read_bytes();assert (site/(dossier+'.html')).is_file()
assert (site/'laboratory-control-support.json').read_bytes()==(root/'catalogue/laboratory-control-support.json').read_bytes()
for f in ['web-build-final-v5-process.json']:assert read(b/f)['returncode']==0
s=read(b/'supported-package-complete-v2.json');assert s['status']=='passed' and len(s['ordinary'])==13 and len(s['named'])==1
assert read(b/'recorded-wire-parity.json')['ok'];assert len(read(b/'recorded-wire-parity.json')['pairs'])==46
assert read(b/'numerics-parity.json')['status']=='passed';assert len(read(b/'numerics-parity.json')['pairs'])==17
paths=['package-manifest-final-v1.json','web-build-final-v5-process.json','supported-package-complete-v2.json','recorded-wire-parity.json','numerics-parity.json'];out={'status':'passed','compiled_calls':0,'package_file_hashes_verified':len(manifest['files']),'reviewed_receipt_hashes':{f:sha(b/f) for f in paths},'packaged_app_sha256':sha(site/'app.js'),'packaged_evidence_sha256':sha(site/'evidence.json')}
(b/'independent-review/final-results.json').write_text(json.dumps(out,indent=2)+'\n');print('Final static package checks pass,',len(manifest['files']),'file hashes; zero compiled calls')
