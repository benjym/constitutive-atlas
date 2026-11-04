"""Bundle approved imposed-field physical-time models into the normal main atlas."""
import hashlib,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.controlled_time_compiler import generate
from atlas.agent_review import validate_review
COMPONENTS=('controlled-time-engine.mjs','controlled-time-worker.mjs','controlled-time-laboratory.mjs')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_pin(pin):
    p=Path(pin['path'])
    if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe source binding')
    if sha(ROOT/p)!=pin['sha256']:raise ValueError('Changed controlled-time source/evidence: '+str(p))
def bundle(destination,build):
    destination,build=Path(destination),Path(build)
    # The qualification receipt is produced only after actual native/Wasm qualification
    # and separate review. Its exact bytes must also be pinned by the model approval.
    receipt_path=build/'public-qualification.json'
    receipt=json.loads(receipt_path.read_text())
    if receipt.get('kind')!='controlled-time-public-engine-qualification-v1' or receipt.get('status')!='accepted':raise ValueError('Actual accepted controlled-time qualification required')
    for f in receipt['source_files']:source_pin(f)
    for name in ('atlas_controlled_time_capability.mjs','atlas_controlled_time_capability.wasm'):
        if sha(build/name)!=receipt['artifacts'][name]:raise ValueError('Changed qualified engine artifact: '+name)
    model_id=receipt['model_id'];registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    candidates=[a for a in registry if a['model_id']==model_id and a['status']=='approved' and a['definition']['sha256']==receipt['definition_sha256']]
    if len(candidates)!=1:raise ValueError('Exact approved controlled-time model missing/ambiguous')
    approval=candidates[0];source_pin(approval['definition']);source_pin(approval['review'])
    for p in approval['supporting_files']:source_pin(p)
    record=ROOT/approval['review']['path'];review=validate_review(record,for_approval=True)
    if review['model']!=dict(id=model_id,**approval['definition']):raise ValueError('Review/definition mismatch')
    expected_receipt=next((p for p in approval['supporting_files'] if p['path']==receipt['root_receipt_path']),None)
    if expected_receipt is None:raise ValueError('Qualification receipt not bound by exact approval')
    # This is a durable root receipt copied alongside the qualified build, not a
    # mutable local artifact path in public scientific evidence.
    source_pin(expected_receipt)
    if (ROOT/expected_receipt['path']).read_bytes()!=receipt_path.read_bytes():raise ValueError('Qualification receipt differs from approval evidence')
    if expected_receipt not in approval['supporting_files']:raise ValueError('Qualification not bound by exact approval')
    model=ROOT/approval['definition']['path'];examples=ROOT/receipt['examples']['path'];source_pin(receipt['examples']);source_pin(receipt['public_results'])
    if receipt['public_results'] not in approval['supporting_files']:raise ValueError('Public replay results not bound by approval')
    if receipt['examples'] not in approval['supporting_files']:raise ValueError('Public histories not bound by approval')
    with tempfile.TemporaryDirectory(prefix='atlas-controlled-time-catalogue-') as td:
        generate(td,[model])
        for name in ('controlled_time_models.hpp','controlled_time_api.cpp','controlled_time_catalogue.json'):
            if (Path(td)/name).read_bytes()!=(build/'generated'/name).read_bytes():raise ValueError('Controlled-time generated source/catalogue stale: '+name)
        catalogue=json.loads((Path(td)/'controlled_time_catalogue.json').read_text())
    engine=destination/'engine-controlled-time';engine.mkdir(parents=True,exist_ok=True)
    allowed={'model.json','examples.json','expected-results.json','review.json','catalogue.json','engine.mjs','engine.wasm','qualification.json','approval.json','identity.json','package-manifest.json'}
    if any(p.name not in allowed or not p.is_file() for p in engine.iterdir()):raise ValueError('Unexpected retained controlled-time package assets; use a fresh output')
    for source,name in [(model,'model.json'),(examples,'examples.json'),(ROOT/receipt['public_results']['path'],'expected-results.json'),(record,'review.json'),(build/'generated/controlled_time_catalogue.json','catalogue.json'),(build/'atlas_controlled_time_capability.mjs','engine.mjs'),(build/'atlas_controlled_time_capability.wasm','engine.wasm'),(receipt_path,'qualification.json')]:shutil.copyfile(source,engine/name)
    (engine/'approval.json').write_text(json.dumps(approval,indent=2)+'\n')
    for n in COMPONENTS:shutil.copyfile(ROOT/'web'/n,destination/n)
    identity=dict(profile='controlled-time-ode-v1',model=model_id,model_sha256=catalogue['models'][0]['model_sha256'],definition_file_sha256=sha(model),catalogue_sha256=catalogue['catalogue_sha256'],files={p.name:sha(p) for p in sorted(engine.iterdir()) if p.is_file() and p.name not in ('identity.json','package-manifest.json')},components={n:sha(destination/n) for n in COMPONENTS})
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    names=[*COMPONENTS,*('engine-controlled-time/'+n for n in [*identity['files'],'identity.json'])]
    (engine/'package-manifest.json').write_text(json.dumps(dict(kind='controlled-time-mainatlas-package-v1',files={n:sha(destination/n) for n in names}),indent=2)+'\n')
if __name__=='__main__':bundle(*sys.argv[1:])
