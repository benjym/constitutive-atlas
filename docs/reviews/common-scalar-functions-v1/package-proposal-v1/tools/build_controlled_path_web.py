"""Package the approved controlled-path engine inside the ordinary atlas."""
import hashlib
import html
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.agent_review import approval_entry, validate_review
from atlas.compiler import generate

MODEL = 'norsand-jefferies-1993-active-axial'
COMPONENTS = ('path-engine.mjs', 'path-worker.mjs', 'path-laboratory.mjs',
              'laboratory-controller-router.mjs')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bundle(destination, build):
    destination, build = Path(destination), Path(build)
    approvals = json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    matches = [a for a in approvals if a['model_id'] == MODEL]
    if len(matches) != 1:
        raise ValueError('Exact controlled-path approval is missing or ambiguous')
    approval = matches[0]
    review_path = ROOT/approval['review']['path']
    review = validate_review(review_path, for_approval=True)
    if approval != approval_entry(review_path) or review['model']['id'] != MODEL:
        raise ValueError('Controlled-path registry/reviewer disagreement')
    definition = ROOT/approval['definition']['path']
    if sha(definition) != approval['definition']['sha256']:
        raise ValueError('Controlled-path approved definition changed')
    for pin in approval['supporting_files']:
        if sha(ROOT/pin['path']) != pin['sha256']:
            raise ValueError('Controlled-path approval evidence changed: '+pin['path'])
    example_path = ROOT/'catalogue/path-examples/norsand-1993-loose-constant-cell.json'
    example = json.loads(example_path.read_text())
    if example['model'] != MODEL or example['definition_sha256'] != sha(definition):
        raise ValueError('Controlled-path example definition differs')
    # This qualified generic engine also contains two analytical fixtures.
    # They remain auxiliary test definitions, never atlas scientific admissions.
    paths = [definition, ROOT/'tests/fixtures/controlled-path/synthetic-curved.json',
             ROOT/'tests/fixtures/controlled-path/synthetic-model.json']
    with tempfile.TemporaryDirectory() as temporary:
        generate(temporary, paths)
        expected = (Path(temporary)/'path_catalogue.json').read_bytes()
        for name in ('path_catalogue.json', 'path_models.hpp', 'path_api.cpp'):
            if (build/'generated'/name).read_bytes() != (Path(temporary)/name).read_bytes():
                raise ValueError('Controlled-path generated source is stale: '+name)
    current_receipt = build/'controlled-path-qualification.json'
    if current_receipt.is_file():
        qualification_path = current_receipt
        qualification = json.loads(current_receipt.read_text())
        binding = qualification.get('binding', {})
        sources = binding.get('sources', {})
        required = {p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/include/atlas').glob('*.hpp')}
        required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/scalar-functions').rglob('*') if p.is_file())
        required.update(('cmake/controlled-path/CMakeLists.txt', 'cmake/AtlasScalarFunctions.cmake',
                         'cpp/controlled_path.cpp', 'models/research/norsand/norsand-jefferies-1993-active-axial.json',
                         'tests/fixtures/controlled-path/synthetic-curved.json', 'tests/fixtures/controlled-path/synthetic-model.json'))
        if set(sources) != required or any(sha(ROOT/name) != digest for name, digest in sources.items()):
            raise ValueError('Controlled-path qualified source closure changed')
        artifacts = {name:sha(build/name) for name in ('atlas_path_capability.mjs', 'atlas_path_capability.wasm')}
        generated = {name:sha(build/'generated'/name) for name in ('path_catalogue.json','path_models.hpp','path_api.cpp')}
        gates = {'native_requests':58, 'wasm_requests':58, 'native_successes':40, 'native_rejections':18,
                 'wasm_successes':40, 'wasm_rejections':18, 'source_analytical':True, 'parity':True}
        if qualification.get('schema_version') != 'controlled-path-qualified-build-1' or qualification.get('model') != MODEL or qualification.get('status') != 'passed' or binding.get('artifacts') != artifacts or binding.get('generated') != generated or qualification.get('gates') != gates or not qualification.get('implementation_run'):
            raise ValueError('Controlled-path qualification incomplete or stale')
        reviewer = qualification.get('independent_review', {})
        relative = Path(reviewer.get('path',''))
        review_file = (build/relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not review_file.is_relative_to(build.resolve()) or not review_file.is_file():
            raise ValueError('Unsafe controlled-path build review')
        accepted = json.loads(review_file.read_text())
        if sha(review_file) != reviewer.get('sha256') or accepted.get('status') != 'accepted' or accepted.get('binding') != binding or accepted.get('gates') != gates or not accepted.get('reviewer_run') or accepted['reviewer_run'] == qualification['implementation_run']:
            raise ValueError('Controlled-path independent build review missing or changed')
    else:
        source_freeze = json.loads((ROOT/'docs/ingestion/norsand-1993/shared-integration-v1/target-source-freeze-v2.json').read_text())
        for name, digest in source_freeze['files'].items():
            if name.startswith('cpp/include/atlas/') or name == 'cmake/controlled-path/CMakeLists.txt':
                if sha(ROOT/name) != digest:
                    raise ValueError('Controlled-path compiled dependency changed: '+name)
        qualification_path = ROOT/'docs/ingestion/norsand-1993/shared-integration-v1/target-qualification-v2.json'
        qualification = json.loads(qualification_path.read_text())
        if qualification['result'] != 'PASS' or qualification['native_count'] != 58 or qualification['wasm_count'] != 58:
            raise ValueError('Controlled-path target qualification is incomplete')
        prefix = 'docs/ingestion/norsand-1993/shared-integration-v1/wasm-v2/'
        for name in ('atlas_path_capability.mjs', 'atlas_path_capability.wasm'):
            if sha(build/name) != qualification['artifacts'][prefix+name]:
                raise ValueError('Controlled-path engine differs from qualified artifact: '+name)
    engine = destination/'engine-path'
    if engine.is_symlink():
        raise ValueError('Controlled-path package destination is a symlink')
    if engine.exists():
        shutil.rmtree(engine)
    engine.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(build/'atlas_path_capability.mjs', engine/'engine.mjs')
    shutil.copyfile(build/'atlas_path_capability.wasm', engine/'engine.wasm')
    (engine/'catalogue.json').write_bytes(expected)
    shutil.copyfile(definition, engine/'model.json')
    shutil.copyfile(example_path, engine/'example.json')
    shutil.copyfile(review_path, engine/'review.json')
    (engine/'approval.json').write_text(json.dumps(approval, indent=2)+'\n')
    shutil.copyfile(qualification_path, engine/'qualification.json')
    shutil.copyfile(ROOT/'docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json', engine/'source-receipt.json')
    report = (ROOT/'docs/ingestion/norsand-1993/approval-v1/REPORT.md').read_text()
    (engine/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>NorSand independent review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>NorSand 1993 independent scientific review</h1><p><a href="../index.html#laboratory?model='+MODEL+'">Main atlas laboratory</a> · <a href="review.json">Checklist</a> · <a href="approval.json">Approval and limitations</a></p><pre>'+html.escape(report)+'</pre></html>')
    for name in COMPONENTS:
        shutil.copyfile(ROOT/'web'/name, destination/name)
    identity = {'profile':'controlled-path-ode-v1', 'model':MODEL,
                'definition_sha256':sha(definition),
                'files':{p.name:sha(p) for p in sorted(engine.iterdir()) if p.name not in ('identity.json','package-manifest.json') and p.is_file()},
                'components':{name:sha(destination/name) for name in COMPONENTS},
                'qualification_scope':'Exact accepted Python/native C ABI/Node-Wasm scope; packaged/actual-browser qualification is separately recorded.'}
    (engine/'identity.json').write_text(json.dumps(identity, indent=2)+'\n')
    names = [*COMPONENTS, *('engine-path/'+name for name in identity['files']), 'engine-path/identity.json']
    manifest = {'kind':'controlled-path-main-atlas-v1', 'model':MODEL,
                'auxiliary_fixtures':[p.stem for p in paths[1:]],
                'files':{name:sha(destination/name) for name in sorted(names)}}
    (engine/'package-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    bundle(*sys.argv[1:])
