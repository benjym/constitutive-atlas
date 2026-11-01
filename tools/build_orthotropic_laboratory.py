"""Guarded main-atlas bundle for the independently reviewed orthotropic law."""
import hashlib,html,json,shutil,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
MODEL='orthotropic-linear-elastic-ogs';MODEL_SHA='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14'
APPROVAL='docs/admission/orthotropic-ogs-approved-v1/approval.json';PREFIX='material-point-orthotropic'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bundle(dest,build):
 from atlas.compiler import generate
 from atlas.agent_review import approval_entry,validate_review
 dest,build=Path(dest),Path(build);approval=json.loads((ROOT/APPROVAL).read_text());review_path=ROOT/approval['review']['path'];review=validate_review(review_path,for_approval=True)
 if approval!=approval_entry(review_path):raise ValueError('Orthotropic approval/review mismatch')
 registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
 if [a for a in registry if a['model_id']==MODEL]!=[approval]:raise ValueError('Orthotropic registry mismatch')
 model=ROOT/approval['definition']['path']
 if sha(model)!=MODEL_SHA or approval['definition']['sha256']!=MODEL_SHA or review['model']['id']!=MODEL:raise ValueError('Orthotropic exact model identity mismatch')
 with tempfile.TemporaryDirectory() as t:
  generate(t,[model]);expected=(Path(t)/'models.json').read_bytes()
 if (build/'generated/models.json').read_bytes()!=expected:raise ValueError('Stale orthotropic catalogue: rebuild dedicated target')
 assets=dest/PREFIX;assets.mkdir(parents=True,exist_ok=True)
 for name in ['orthotropic.js','orthotropic.wasm']:shutil.copyfile(build/name,assets/name)
 shutil.copyfile(build/'generated/models.json',assets/'models.json');shutil.copyfile(model,assets/'model.json');shutil.copyfile(ROOT/APPROVAL,assets/'approval.json');shutil.copyfile(review_path,assets/'review.json')
 texts=[('Source, equations and conventions',ROOT/'docs/ingestion/orthotropic-ogs/source-v1/README.md'),('Exact scientific review',ROOT/'docs/ingestion/orthotropic-ogs/scientific-review-v1/report.md')]
 body='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Orthotropic sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><p><a href="../index.html#laboratory?model='+MODEL+'">Main laboratory</a> · <a href="approval.json">Exact approval</a> · <a href="review.json">Independent checklist</a> · <a href="model.json">Definition</a></p>'
 for title,path in texts:body+='<h1>'+html.escape(title)+'</h1><pre>'+html.escape(path.read_text())+'</pre>'
 body+='<p>Independent scientific approval covers the bounded native/Wasm strain-increment APIs. Browser and live delivery have separate checks. Fixed aligned axes, constant parameters, infinitesimal strain; illustrative parameters and no experimental validation.</p></html>'
 (assets/'review.html').write_text(body)
 for name in ['orthotropic-contract.mjs','orthotropic-laboratory.mjs']:shutil.copyfile(ROOT/'web'/name,dest/name)
 identity=dict(model=MODEL,model_sha256=MODEL_SHA,catalogue_hash=json.loads(expected)['sha256'],catalogue_sha256=sha(assets/'models.json'),module_sha256=sha(assets/'orthotropic.js'),wasm_sha256=sha(assets/'orthotropic.wasm'),approval_sha256=sha(assets/'approval.json'),review_sha256=sha(assets/'review.json'),review_html_sha256=sha(assets/'review.html'))
 (assets/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
 files=[dest/'orthotropic-contract.mjs',dest/'orthotropic-laboratory.mjs',*(p for p in assets.iterdir() if p.is_file() and p.name!='package-manifest.json')]
 (assets/'package-manifest.json').write_text(json.dumps({str(p.relative_to(dest)):sha(p) for p in sorted(files)},indent=2)+'\n');return identity
if __name__=='__main__':print(json.dumps(bundle(*sys.argv[1:]),indent=2))
