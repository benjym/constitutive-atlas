"""Package the approved, independently qualified timed law beside the strain-path lab."""
import hashlib,html,json,shutil,sys,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
MODEL='power-creep-itasca900-both-active-ode'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bundle(dest,build):
    dest=Path(dest);build=Path(build)
    approval=json.loads((ROOT/'docs/admission/power-creep-approved-v1/approval.json').read_text())
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    assert approval in registry and approval['status']=='approved' and approval['deployment_authorized']
    assert sha(ROOT/approval['definition']['path'])==approval['definition']['sha256']
    for item in approval['supporting_files']:assert sha(ROOT/item['path'])==item['sha256'],item['path']
    engine=dest/'engine';engine.mkdir(parents=True,exist_ok=True)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,sorted((ROOT/'models/research/power-creep').glob('*.json')))
        expected=(Path(tmp)/'models.json').read_bytes()
    catalogue=build/'power-creep-generated/models.json'
    if catalogue.read_bytes()!=expected:raise ValueError('Stale power-creep catalogue: rebuild dedicated target')
    for name in ['power-creep.js','power-creep.wasm']:shutil.copyfile(build/name,engine/name)
    shutil.copyfile(catalogue,engine/'models.json')
    revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    identity={'release_revision':revision,'model':MODEL,'catalogue_hash':json.loads(expected)['sha256'],'model_sha256':approval['definition']['sha256'],'module_sha256':sha(engine/'power-creep.js'),'wasm_sha256':sha(engine/'power-creep.wasm')}
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    shutil.copyfile(ROOT/'web/power-creep.html',dest/'power-creep.html')
    shutil.copyfile(ROOT/'docs/admission/power-creep-approved-v1/approval.json',dest/'power-creep-approval.json')
    from atlas.agent_review import validate_review
    record=ROOT/'catalogue/agent-reviews/power-creep-agent-v2.json'
    validate_review(record,for_approval=True)
    shutil.copyfile(record,dest/'power-creep-agent-review.json')
    for name in ['power-creep-contract.mjs','recorded.mjs','numerics.mjs','loading.mjs']:
        shutil.copyfile(ROOT/'web'/name,dest/name)
    review=(ROOT/'docs/ingestion/power-creep-itasca900/review-v2/README.md').read_text()
    (dest/'power-creep-review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Power creep review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>Power creep review and scope</h1><a href="power-creep.html">Physical-time laboratory</a><pre>'+html.escape(review)+'</pre></html>')
    shutil.copyfile(ROOT/approval['definition']['path'],engine/(MODEL+'.json'))

    names=['power-creep.html','power-creep-contract.mjs','recorded.mjs','numerics.mjs','loading.mjs','power-creep-review.html','power-creep-agent-review.json','power-creep-approval.json','engine/identity.json','engine/models.json','engine/power-creep.js','engine/power-creep.wasm','engine/'+MODEL+'.json']
    (dest/'power-creep-package.json').write_text(json.dumps({'kind':'power-creep-public-package-v2','revision':revision,'files':{name:sha(dest/name) for name in names}},indent=2)+'\n')
