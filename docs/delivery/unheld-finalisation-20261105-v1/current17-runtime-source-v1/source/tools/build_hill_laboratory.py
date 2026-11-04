"""Guarded Hill package for the main laboratory; never builds or executes physics."""
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODEL = 'hill-abaqus2025-perfect-be'
MODEL_SHA256 = '1f98a70a68098d95804639e3abeb69da57e7ceeaf302d621e4738db4340e2621'
ASSETS = 'material-point-hill'
EXECUTION = 'docs/ingestion/hill-abaqus2025/execution-v1/'
REVIEW = 'catalogue/agent-reviews/hill-abaqus2025-agent-v1.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact_digest(receipt, suffix):
    found = [value for name, value in receipt['artifacts'].items() if name.endswith('/'+suffix)]
    if len(found) != 1 or not re.fullmatch('[0-9a-f]{64}', found[0]):
        raise ValueError('Ambiguous/missing reviewed build artifact: '+suffix)
    return found[0]


def bundle(dest, build):
    from atlas.compiler import generate
    from atlas.agent_review import approval_entry, validate_review
    dest, build = Path(dest), Path(build)
    review_path = ROOT/REVIEW
    review = validate_review(review_path, for_approval=True)
    if review['model']['id'] != MODEL or review['model']['sha256'] != MODEL_SHA256:
        raise ValueError('Hill review does not bind the final candidate')
    approvals = [entry for entry in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models'] if entry['model_id'] == MODEL]
    if len(approvals) != 1 or approvals[0] != approval_entry(review_path):
        raise ValueError('Hill registry/accepted-review approval mismatch')
    approval = approvals[0]
    model = ROOT/approval['definition']['path']
    if sha(model) != MODEL_SHA256 or approval['definition']['sha256'] != MODEL_SHA256 or approval['review']['path'] != REVIEW or approval['review']['sha256'] != sha(review_path):
        raise ValueError('Hill exact model/review identity mismatch')
    pinned = {entry['path']: entry['sha256'] for entry in review['artifacts']}
    receipt_path = ROOT/(EXECUTION+'build-receipt.json')
    for name in ['build-receipt.json', 'references.json', 'negative-requests.json', 'POLICY.md']:
        path = EXECUTION+name
        if pinned.get(path) != sha(ROOT/path):
            raise ValueError('Hill qualification input is not bound by accepted review: '+path)
    receipt = json.loads(receipt_path.read_text())
    with tempfile.TemporaryDirectory() as check:
        generate(check, [model])
        expected = (Path(check)/'models.json').read_bytes()
    if (build/'generated/models.json').read_bytes() != expected:
        raise ValueError('Stale Hill generated catalogue; rebuild dedicated target')
    for name in ['hill.js', 'hill.wasm', 'generated/models.json']:
        if sha(build/name) != artifact_digest(receipt, name):
            raise ValueError('Provided Hill artifact differs from reviewed build: '+name)
    # Guard the caller-visible contract too, before writing any destination assets.
    contract = (ROOT/'web/hill-contract.mjs').read_text()
    if f"MODEL='{MODEL}'" not in contract or f"MODEL_SHA256='{MODEL_SHA256}'" not in contract:
        raise ValueError('Hill browser contract has a different model identity')
    assets = dest/ASSETS
    if assets.exists() and any(assets.iterdir()):
        raise ValueError('Hill package destination must be empty; preserve prior package evidence')
    assets.mkdir(parents=True, exist_ok=True)
    for name in ['hill.js', 'hill.wasm']:
        shutil.copyfile(build/name, assets/name)
    (assets/'models.json').write_bytes(expected)
    shutil.copyfile(model, assets/(MODEL+'.json'))
    (assets/'approval.json').write_text(json.dumps(approval, indent=2)+'\n')
    shutil.copyfile(review_path, assets/'review.json')
    shutil.copyfile(receipt_path, assets/'build-receipt.json')
    for name in ['references.json', 'negative-requests.json', 'POLICY.md']:
        shutil.copyfile(ROOT/(EXECUTION+name), assets/name)
    dossier = ROOT/'docs/models/hill-abaqus2025.md'
    shutil.copyfile(dossier, assets/'dossier.md')
    identity = dict(model=MODEL, model_sha256=MODEL_SHA256,
                    catalogue_hash=json.loads(expected)['sha256'], catalogue_sha256=sha(assets/'models.json'),
                    module_sha256=sha(assets/'hill.js'), wasm_sha256=sha(assets/'hill.wasm'),
                    approval_sha256=sha(assets/'approval.json'), review_sha256=sha(assets/'review.json'))
    (assets/'identity.json').write_text(json.dumps(identity, indent=2)+'\n')
    for name in ['hill-contract.mjs', 'hill-laboratory.mjs']:
        shutil.copyfile(ROOT/'web'/name, dest/name)
    body = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Hill sources and reviewed scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style>'
    body += '<p><a href="../index.html#laboratory?model='+MODEL+'">Main laboratory</a> · <a href="approval.json">Approval</a> · <a href="review.json">Exact independent checklist</a> · <a href="'+MODEL+'.json">Exact model</a> · <a href="dossier.md">Dossier</a> · <a href="references.json">Frozen independent references</a> · <a href="build-receipt.json">Reviewed build receipt</a></p>'
    body += '<h1>Hill associative perfect plasticity</h1><p>Dry total stress, infinitesimal strain and fixed aligned material axes. Isotropic linear elasticity, positive Hill coefficients and perfect plasticity. Atlas backward Euler has no physical clock. All six Mandel stresses and the latest temporary multiplier are shown and exported. No accumulated plastic-strain state, hardening, viscosity, finite rotation, FE-host qualification or experimental validation. Custom paths and the broad machine bounds are exploratory.</p><p>Sources are linked rather than redistributed. Copyrighted Abaqus documentation and vendor implementation binaries are not bundled. No vendor code is executed. This package uses the declarative Atlas model and common engine.</p>'
    for title, text in [('Approved scope', review['scope']), ('Review limitations', '\n'.join(review['limitations'])), ('Source and formulation dossier', dossier.read_text()), ('Frozen numerical policy', (ROOT/(EXECUTION+'POLICY.md')).read_text())]:
        body += '<h2>'+html.escape(title)+'</h2><pre>'+html.escape(text)+'</pre>'
    body += '<p>Source: <a href="https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-anisoyield.htm">Abaqus2025 anisotropic yield</a> · <a href="https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-metalplastic.htm">Metal plasticity</a> · <a href="https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-linearelastic.htm">Linear elasticity</a>. Scientific approval does not itself certify browser delivery; actual package and browser qualification are recorded separately.</p></html>'
    (assets/'review.html').write_text(body)
    files = [dest/'hill-contract.mjs', dest/'hill-laboratory.mjs', *(p for p in assets.iterdir() if p.is_file())]
    manifest = {p.relative_to(dest).as_posix(): sha(p) for p in sorted(files)}
    (assets/'package-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return identity


if __name__ == '__main__':
    import sys
    bundle(*sys.argv[1:])
