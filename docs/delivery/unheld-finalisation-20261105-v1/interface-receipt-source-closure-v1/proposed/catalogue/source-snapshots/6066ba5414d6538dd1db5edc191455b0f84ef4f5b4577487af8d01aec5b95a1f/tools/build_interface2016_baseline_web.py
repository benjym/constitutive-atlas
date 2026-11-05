"""Guarded source-reconciled interface path package inside the ordinary atlas."""
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODEL = 'hvwe2016-reconciled-fixed-local'
NAMESPACE = 'material-point-interface2016'
PACKET = 'docs/ingestion/hypoplastic-interface-2016/'
EXAMPLE = PACKET+'implementation-v1/example.json'
BUILD_RECEIPT = PACKET+'execution-v1/build-receipt.json'
PACKAGE_CASES = PACKET+'execution-v1/package-cases.json'
COMPONENTS = ('path-engine.mjs', 'path-worker.mjs', 'interface2016-laboratory.mjs')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def receipt_artifact(receipt, extension):
    entries = [(name, digest) for name, digest in receipt['artifacts'].items() if name.endswith(extension)]
    if len(entries) != 1:
        raise ValueError('Expected exactly one reviewed '+extension+' engine artifact')
    return entries[0]


def bundle(destination, build):
    from atlas.agent_review import approval_entry, validate_review
    from atlas.compiler import generate
    from atlas.evidence import checked_receipt
    destination, build = Path(destination), Path(build)
    entries = [a for a in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models'] if a['model_id'] == MODEL]
    if len(entries) != 1:
        raise ValueError('Exact interface approval is missing or ambiguous')
    approval = entries[0]
    review_path = ROOT/approval['review']['path']
    review = validate_review(review_path, for_approval=True)
    if approval != approval_entry(review_path) or review['model']['id'] != MODEL:
        raise ValueError('Interface registry/reviewer disagreement')
    definition = ROOT/approval['definition']['path']
    if sha(definition) != approval['definition']['sha256']:
        raise ValueError('Approved interface definition changed')
    for pin in approval['supporting_files']:
        checked_receipt(ROOT, approval['review']['path'], pin['path'], pin['sha256'])
    pins = {p['path']:p['sha256'] for p in review['artifacts']}
    for name in [EXAMPLE, BUILD_RECEIPT, PACKAGE_CASES, PACKET+'execution-v1/qualification.json', PACKET+'execution-v1/build-review.json']:
        if pins.get(name) != sha(ROOT/name):
            raise ValueError('Interface package input must be hash-bound by independent review: '+name)
    example = json.loads((ROOT/EXAMPLE).read_text())
    if example['model'] != MODEL or example['definition_sha256'] != sha(definition):
        raise ValueError('Interface example definition differs')
    from qualify_controlled_path_refresh import validate_refresh
    from profile_source_compatibility_baseline import validate as compatible_source, copy_evidence
    compatibility = compatible_source(ROOT, build, 'interface2016')
    refresh = dict(qualification=compatibility['qualification'], qualification_bytes=compatibility['qualification_bytes'], review_bytes=compatibility['review_bytes']) if compatibility is not None else validate_refresh(build, MODEL)
    if refresh is not None:
        qualification = refresh['qualification']
        closure = compatibility['sources'] if compatibility is not None else qualification['binding']['source_closure']
        receipt = dict(status='passed', definition_sha256=sha(definition),
                       artifacts={name:digest for name,digest in qualification['binding']['artifacts'].items()
                                  if name.endswith(('.mjs', '.wasm'))},
                       source_closure=closure, refresh_qualification_sha256=sha(build/'refresh-qualification.json'))
        receipt['artifacts']['generated/path_catalogue.json'] = qualification['binding']['generated']['path_catalogue.json']
    else:
        receipt = json.loads((ROOT/BUILD_RECEIPT).read_text())
        if receipt.get('schema_version') != 'interface2016-qualified-build-v1' or receipt.get('status') != 'passed' or receipt.get('model') != MODEL or receipt.get('definition_sha256') != sha(definition) or not receipt.get('commands') or not receipt.get('toolchain'):
            raise ValueError('Incomplete interface qualified build receipt')
        closure = receipt.get('source_closure', {})
        required = {p.relative_to(ROOT).as_posix() for p in (ROOT/'atlas').rglob('*.py') if '__pycache__' not in p.parts}
        required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'schemas').rglob('*.json'))
        required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/include/atlas').rglob('*.hpp'))
        required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/scalar-functions').rglob('*') if p.is_file())
        required.update(['cmake/controlled-path/CMakeLists.txt', 'cmake/AtlasScalarFunctions.cmake', 'tools/generate_controlled_path.py', approval['definition']['path']])
        if not required.issubset(closure):
            raise ValueError('Interface qualified source closure omits current dependencies')
        for name,digest in closure.items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or sha(ROOT/path) != digest:
                raise ValueError('Interface qualified source closure changed: '+name)
        evidence = {}
        for key,filename in [('qualification','qualification.json'),('independent_review','build-review.json')]:
            pin = receipt.get(key,{})
            expected_path = PACKET+'execution-v1/'+filename
            if pin.get('path') != expected_path or pin.get('sha256') != sha(ROOT/expected_path):
                raise ValueError('Interface build evidence pin changed: '+key)
            evidence[key] = json.loads((ROOT/expected_path).read_text())
        qualification, accepted = evidence['qualification'], evidence['independent_review']
        binding = qualification.get('binding', {})
        if qualification.get('status') != 'passed' or binding.get('model_sha256') != sha(definition) or binding.get('artifacts') != receipt['artifacts'] or binding.get('source_closure') != closure or not isinstance(qualification.get('implementation_run'), str) or not qualification['implementation_run'].strip():
            raise ValueError('Interface qualification binding incomplete')
        if accepted.get('status') != 'accepted' or accepted.get('binding') != binding or not isinstance(accepted.get('reviewer_run'), str) or not accepted['reviewer_run'].strip() or accepted['reviewer_run'] == qualification['implementation_run']:
            raise ValueError('Interface independent build review missing or changed')
        for group in ['cases','results']:
            if not binding.get(group):
                raise ValueError('Interface qualification must bind concrete '+group)
            for name,digest in binding[group].items():
                path = Path(name)
                if path.is_absolute() or '..' in path.parts or sha(ROOT/path) != digest:
                    raise ValueError('Interface qualification '+group+' changed: '+name)
    with tempfile.TemporaryDirectory() as temporary:
        generate(temporary, [definition])
        expected = (Path(temporary)/'path_catalogue.json').read_bytes()
        for name in ['path_catalogue.json', 'path_models.hpp', 'path_api.cpp']:
            if (build/'generated'/name).read_bytes() != (Path(temporary)/name).read_bytes():
                raise ValueError('Stale interface generated source: '+name)
    sources = {}
    for extension, name in [('.mjs','engine.mjs'),('.wasm','engine.wasm')]:
        original, expected_digest = receipt_artifact(receipt, extension)
        source = build/Path(original).name
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected_digest:
            raise ValueError('Interface engine differs from reviewed executable: '+str(source))
        sources[name] = data
    generated_pins = ([qualification['binding']['generated']['path_catalogue.json']] if refresh is not None else
                      [digest for name,digest in receipt['artifacts'].items() if name.endswith('/generated/path_catalogue.json')])
    if generated_pins != [hashlib.sha256(expected).hexdigest()]:
        raise ValueError('Interface generated catalogue is not pinned by build receipt')
    namespace = destination/NAMESPACE
    if namespace.exists() and any(namespace.iterdir()):
        raise ValueError('Preserve prior interface package; use an empty destination namespace')
    engine = namespace/'engine-path'
    engine.mkdir(parents=True, exist_ok=True)
    for name,data in sources.items():
        (engine/name).write_bytes(data)
    (engine/'catalogue.json').write_bytes(expected)
    shutil.copyfile(definition, engine/'model.json')
    shutil.copyfile(ROOT/EXAMPLE, engine/'example.json')
    shutil.copyfile(review_path, engine/'review.json')
    (engine/'approval.json').write_text(json.dumps(approval, indent=2)+'\n')
    if refresh is None:
        shutil.copyfile(ROOT/BUILD_RECEIPT, engine/'build-receipt.json')
    else:
        (engine/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    shutil.copyfile(ROOT/PACKAGE_CASES, engine/'package-cases.json')
    if refresh is None:
        shutil.copyfile(ROOT/(PACKET+'execution-v1/qualification.json'), engine/'qualification.json')
        shutil.copyfile(ROOT/(PACKET+'execution-v1/build-review.json'), engine/'build-review.json')
    else:
        (engine/'qualification.json').write_bytes(refresh['qualification_bytes'])
        (engine/'build-review.json').write_bytes(refresh['review_bytes'])
    shutil.copyfile(ROOT/(PACKET+'source-v2/receipts.json'), engine/'source-receipt.json')
    model = json.loads(definition.read_text())
    report = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Fully rough interface sources and scope</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>Fully rough granular interface</h1><p><a href="../../index.html#laboratory?model='+MODEL+'">Main atlas laboratory</a> · <a href="model.json">Exact definition</a> · <a href="review.json">Independent checklist</a> · <a href="approval.json">Approval</a> · <a href="example.json">Complete starting example</a> · <a href="source-receipt.json">Source provenance</a></p><p>Source-reconciled fully rough HvWE2016 law with VW96 host closure; local effective Cauchy stress, fixed local axes and zero spin; no pore-pressure law. Prescribed normal compression strain and two source shear angles are dimensionless. A shear-angle rate gives half the engineering shear stretching. There is no finite-slip/thickness adapter, CNL/CNS controller, contact opening/recontact or finite-rotation transport.</p><p>The complete state is local normal stress, shared in-plane normal stress, two shear tractions and void ratio. Complete state and recovered Mandel stress are exported at every output. No experimental calibration or validation is claimed. Raw copyrighted papers and vendor code are not redistributed or executed.</p>'
    for title,text in [('Accepted scope',review['scope']),('Limitations','\n'.join(review['limitations'])),('Declarative equations',json.dumps(model.get('equations'),indent=2))]:
        report += '<h2>'+html.escape(title)+'</h2><pre>'+html.escape(text)+'</pre>'
    report += '<p><a href="https://doi.org/10.1007/s11440-016-0440-1">Stutz, Mašín and Wuttke2016</a> · <a href="https://www.geotechnics.ifg.uni-kiel.de/en/publications/2016-hanshenningstutz.pdf">Author thesis</a>. Scientific approval and actual browser delivery are separately assessed.</p></html>'
    (engine/'review.html').write_text(report)
    for name in COMPONENTS:
        shutil.copyfile(ROOT/'web'/name, namespace/name)
    for name in ['path-engine.mjs','interface2016-laboratory.mjs']:
        path = destination/name
        if path.exists() and sha(path) != sha(ROOT/'web'/name):
            raise ValueError('Root interface component conflicts with namespaced copy: '+name)
        shutil.copyfile(ROOT/'web'/name, path)
    if any(sha(ROOT/name) != digest for name,digest in closure.items()):
        raise ValueError('Interface qualified source changed during packaging')
    copy_evidence(compatibility, engine)
    identity = dict(profile='controlled-path-ode-v1', model=MODEL, definition_sha256=sha(definition),
                    files={p.name:sha(p) for p in sorted(engine.iterdir()) if p.is_file()},
                    components={name:sha(namespace/name) for name in COMPONENTS},
                    qualification_scope='Exact source-reconciled fixed-local interface law and independently accepted native/Wasm scope; actual browser delivery is separately qualified.')
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    names = [*(NAMESPACE+'/'+name for name in COMPONENTS), *(NAMESPACE+'/engine-path/'+name for name in identity['files']), NAMESPACE+'/engine-path/identity.json', 'path-engine.mjs', 'interface2016-laboratory.mjs']
    manifest = dict(kind='interface2016-main-atlas-v1',model=MODEL,files={name:sha(destination/name) for name in sorted(names)})
    (engine/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    bundle(*sys.argv[1:])
