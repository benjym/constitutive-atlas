"""Package the exact approved Bingham schedule engine inside the main atlas.

This copies prequalified generic generated artifacts; it never builds or runs them.
"""
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.agent_review import approval_entry, validate_review
from atlas.compiler import generate

MODEL = 'bingham-comsol63-mises-perfect-zero-spin-ode'
COMPONENTS = ('bingham-laboratory.mjs', 'bingham-atlas-contract.mjs',
              'bingham-atlas-worker.mjs', 'laboratory-controller-router.mjs')
SOURCE_RECEIPT = 'docs/ingestion/bingham-comsol63/source-v1/source-receipts.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bundle(dest, build):
    dest, build = Path(dest), Path(build)
    registry = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
    matches = [entry for entry in registry if entry['model_id'] == MODEL]
    if len(matches) != 1:
        raise ValueError('One exact Bingham registry approval is required')
    approval = matches[0]
    record = ROOT / approval['review']['path']
    review = validate_review(record, for_approval=True)
    if approval != approval_entry(record) or sha(record) != approval['review']['sha256']:
        raise ValueError('Bingham exact registry/review binding differs')
    definition = ROOT / approval['definition']['path']
    if review['model']['id'] != MODEL or sha(definition) != approval['definition']['sha256']:
        raise ValueError('Bingham exact definition binding differs')
    if json.loads(definition.read_text())['schema_version'] != '0.3':
        raise ValueError('Bingham requires explicit schema0.3 formulation')
    receipts = [item for item in review['artifacts'] if item['path'] == SOURCE_RECEIPT]
    if len(receipts) != 1 or sha(ROOT / SOURCE_RECEIPT) != receipts[0]['sha256']:
        raise ValueError('Bingham source receipt must be bound to accepted review')
    contract = (ROOT / 'web/bingham-atlas-contract.mjs').read_text()
    if "modelSha256='" + sha(definition) + "'" not in contract:
        raise ValueError('Bingham browser contract is not pinned to exact approved definition')
    with tempfile.TemporaryDirectory() as temporary:
        generate(temporary, [definition])
        expected = (Path(temporary) / 'models.json').read_bytes()
    metadata = next((p for p in (build / 'generated/models.json', build / 'bingham-generated/models.json') if p.is_file()), None)
    if metadata is None or metadata.read_bytes() != expected:
        raise ValueError('Stale Bingham generated metadata; rebuild exact dedicated target')
    module = next((p for p in (build / 'bingham.mjs', build / 'bingham.js') if p.is_file()), None)
    if module is None or not (build / 'bingham.wasm').is_file():
        raise ValueError('Qualified Bingham Wasm artifacts missing')
    engine = dest / 'engine-bingham'
    engine.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(module, engine / 'bingham.mjs')
    shutil.copyfile(build / 'bingham.wasm', engine / 'bingham.wasm')
    (engine / 'models.json').write_bytes(expected)
    shutil.copyfile(definition, engine / (MODEL + '.json'))
    (engine / 'approval.json').write_text(json.dumps(approval, indent=2) + '\n')
    shutil.copyfile(record, engine / 'review.json')
    shutil.copyfile(ROOT / SOURCE_RECEIPT, engine / 'source-receipts.json')
    source_hashes = [{'url': item['url'], 'sha256': item['sha256']}
                     for item in json.loads((ROOT / SOURCE_RECEIPT).read_text())['receipts']
                     if item.get('original') and item.get('url')]
    if not source_hashes:
        raise ValueError('Bingham retained original source identities missing')
    body = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Bingham sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>Bingham independent scientific review</h1><p><a href="../index.html#laboratory?model=' + MODEL + '">Main atlas laboratory</a> · <a href="review.json">Accepted checklist</a> · <a href="approval.json">Approval and limitations</a> · <a href="source-receipts.json">Source identities</a></p><pre>'
    body += html.escape(json.dumps(review, indent=2))
    body += '</pre><h2>Approved scope</h2><pre>' + html.escape(json.dumps(approval['scope'], indent=2)) + '</pre><h2>Limitations</h2><pre>' + html.escape(json.dumps(approval['limitations'], indent=2)) + '</pre><p>Experimental comparison is unavailable. Scientific approval and functional browser qualification are separate evidence.</p></html>'
    (engine / 'review.html').write_text(body)
    for name in COMPONENTS:
        shutil.copyfile(ROOT / 'web' / name, dest / name)
    identity = dict(model=MODEL, model_sha256=sha(definition),
                    catalogue_hash=json.loads(expected)['sha256'],
                    catalogue_file_sha256=sha(engine / 'models.json'),
                    module_sha256=sha(engine / 'bingham.mjs'), wasm_sha256=sha(engine / 'bingham.wasm'),
                    approval_sha256=sha(engine / 'approval.json'), review_sha256=sha(record),
                    review_html_sha256=sha(engine / 'review.html'), source_receipts_sha256=sha(engine / 'source-receipts.json'),
                    source_sha256=source_hashes,
                    component_sha256={name: sha(dest / name) for name in COMPONENTS},
                    release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    (engine / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    names = [*COMPONENTS, *('engine-bingham/' + name for name in ('bingham.mjs', 'bingham.wasm', 'models.json', MODEL + '.json', 'approval.json', 'review.json', 'review.html', 'source-receipts.json', 'identity.json'))]
    (engine / 'package-manifest.json').write_text(json.dumps(dict(kind='bingham-general-atlas-laboratory-v1', files={name: sha(dest / name) for name in sorted(names)}), indent=2) + '\n')
    return identity


if __name__ == '__main__':
    bundle(*sys.argv[1:])
