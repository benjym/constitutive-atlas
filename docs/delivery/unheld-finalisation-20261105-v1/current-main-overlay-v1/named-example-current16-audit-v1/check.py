"""Saved JSON and literal source audit only; no model/compiler/runtime calls."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source');OVER=P.parent/'final-active-v1/proposed'
def sha(b):return hashlib.sha256(b).hexdigest()
def identity(models):return sha(json.dumps(models,sort_keys=True,separators=(',',':')).encode())
files=sorted((BASE/'models').glob('*.json'));before=[json.loads(f.read_text()) for f in files];after=[json.loads((OVER/'models'/f.name).read_text()) if (OVER/'models'/f.name).is_file() else json.loads(f.read_text()) for f in files]
old,new=identity(before),identity(after);assert len(before)==len(after)==16 and old!=new
index=json.loads((BASE/'catalogue/laboratory-examples.json').read_text());rows=[]
for e in index['examples']:
 raw=(BASE/e['document_path']).read_bytes();d=json.loads(raw);assert sha(raw)==e['document_sha256'];assert d['schema_version']=='atlas-laboratory-export-0.2';assert d['catalogue_hash']==d['result']['catalogue_hash']==old
 assert next(m for m in before if m['id']==e['model'])==next(m for m in after if m['id']==e['model'])
 rows.append({'id':e['id'],'model':e['model'],'document_path':e['document_path'],'document_sha256':sha(raw),'definition_sha256':e['definition_sha256'],'specification_sha256':sha(json.dumps(d['specification'],sort_keys=True,separators=(',',':')).encode()),'points':len(d['result']['points']),'saved_catalogue_hash':d['catalogue_hash'],'current16_catalogue_hash':new,'import_guard_will_reject':True,'same_request_fresh_response_required':True})
sourcepins={p:sha((BASE/p).read_bytes()) for p in ['atlas/compiler.py','web/laboratory-document.mjs','web/laboratory-examples.mjs','web/laboratory-scope.mjs','tools/build_laboratory_examples.mjs']}
assert "doc.catalogue_hash===catalogue?.sha256" in (BASE/'web/laboratory-document.mjs').read_text()
assert "r.catalogue_hash===catalogue.sha256" in (BASE/'web/laboratory-scope.mjs').read_text()
assert 'for(const entry of index.examples)await prepareExample' in (BASE/'tools/build_laboratory_examples.mjs').read_text()
(P/'report.json').write_text(json.dumps({'status':'PASS-static-incompatibility-confirmed','original_sixteen_catalogue_hash':old,'proposed_sixteen_catalogue_hash':new,'ordinary_model_count':16,'examples':rows,'source_pins':sourcepins,'scope':'JSON/source reading and serialization hashing only; no compiler generation, model/material/runtime/process/browser calls'},indent=2)+'\n')
print(json.dumps({'old_catalogue':old,'new_catalogue':new,'fresh_existing_envelopes_required':len(rows)},indent=2))
