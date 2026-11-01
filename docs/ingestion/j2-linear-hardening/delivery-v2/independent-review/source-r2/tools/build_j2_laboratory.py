"""Package the qualified J2 engine for the main laboratory (no standalone page)."""
import html
import json
import shutil
import tempfile
from pathlib import Path
from build_j2_web import ROOT, MODEL, bundle as qualified_bundle, sha

ASSETS='material-point-j2'

def bundle(dest,build):
    dest=Path(dest)
    # Reuse exact approval/generated-metadata validation from the qualified v1
    # packager. Its historical pages stay in temporary storage, never in dest.
    with tempfile.TemporaryDirectory() as temporary:
        stage=Path(temporary)
        identity=qualified_bundle(stage,build)
        assets=dest/ASSETS
        assets.mkdir(parents=True,exist_ok=True)
        for name in ('j2.js','j2.wasm','models.json',MODEL+'.json','identity.json'):
            shutil.copyfile(stage/'engine-j2'/name,assets/name)
        for old,new in [('j2-approval.json','approval.json'),('j2-agent-review.json','review.json')]:
            shutil.copyfile(stage/old,assets/new)
    for name in ('j2-contract.mjs','j2-laboratory.mjs'):
        shutil.copyfile(ROOT/'web'/name,dest/name)
    texts=[('Scientific review',ROOT/'docs/reviews/j2-scientific-v2/README.md'),
           ('Historical interface qualification',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/PUBLIC_DELIVERY.md'),
           ('Independent interface review',ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/README.md')]
    body='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>J2 sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><p><a href="../index.html#laboratory?model='+MODEL+'">Main laboratory</a> · <a href="approval.json">Approval</a> · <a href="review.json">Exact accepted checklist</a></p>'
    for title,path in texts:
        body+='<h1 id="'+('law-review' if title=='Scientific review' else 'interface-review' if title=='Independent interface review' else 'historical-interface')+'">'+html.escape(title)+'</h1><pre>'+html.escape(path.read_text())+'</pre>'
    body+='<p>The standalone interface above is retained historical evidence. The current interface mounts inside the main laboratory. Its delivery status is recorded separately; historical scientific approval does not itself approve browser packaging.</p></html>'
    (assets/'review.html').write_text(body)
    files=[dest/'j2-contract.mjs',dest/'j2-laboratory.mjs',*(p for p in assets.iterdir() if p.is_file() and p.name!='package-manifest.json')]
    manifest={str(p.relative_to(dest)):sha(p) for p in sorted(files)}
    (assets/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return identity

if __name__=='__main__':
    import sys
    bundle(*sys.argv[1:])
