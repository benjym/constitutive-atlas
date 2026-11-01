"""Bundle the independently approved SLS law with an isolated physical-time UI."""
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.compiler import generate
from atlas.agent_review import validate_review
MODEL = 'sls-comsol63-deviatoric-zero-spin-ode'
APPROVAL = 'docs/admission/sls-comsol63-approved-v1/approval.json'
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bundle(dest, build):
    dest, build = Path(dest), Path(build)
    approval = json.loads((ROOT / APPROVAL).read_text())
    registry = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
    if approval not in registry or approval['status'] != 'approved' or approval['model_id'] != MODEL:
        raise ValueError('SLS approved entry missing or inconsistent')
    review_path = ROOT / approval['review']['path']
    review = validate_review(review_path, for_approval=True)
    if sha(review_path) != approval['review']['sha256'] or review['model'] != dict(id=MODEL, **approval['definition']):
        raise ValueError('SLS review/model identity mismatch')
    for item in [approval['definition'], *approval['supporting_files']]:
        if sha(ROOT / item['path']) != item['sha256']:
            raise ValueError('Changed SLS evidence: ' + item['path'])
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp, [ROOT / approval['definition']['path']])
        expected = (Path(tmp) / 'models.json').read_bytes()
    candidates = [build / 'generated/models.json', build / 'sls-generated/models.json']
    catalogue = next((p for p in candidates if p.is_file()), None)
    if catalogue is None or catalogue.read_bytes() != expected:
        raise ValueError('Stale SLS generated catalogue: rebuild dedicated target')
    engine = dest / 'engine-sls'
    engine.mkdir(parents=True, exist_ok=True)
    for name in ['sls.js', 'sls.wasm']:
        shutil.copyfile(build / name, engine / name)
    shutil.copyfile(catalogue, engine / 'models.json')
    shutil.copyfile(ROOT / approval['definition']['path'], engine / (MODEL + '.json'))
    shutil.copyfile(ROOT / APPROVAL, dest / 'sls-approval.json')
    shutil.copyfile(review_path, dest / 'sls-agent-review.json')
    identity = dict(model=MODEL, model_sha256=approval['definition']['sha256'], catalogue_hash=json.loads(expected)['sha256'], module_sha256=sha(engine/'sls.js'), wasm_sha256=sha(engine/'sls.wasm'), approval_sha256=sha(ROOT/APPROVAL), review_sha256=sha(review_path))
    (engine / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    shutil.copyfile(ROOT / 'web/sls.html', dest / 'sls.html')
    text = (ROOT / 'docs/reviews/sls-comsol63-scientific-v1/README.md').read_text()
    (dest / 'sls-review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SLS independent scientific review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>SLS independent scientific review</h1><p><a href="sls.html">SLS laboratory</a> · <a href="sls-agent-review.json">Hash-bound checklist</a> · <a href="sls-approval.json">Approval</a></p><pre>' + html.escape(text) + '</pre></html>')
    manifest = {str(p.relative_to(dest)): sha(p) for p in sorted(dest.rglob('*')) if p.is_file() and p.name != 'package-manifest.json' and (p.parent == engine or p.name.startswith('sls'))}
    (engine/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__ == '__main__':
    bundle(*sys.argv[1:])
