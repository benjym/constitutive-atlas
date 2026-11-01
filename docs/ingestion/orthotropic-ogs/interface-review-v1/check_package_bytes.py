"""Read/hash only independent package audit. Does not execute compiled artifacts."""
from pathlib import Path
import json,hashlib,sys
site=Path(sys.argv[1]);source=Path(sys.argv[2]);root=Path(__file__).resolve().parents[4];own=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prefix='material-point-orthotropic/';manifest=json.loads((site/prefix/'package-manifest.json').read_text());identity=json.loads((site/prefix/'identity.json').read_text())
required=['orthotropic-contract.mjs','orthotropic-laboratory.mjs']+[prefix+p for p in ['orthotropic.js','orthotropic.wasm','models.json','model.json','identity.json','approval.json','review.json','review.html']]
assert set(manifest)==set(required)
for p,h in manifest.items():assert sha(site/p)==h
for p,k in [('model.json','model_sha256'),('models.json','catalogue_sha256'),('orthotropic.js','module_sha256'),('orthotropic.wasm','wasm_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('review.html','review_html_sha256')]:assert sha(site/prefix/p)==identity[k]
assert identity['model_sha256']=='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14'
model=json.loads((site/prefix/'model.json').read_text());metadata=json.loads((site/prefix/'models.json').read_text());assert metadata['models']==[model] and metadata['sha256']==identity['catalogue_hash']
review=json.loads((site/prefix/'review.json').read_text());approval=json.loads((site/prefix/'approval.json').read_text());assert review['status']=='accepted' and not review['blocking_findings'] and all(r['outcome']=='pass' for r in review['checklist']);assert approval['status']=='approved' and approval['review']['sha256']==identity['review_sha256'] and approval['definition']['sha256']==identity['model_sha256']
assert sha(site/prefix/'review.json')==sha(root/'docs/ingestion/orthotropic-ogs/scientific-review-v1/review-proposal.json')
assert sha(site/'orthotropic-laboratory.mjs')==sha(source/'web/orthotropic-laboratory.mjs')==sha(root/'web/orthotropic-laboratory.mjs')
assert sha(site/'orthotropic-contract.mjs')==sha(source/'web/orthotropic-contract.mjs')==sha(root/'web/orthotropic-contract.mjs')
assert sha(site/'app.js')==sha(source/'web/app.js')
text=(site/'orthotropic-laboratory.mjs').read_text();assert 'The source uses tension-positive' not in text and 'the inspected source does not explicitly label its scalar sign convention' in text
assert not (site/'orthotropic.html').exists()
for f in ['manifest.json','approved-models.json']:
 old=json.loads((root/'docs/ingestion/orthotropic-ogs/atlas-v1/shared-before/catalogue'/f).read_text());new=json.loads((source/'catalogue'/f).read_text());assert [r for r in new['models'] if r.get('id')!='orthotropic-linear-elastic-ogs' and r.get('model_id')!='orthotropic-linear-elastic-ogs']==old['models']
report={'passed':True,'site':str(site),'guarded_assets':len(manifest),'asset_hashes':manifest,'identity':identity,'same_exact_scientific_review':True,'all_previous_catalogue_and_approval_entries_preserved':True,'F1_corrected_in_actual_packaged_module':True,'no_standalone':True,'source_files':{p:sha(source/p) for p in ['web/app.js','web/orthotropic-contract.mjs','web/orthotropic-laboratory.mjs','tools/build_orthotropic_laboratory.py','tools/test_orthotropic_package.mjs','tools/build_web.py','catalogue/manifest.json','catalogue/approved-models.json','.github/workflows/verify.yml']}}
print(json.dumps(report,indent=2))
