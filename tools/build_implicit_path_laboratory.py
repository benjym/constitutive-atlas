"""Bundle the main-atlas implicit-path route with exact independent qualifications."""
from pathlib import Path
import hashlib
import html
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.agent_review import validate_review, approval_entry
from atlas.evidence import checked_receipt
from tools.generate_implicit_path import regenerate, MODEL_ID, INPUTS

DEFINITION = INPUTS[0]
PACKET = 'docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
INTERFACE = PACKET + 'independent-review/interface-review-receipt.json'
COMPONENTS = tuple('implicit-path-' + name + '.mjs' for name in ('contract', 'engine', 'runner', 'worker', 'laboratory'))
GATES = ('interpreter', 'helpers', 'native_triaxial', 'native_fixed', 'native_domain',
         'native_lifecycle', 'native_legacy', 'native_supplement', 'wasm_parity', 'wasm_chains', 'wasm_source')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def local_file(root, name):
    name = Path(name)
    path = (root/name).resolve()
    if name.is_absolute() or '..' in name.parts or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Unsafe or missing implicit-path artifact: ' + str(name))
    return path


def runtime_manifest():
    root = ROOT/'cpp/profiles/implicit-path-v1'
    paths = [root/'main.cpp', *sorted((root/'include').rglob('*.hpp'))]
    files = {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in paths}
    return {'files': files, 'sha256': digest(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())}


def passed_gates(value):
    return isinstance(value, dict) and set(value) == set(GATES) and all(v is True for v in value.values())


def bundle(destination, build):
    destination, build = Path(destination), Path(build)
    before = runtime_manifest()
    registry = json.loads((ROOT/'catalogue/approved-models.json').read_bytes())
    entries = [m for m in registry['models'] if m.get('model_id') == MODEL_ID and m.get('status') == 'approved']
    if len(entries) != 1:
        raise ValueError('Exactly one independently approved Lade model is required')
    approval = entries[0]
    approval_bytes = encoded(approval)
    review_path = local_file(ROOT, approval['review']['path'])
    review_bytes = review_path.read_bytes()
    review = validate_review(review_path, root=ROOT, for_approval=True)
    if approval != approval_entry(review_path, root=ROOT):
        raise ValueError('Implicit-path approval differs from canonical independent review')
    definition = (ROOT/DEFINITION).read_bytes()
    binding_model = {'path': DEFINITION, 'sha256': digest(definition)}
    if approval['definition'] != binding_model or review['model'] != dict(id=MODEL_ID, **binding_model) or digest(review_bytes) != approval['review']['sha256']:
        raise ValueError('Implicit-path definition/review identity changed')
    for item in approval.get('supporting_files', []):
        checked_receipt(ROOT, approval['review']['path'], item['path'], item['sha256'])
    with tempfile.TemporaryDirectory() as temporary:
        generation = regenerate(temporary)
        catalogue = (Path(temporary)/'models.json').read_bytes()
    if local_file(build, 'generated/models.json').read_bytes() != catalogue:
        raise ValueError('Stale implicit-path compiled catalogue')
    module = local_file(build, 'lade-domain.mjs').read_bytes()
    wasm = local_file(build, 'lade-domain.wasm').read_bytes()
    qualification_bytes = local_file(build, 'implicit-path-qualification.json').read_bytes()
    qualification = json.loads(qualification_bytes)
    binding = dict(model_sha256=digest(definition), runtime_sha256=before['sha256'],
                   generated=generation['outputs'], ordered_inputs=generation['ordered_inputs'],
                   module_sha256=digest(module), wasm_sha256=digest(wasm))
    if qualification.get('schema_version') != 'implicit-path-qualified-build-1' or qualification.get('model') != MODEL_ID or qualification.get('status') != 'passed' or qualification.get('binding') != binding or not passed_gates(qualification.get('gates')) or not qualification.get('implementation_run'):
        raise ValueError('Missing, stale or failed implicit-path numerical qualification')
    reviewer = qualification.get('independent_review', {})
    accepted_bytes = local_file(build, reviewer.get('path', '')).read_bytes()
    accepted = json.loads(accepted_bytes)
    if digest(accepted_bytes) != reviewer.get('sha256') or accepted.get('status') != 'accepted' or accepted.get('binding') != binding or not passed_gates(accepted.get('gates')) or not accepted.get('reviewer_run') or accepted['reviewer_run'] == qualification['implementation_run']:
        raise ValueError('Independent exact implicit-path qualification missing or changed')
    components = {name: (ROOT/'web'/name).read_bytes() for name in COMPONENTS}
    interface_bytes = (ROOT/INTERFACE).read_bytes()
    interface = json.loads(interface_bytes)
    if interface.get('status') != 'accepted' or interface.get('blocking_findings') != [] or not interface.get('reviewer_run'):
        raise ValueError('Implicit-path interface review is incomplete')
    pins = interface.get('files', {})
    for name, data in components.items():
        if pins.get('web/'+name) != digest(data):
            raise ValueError('Implicit-path interface changed: '+name)
    for name in ['tools/generate_implicit_path.py', 'tools/build_implicit_path_laboratory.py', 'cmake/implicit-path-v1/CMakeLists.txt', PACKET+'check_interface.mjs']:
        if pins.get(name) != digest((ROOT/name).read_bytes()):
            raise ValueError('Implicit-path integration source changed: '+name)
    for name, expected in pins.items():
        if digest(local_file(ROOT, name).read_bytes()) != expected:
            raise ValueError('Implicit-path interface supporting evidence changed: '+name)
    source = (ROOT/PACKET/'independent-review/MODEL_REVIEW.md').read_text()
    review_html = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Lade–Duncan 1975 independent review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>Lade–Duncan 1975 independent agent review</h1><p><a href="../index.html#laboratory?model='+MODEL_ID+'">Main atlas laboratory</a> · <a href="review.json">Checklist</a> · <a href="approval.json">Scope</a></p><pre>'+html.escape(source)+'</pre></html>').encode()
    identity = dict(profile='implicit-path-v1', model=MODEL_ID, model_sha256=digest(definition), public_models=[MODEL_ID],
                    catalogue_hash=json.loads(catalogue)['sha256'], catalogue_file_sha256=digest(catalogue),
                    module_sha256=digest(module), wasm_sha256=digest(wasm), approval_sha256=digest(approval_bytes),
                    review_sha256=digest(review_bytes), review_html_sha256=digest(review_html),
                    qualification_sha256=digest(qualification_bytes), build_review_sha256=digest(accepted_bytes),
                    runtime_sha256=before['sha256'], interface_review_sha256=digest(interface_bytes),
                    component_sha256={name:digest(data) for name,data in components.items()},
                    release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    assets = {'lade-domain.mjs':module, 'lade-domain.wasm':wasm, 'models.json':catalogue, MODEL_ID+'.json':definition,
              'approval.json':approval_bytes, 'review.json':review_bytes, 'review.html':review_html,
              'qualification.json':qualification_bytes, 'build-review.json':accepted_bytes,
              'interface-review.json':interface_bytes, 'source-manifest.json':encoded(before),
              'identity.json':encoded(identity)}
    files = {'engine-implicit-path/'+name:data for name,data in assets.items()}
    files.update(components)
    if runtime_manifest() != before or (ROOT/DEFINITION).read_bytes() != definition:
        raise ValueError('Implicit-path inputs changed while packaging')
    destination.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        out=destination/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    (destination/'engine-implicit-path/package-manifest.json').write_bytes(encoded({'kind':'implicit-path-main-atlas-1','files':{name:digest(data) for name,data in sorted(files.items())}}))
    return identity


if __name__ == '__main__':
    bundle(*sys.argv[1:])
