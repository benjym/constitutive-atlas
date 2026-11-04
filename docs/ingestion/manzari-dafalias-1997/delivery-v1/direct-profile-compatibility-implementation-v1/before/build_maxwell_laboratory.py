"""Bundle the main-atlas Maxwell laboratory only with exact reviewed qualification."""
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
from atlas.agent_review import validate_review, approval_entry
from atlas.compiler import generate
from atlas.evidence import checked_receipt

MODEL = 'maxwell-itasca900-zero-spin-ode'
DEFINITION = 'models/research/maxwell/' + MODEL + '.json'
APPROVAL = 'docs/admission/maxwell-agent-v2/approval.json'
COMPONENTS = ('maxwell-atlas-contract.mjs', 'maxwell-atlas-engine.mjs',
              'maxwell-atlas-runner.mjs', 'maxwell-atlas-worker.mjs',
              'maxwell-laboratory.mjs', 'laboratory-controller-router.mjs')
GATES = ('native_references', 'wasm_references', 'transactions', 'parity', 'presets')
INTERFACE_REVIEW_SHA256 = 'c6d480f8921677079381f80d228272ab7b95207fa0d63d225c3abc0fd71f1584'
INTERFACE_REVIEW = 'docs/ingestion/maxwell-itasca900/atlas-controller-v1/independent-review/receipt.json'
REFERENCE = 'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode()


def source_manifest():
    paths = {ROOT/'cmake/maxwell/CMakeLists.txt', ROOT/'cmake/AtlasScalarFunctions.cmake', ROOT/DEFINITION}
    paths.update(p for p in (ROOT/'cpp/scalar-functions').rglob('*') if p.is_file())
    for directory, suffixes in [('atlas', {'.py'}), ('cpp', {'.cpp', '.hpp'}), ('schemas', {'.json'})]:
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
    files = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in sorted(paths)}
    return {'files': files, 'sha256': digest(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())}


def passed_gates(value):
    return isinstance(value, dict) and set(value) == set(GATES) and all(v is True for v in value.values())


def local_file(root, relative):
    name = Path(relative)
    path = (root/name).resolve()
    if name.is_absolute() or '..' in name.parts or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Unsafe or missing Maxwell qualification artifact: ' + str(relative))
    return path


def bundle(destination, build):
    destination, build = Path(destination), Path(build)
    before = source_manifest()
    approval_bytes = (ROOT/APPROVAL).read_bytes()
    approval = json.loads(approval_bytes)
    registry = json.loads((ROOT/'catalogue/approved-models.json').read_bytes())
    if approval not in registry['models'] or approval['model_id'] != MODEL or approval['status'] != 'approved':
        raise ValueError('Maxwell exact approved registry entry missing or changed')
    review_path = local_file(ROOT, approval['review']['path'])
    review_bytes = review_path.read_bytes()
    review = validate_review(review_path, root=ROOT, for_approval=True)
    if approval != approval_entry(review_path, root=ROOT):
        raise ValueError('Maxwell approval differs from canonical reviewed scope')
    definition = (ROOT/DEFINITION).read_bytes()
    if approval['definition'] != {'path': DEFINITION, 'sha256': digest(definition)} or review['model'] != dict(id=MODEL, **approval['definition']) or digest(review_bytes) != approval['review']['sha256']:
        raise ValueError('Maxwell scientific model/review binding differs')
    for item in approval.get('supporting_files', []):
        checked_receipt(ROOT, APPROVAL, item['path'], item['sha256'])
    with tempfile.TemporaryDirectory() as temporary:
        generate(temporary, [ROOT/DEFINITION])
        catalogue = (Path(temporary)/'models.json').read_bytes()
    if local_file(build, 'generated/models.json').read_bytes() != catalogue:
        raise ValueError('Stale Maxwell generated catalogue; rebuild exact dedicated target')
    module_path = next((build/name for name in ('maxwell.mjs', 'maxwell.js') if (build/name).is_file()), None)
    if module_path is None:
        raise ValueError('Maxwell module missing')
    module = local_file(build, module_path.name).read_bytes()
    wasm = local_file(build, 'maxwell.wasm').read_bytes()
    qualification_bytes = local_file(build, 'maxwell-qualification.json').read_bytes()
    qualification = json.loads(qualification_bytes)
    binding = {'model_sha256': digest(definition), 'catalogue_file_sha256': digest(catalogue),
               'module_sha256': digest(module), 'wasm_sha256': digest(wasm),
               'source_manifest_sha256': before['sha256'], 'reference_policy_sha256': digest((ROOT/REFERENCE).read_bytes())}
    if qualification.get('schema_version') != 'maxwell-qualified-build-1' or qualification.get('model') != MODEL or qualification.get('status') != 'passed' or qualification.get('binding') != binding or not passed_gates(qualification.get('gates')) or not isinstance(qualification.get('implementation_run'), str) or not qualification['implementation_run'].strip():
        raise ValueError('Missing, stale or failed Maxwell build qualification')
    reviewer = qualification.get('independent_review', {})
    accepted_bytes = local_file(build, reviewer.get('path', '')).read_bytes()
    accepted = json.loads(accepted_bytes)
    if digest(accepted_bytes) != reviewer.get('sha256') or accepted.get('status') != 'accepted' or accepted.get('binding') != binding or not passed_gates(accepted.get('gates')) or not isinstance(accepted.get('reviewer_run'), str) or not accepted['reviewer_run'].strip() or accepted['reviewer_run'] == qualification['implementation_run']:
        raise ValueError('Independent Maxwell build review missing or changed')
    components = {name: (ROOT/'web'/name).read_bytes() for name in COMPONENTS}
    interface_review_bytes = (ROOT/INTERFACE_REVIEW).read_bytes()
    interface_review = json.loads(interface_review_bytes)
    if digest(interface_review_bytes) != INTERFACE_REVIEW_SHA256 or interface_review.get('unresolved_in_scope_blockers') != [] or interface_review.get('decision') != 'accepted after exact-model and verified-Wasm-consumption fixes':
        raise ValueError('Maxwell interface review is not the exact accepted decision')
    reviewed = {item['path']: item['sha256'] for item in interface_review['files']}
    for name, data in components.items():
        if name != 'laboratory-controller-router.mjs' and reviewed.get('web/'+name) != digest(data):
            raise ValueError('Changed reviewed Maxwell interface: '+name)
    source = (ROOT/'docs/reviews/maxwell-checklist-v2/README.md').read_text()
    review_html = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Maxwell independent review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>Maxwell independent agent review</h1><p><a href="../index.html#laboratory?model='+MODEL+'">Main atlas laboratory</a> · <a href="review.json">Checklist</a> · <a href="approval.json">Approved scope</a> · <a href="qualification.json">Current build qualification</a></p><pre>'+html.escape(source)+'</pre></html>').encode()
    identity = dict(model=MODEL, model_sha256=digest(definition), catalogue_hash=json.loads(catalogue)['sha256'],
                    catalogue_file_sha256=digest(catalogue), module_sha256=digest(module), wasm_sha256=digest(wasm),
                    approval_sha256=digest(approval_bytes), review_sha256=digest(review_bytes), review_html_sha256=digest(review_html),
                    qualification_sha256=digest(qualification_bytes), build_review_sha256=digest(accepted_bytes), interface_review_sha256=digest(interface_review_bytes),
                    component_sha256={name: digest(data) for name, data in components.items()},
                    release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    files = {'engine-maxwell/'+name: data for name, data in {
        'maxwell.mjs': module, 'maxwell.wasm': wasm, 'models.json': catalogue,
        MODEL+'.json': definition, 'approval.json': approval_bytes, 'review.json': review_bytes,
        'review.html': review_html, 'qualification.json': qualification_bytes,
        'build-review.json': accepted_bytes, 'interface-review.json': interface_review_bytes, 'source-manifest.json': encoded(before), 'identity.json': encoded(identity)}.items()}
    files.update(components)
    # Keep inputs captured above: hashes refer to the exact copied bytes, not a second read.
    if source_manifest() != before or (ROOT/DEFINITION).read_bytes() != definition:
        raise ValueError('Maxwell source changed while packaging')
    destination.mkdir(parents=True, exist_ok=True)
    engine = destination/'engine-maxwell'
    if engine.exists():
        shutil.rmtree(engine)
    for name, data in files.items():
        path = destination/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (engine/'package-manifest.json').write_bytes(encoded({'kind': 'maxwell-main-atlas-1', 'files': {name: digest(data) for name, data in sorted(files.items())}}))
    return identity


if __name__ == '__main__':
    bundle(*sys.argv[1:])
