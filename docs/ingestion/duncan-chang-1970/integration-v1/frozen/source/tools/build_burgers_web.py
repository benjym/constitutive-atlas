"""Package exact Burgers timed engine assets for the main laboratory."""
import hashlib,json,shutil,sys,tempfile,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.agent_review import validate_review,approval_entry
MODEL='burgers-itasca900-dry-zero-spin-ode'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bundle(dest,build):
    dest,build=Path(dest),Path(build)
    record=ROOT/'catalogue/agent-reviews/burgers-agent-v2.json'
    review=validate_review(record,for_approval=True)
    approval=approval_entry(record)
    if approval not in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']:raise ValueError('Burgers agent approval not integrated')
    definition=ROOT/review['model']['path']
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,[definition]);expected=(Path(tmp)/'models.json').read_bytes()
    catalogue=next((p for p in [build/'generated/models.json',build/'burgers-generated/models.json'] if p.exists()),None)
    if catalogue is None or catalogue.read_bytes()!=expected:raise ValueError('Stale Burgers engine catalogue; rebuild exact target')
    engine=dest/'engine-burgers';engine.mkdir(parents=True,exist_ok=True)
    for name in ['burgers.mjs','burgers.wasm']:shutil.copyfile(build/name,engine/name)
    (engine/'models.json').write_bytes(expected)
    shutil.copyfile(definition,engine/(MODEL+'.json'));shutil.copyfile(record,engine/'review.json')
    (engine/'approval.json').write_text(json.dumps(approval,indent=2)+'\n')
    identity=dict(model=MODEL,model_sha256=sha(definition),catalogue_hash=json.loads(expected)['sha256'],catalogue_file_sha256=sha(engine/'models.json'),module_sha256=sha(engine/'burgers.mjs'),wasm_sha256=sha(engine/'burgers.wasm'),review_sha256=sha(record),approval_sha256=sha(engine/'approval.json'),release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    for name in ['timed-contract.mjs','timed-laboratory.mjs','timed-worker.mjs','recorded.mjs','numerics.mjs','loading.mjs']:shutil.copyfile(ROOT/'web'/name,dest/name)
    dossier=Path('docs/models/burgers-main-laboratory-v1.md');target=dest/dossier;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/dossier,target)
    from build_evidence import dossier_view
    target.with_name(target.name+'.html').write_bytes(dossier_view(dossier,(ROOT/dossier).read_bytes()))
    names=[str(p.relative_to(dest)) for p in engine.iterdir() if p.is_file() and p.name!='package.json']+['timed-contract.mjs','timed-laboratory.mjs','timed-worker.mjs']
    (engine/'package.json').write_text(json.dumps(dict(kind='burgers-main-laboratory-v1',files={n:sha(dest/n) for n in sorted(names)}),indent=2)+'\n')
if __name__=='__main__':bundle(*sys.argv[1:])
