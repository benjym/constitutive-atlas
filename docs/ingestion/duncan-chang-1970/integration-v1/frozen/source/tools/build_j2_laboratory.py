"""Package the qualified J2 engine for the main laboratory (no standalone page)."""
import html
import json
import shutil
import tempfile
from pathlib import Path
from build_j2_web import ROOT, MODEL, sha

ASSETS='material-point-j2'

def bundle(dest,build):
    dest=Path(dest)
    # Validate the exact law/approval and generated metadata before copying assets.
    from atlas.compiler import generate
    from atlas.agent_review import approval_entry, validate_review
    from build_j2_web import MODEL_SHA256, APPROVAL
    build=Path(build)
    approval=json.loads((ROOT/APPROVAL).read_text())
    review_path=ROOT/approval['review']['path']
    review=validate_review(review_path,for_approval=True)
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    if [entry for entry in registry if entry['model_id']==MODEL]!=[approval] or approval!=approval_entry(review_path):
        raise ValueError('J2 exact approval/registry/review mismatch')
    model=ROOT/approval['definition']['path']
    if approval['definition']['sha256']!=MODEL_SHA256 or sha(model)!=MODEL_SHA256 or review['model']['id']!=MODEL or sha(review_path)!=approval['review']['sha256']:
        raise ValueError('J2 approved definition/review identity changed')
    with tempfile.TemporaryDirectory() as check:
        generate(check,[model]);expected=(Path(check)/'models.json').read_bytes()
    if not (build/'generated/models.json').is_file() or (build/'generated/models.json').read_bytes()!=expected:
        raise ValueError('Stale J2 generated catalogue: rebuild dedicated target')
    for name in ('j2.js','j2.wasm'):
        if not (build/name).is_file():raise ValueError('Missing qualified J2 artifact: '+name)
    assets=dest/ASSETS;assets.mkdir(parents=True,exist_ok=True)
    for name in ('j2.js','j2.wasm'):shutil.copyfile(build/name,assets/name)
    shutil.copyfile(build/'generated/models.json',assets/'models.json')
    shutil.copyfile(model,assets/(MODEL+'.json'))
    shutil.copyfile(ROOT/APPROVAL,assets/'approval.json');shutil.copyfile(review_path,assets/'review.json')
    identity=dict(model=MODEL,model_sha256=MODEL_SHA256,catalogue_hash=json.loads(expected)['sha256'],catalogue_sha256=sha(assets/'models.json'),module_sha256=sha(assets/'j2.js'),wasm_sha256=sha(assets/'j2.wasm'),approval_sha256=sha(assets/'approval.json'),review_sha256=sha(assets/'review.json'))
    (assets/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    for name in ('j2-contract.mjs','j2-laboratory.mjs'):
        shutil.copyfile(ROOT/'web'/name,dest/name)
    texts=[('Scientific review',ROOT/'docs/reviews/j2-scientific-v2/README.md'),
           ('Historical interface qualification',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/PUBLIC_DELIVERY.md'),
           ('Historical independent interface review',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/README.md'),
           ('Initial main interface review',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/README.md'),
           ('Independent interface review',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/README.md'),
           ('Catalogue-copy preservation review',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/catalogue-copy-followup/receipt.json')]
    body='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>J2 sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><p><a href="../index.html#laboratory?model='+MODEL+'">Main laboratory</a> · <a href="approval.json">Approval</a> · <a href="review.json">Exact accepted checklist</a></p>'
    for title,path in texts:
        body+='<h1 id="'+('law-review' if title=='Scientific review' else 'interface-review' if title=='Independent interface review' else 'historical-interface-review' if title=='Historical independent interface review' else 'initial-main-interface' if title=='Initial main interface review' else 'catalogue-copy-review' if title=='Catalogue-copy preservation review' else 'historical-interface')+'">'+html.escape(title)+'</h1><pre>'+html.escape(path.read_text())+'</pre>'
    body+='<p>The standalone interface above is retained historical evidence. The current interface mounts inside the main laboratory. Its delivery status is recorded separately; historical scientific approval does not itself approve browser packaging.</p></html>'
    (assets/'review.html').write_text(body)
    files=[dest/'j2-contract.mjs',dest/'j2-laboratory.mjs',*(p for p in assets.iterdir() if p.is_file() and p.name!='package-manifest.json')]
    manifest={str(p.relative_to(dest)):sha(p) for p in sorted(files)}
    (assets/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return identity

if __name__=='__main__':
    import sys
    bundle(*sys.argv[1:])
