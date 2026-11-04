"""Package the approved Kelvin–Voigt engine and embedded general-atlas laboratory; no page."""
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.agent_review import validate_review
MODEL='kelvin-voigt-comsol63-deviatoric-zero-spin-ode'
COMPONENTS=('kelvin-voigt-laboratory.mjs','kelvin-voigt-contract.mjs','kelvin-voigt-worker.mjs','laboratory-controller-router.mjs')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bundle(dest,build):
    dest,build=Path(dest),Path(build)
    approval_path=ROOT/'docs/ingestion/kelvin-voigt-comsol63/approval-v1.json'
    approval=json.loads(approval_path.read_text())
    if approval not in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models'] or approval['status']!='approved' or approval['model_id']!=MODEL:raise ValueError('Kelvin–Voigt approved registry entry missing or changed')
    record=ROOT/approval['review']['path'];review=validate_review(record,for_approval=True)
    if sha(record)!=approval['review']['sha256'] or review['model']!=dict(id=MODEL,**approval['definition']):raise ValueError('Kelvin–Voigt exact review/model binding differs')
    for item in [approval['definition'],*approval['supporting_files']]:
        if sha(ROOT/item['path'])!=item['sha256']:raise ValueError('Changed Kelvin–Voigt scientific evidence: '+item['path'])
    definition=ROOT/approval['definition']['path']
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,[definition]);expected=(Path(tmp)/'models.json').read_bytes()
    catalogue=next((p for p in (build/'generated/models.json',build/'kelvin-voigt-generated/models.json') if p.is_file()),None)
    if catalogue is None or catalogue.read_bytes()!=expected:raise ValueError('Stale Kelvin–Voigt generated catalogue; rebuild exact dedicated target')
    engine=dest/'engine-kelvin-voigt';engine.mkdir(parents=True,exist_ok=True)
    module=next((p for p in (build/'kv.mjs',build/'kv.js') if p.is_file()),None)
    if module is None:raise ValueError('Kelvin–Voigt qualified Wasm module missing')
    shutil.copyfile(module,engine/'kv.mjs');shutil.copyfile(build/'kv.wasm',engine/'kv.wasm');(engine/'models.json').write_bytes(expected)
    shutil.copyfile(definition,engine/(MODEL+'.json'));shutil.copyfile(approval_path,engine/'approval.json');shutil.copyfile(record,engine/'review.json')
    source=(ROOT/'docs/ingestion/kelvin-voigt-comsol63/review-v1/README.md').read_text()
    (engine/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Kelvin–Voigt scientific review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>Kelvin–Voigt independent scientific review</h1><p><a href="../index.html#laboratory?model='+MODEL+'">General atlas laboratory</a> · <a href="review.json">Checklist</a> · <a href="approval.json">Approval and limitations</a></p><pre>'+html.escape(source)+'</pre></html>')
    for name in COMPONENTS:shutil.copyfile(ROOT/'web'/name,dest/name)
    identity=dict(model=MODEL,model_sha256=sha(definition),catalogue_hash=json.loads(expected)['sha256'],catalogue_file_sha256=sha(engine/'models.json'),module_sha256=sha(engine/'kv.mjs'),wasm_sha256=sha(engine/'kv.wasm'),approval_sha256=sha(engine/'approval.json'),review_sha256=sha(record),review_html_sha256=sha(engine/'review.html'),component_sha256={name:sha(dest/name) for name in COMPONENTS},source_sha256='cf019ac6a6900d3fd6af91023cd806530d500812b100086062a91bfb1723cfcf',release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    names=[*COMPONENTS,*('engine-kelvin-voigt/'+name for name in ('kv.mjs','kv.wasm','models.json',MODEL+'.json','approval.json','review.json','review.html','identity.json'))]
    (engine/'package-manifest.json').write_text(json.dumps(dict(kind='kelvin-voigt-general-atlas-laboratory-v1',files={name:sha(dest/name) for name in sorted(names)}),indent=2)+'\n')
if __name__=='__main__':bundle(*sys.argv[1:])
