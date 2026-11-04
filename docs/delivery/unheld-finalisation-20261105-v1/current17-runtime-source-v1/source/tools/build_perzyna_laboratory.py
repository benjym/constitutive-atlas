"""Package the exact approved Perzyna schedule engine inside the main atlas.

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

MODEL = 'perzyna-comsol63-mises-perfect-zero-spin-ode'
COMPONENTS = ('perzyna-laboratory.mjs', 'perzyna-atlas-contract.mjs',
              'perzyna-atlas-worker.mjs', 'laboratory-controller-router.mjs')
SOURCE_RECEIPT = 'docs/ingestion/perzyna-comsol63/source-v1/source-receipts.json'
BUILD_RECEIPT = 'docs/ingestion/perzyna-comsol63/execution-v1/build-receipt.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bundle(dest, build):
    dest, build = Path(dest), Path(build)
    registry = json.loads((ROOT / 'catalogue/approved-models.json').read_text())['models']
    matches = [entry for entry in registry if entry['model_id'] == MODEL]
    if len(matches) != 1:
        raise ValueError('One exact Perzyna registry approval is required')
    approval = matches[0]
    record = ROOT / approval['review']['path']
    review = validate_review(record, for_approval=True)
    if approval != approval_entry(record) or sha(record) != approval['review']['sha256']:
        raise ValueError('Perzyna exact registry/review binding differs')
    definition = ROOT / approval['definition']['path']
    if review['model']['id'] != MODEL or sha(definition) != approval['definition']['sha256']:
        raise ValueError('Perzyna exact definition binding differs')
    if json.loads(definition.read_text())['schema_version'] != '0.3':
        raise ValueError('Perzyna requires explicit schema0.3 formulation')
    receipts = [item for item in review['artifacts'] if item['path'] == SOURCE_RECEIPT]
    if len(receipts) != 1 or sha(ROOT / SOURCE_RECEIPT) != receipts[0]['sha256']:
        raise ValueError('Perzyna source receipt must be bound to accepted review')
    contract = (ROOT / 'web/perzyna-atlas-contract.mjs').read_text()
    if "modelSha256='" + sha(definition) + "'" not in contract:
        raise ValueError('Perzyna browser contract is not pinned to exact approved definition')
    with tempfile.TemporaryDirectory() as temporary:
        generate(temporary, [definition])
        expected = (Path(temporary) / 'models.json').read_bytes()
    metadata = next((p for p in (build / 'generated/models.json', build / 'perzyna-generated/models.json') if p.is_file()), None)
    if metadata is None or metadata.read_bytes() != expected:
        raise ValueError('Stale Perzyna generated metadata; rebuild exact dedicated target')
    module = next((p for p in (build / 'perzyna.mjs', build / 'perzyna.js') if p.is_file()), None)
    if module is None or not (build / 'perzyna.wasm').is_file():
        raise ValueError('Qualified Perzyna Wasm artifacts missing')
    bindings = [item for item in review['artifacts'] if item['path'] == BUILD_RECEIPT]
    if len(bindings) != 1 or sha(ROOT / BUILD_RECEIPT) != bindings[0]['sha256']:
        raise ValueError('Perzyna build receipt must be bound to accepted review')
    build_receipt = json.loads((ROOT / BUILD_RECEIPT).read_text())
    if build_receipt.get('kind') != 'perzyna-qualified-engine-build-v1' or build_receipt.get('model') != dict(id=MODEL, sha256=sha(definition)):
        raise ValueError('Perzyna reviewed build receipt has wrong model identity')
    artifacts = build_receipt.get('artifacts', {})
    if set(artifacts) != {'module', 'wasm', 'metadata'}:
        raise ValueError('Perzyna build receipt requires module, wasm and metadata')
    for key, path in (('module', module), ('wasm', build / 'perzyna.wasm'), ('metadata', metadata)):
        item = artifacts[key]
        if not isinstance(item, dict) or set(item) != {'path', 'sha256'} or not isinstance(item['path'], str) or not item['path'] or item['sha256'] != sha(path):
            raise ValueError('Perzyna artifact differs from exact reviewed build receipt: ' + key)
    engine = dest / 'engine-perzyna'
    engine.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(module, engine / 'perzyna.mjs')
    shutil.copyfile(build / 'perzyna.wasm', engine / 'perzyna.wasm')
    (engine / 'models.json').write_bytes(expected)
    shutil.copyfile(definition, engine / (MODEL + '.json'))
    (engine / 'approval.json').write_text(json.dumps(approval, indent=2) + '\n')
    shutil.copyfile(record, engine / 'review.json')
    shutil.copyfile(ROOT / SOURCE_RECEIPT, engine / 'source-receipts.json')
    shutil.copyfile(ROOT / BUILD_RECEIPT, engine / 'build-receipt.json')
    source_hashes = [{'url': item['url'], 'sha256': item['sha256']}
                     for item in json.loads((ROOT / SOURCE_RECEIPT).read_text())['receipts']
                     if item.get('url')]
    if not source_hashes:
        raise ValueError('Perzyna retained original source identities missing')
    body = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Perzyna sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>Perzyna independent scientific review</h1><p><a href="../index.html#laboratory?model=' + MODEL + '">Main atlas laboratory</a> · <a href="review.json">Accepted checklist</a> · <a href="approval.json">Approval and limitations</a> · <a href="source-receipts.json">Source identities</a></p><pre>'
    body += html.escape(json.dumps(review, indent=2))
    body += '</pre><h2>Approved scope</h2><pre>' + html.escape(json.dumps(approval['scope'], indent=2)) + '</pre><h2>Limitations</h2><pre>' + html.escape(json.dumps(approval['limitations'], indent=2)) + '</pre><p>Experimental comparison is unavailable. Scientific approval and functional browser qualification are separate evidence.</p></html>'
    (engine / 'review.html').write_text(body)
    for name in COMPONENTS:
        shutil.copyfile(ROOT / 'web' / name, dest / name)
    identity = dict(model=MODEL, model_sha256=sha(definition),
                    catalogue_hash=json.loads(expected)['sha256'],
                    catalogue_file_sha256=sha(engine / 'models.json'),
                    module_sha256=sha(engine / 'perzyna.mjs'), wasm_sha256=sha(engine / 'perzyna.wasm'),
                    approval_sha256=sha(engine / 'approval.json'), review_sha256=sha(record),
                    review_html_sha256=sha(engine / 'review.html'), source_receipts_sha256=sha(engine / 'source-receipts.json'),
                    build_receipt_sha256=sha(engine / 'build-receipt.json'),
                    source_sha256=source_hashes,
                    component_sha256={name: sha(dest / name) for name in COMPONENTS},
                    release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    (engine / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    names = [*COMPONENTS, *('engine-perzyna/' + name for name in ('perzyna.mjs', 'perzyna.wasm', 'models.json', MODEL + '.json', 'approval.json', 'review.json', 'review.html', 'source-receipts.json', 'build-receipt.json', 'identity.json'))]
    (engine / 'package-manifest.json').write_text(json.dumps(dict(kind='perzyna-general-atlas-laboratory-v1', files={name: sha(dest / name) for name in sorted(names)}), indent=2) + '\n')
    return identity


if __name__ == '__main__':
    bundle(*sys.argv[1:])
