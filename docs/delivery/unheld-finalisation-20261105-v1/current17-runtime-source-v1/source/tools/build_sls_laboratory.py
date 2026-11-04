"""Package the approved SLS engine and embedded general-atlas laboratory; no page."""
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
MODEL='sls-comsol63-deviatoric-zero-spin-ode'
COMPONENTS=('sls-laboratory.mjs','sls-atlas-contract.mjs','sls-atlas-worker.mjs','laboratory-controller-router.mjs')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bundle(dest,build):
    dest,build=Path(dest),Path(build)
    approval_path=ROOT/'docs/admission/sls-comsol63-approved-v1/approval.json'
    approval=json.loads(approval_path.read_text())
    if approval not in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models'] or approval['status']!='approved' or approval['model_id']!=MODEL:raise ValueError('SLS approved registry entry missing or changed')
    record=ROOT/approval['review']['path'];review=validate_review(record,for_approval=True)
    if sha(record)!=approval['review']['sha256'] or review['model']!=dict(id=MODEL,**approval['definition']):raise ValueError('SLS exact review/model binding differs')
    for item in [approval['definition'],*approval['supporting_files']]:
        if sha(ROOT/item['path'])!=item['sha256']:raise ValueError('Changed SLS scientific evidence: '+item['path'])
    definition=ROOT/approval['definition']['path']
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,[definition]);expected=(Path(tmp)/'models.json').read_bytes()
    catalogue=next((p for p in (build/'generated/models.json',build/'sls-generated/models.json') if p.is_file()),None)
    if catalogue is None or catalogue.read_bytes()!=expected:raise ValueError('Stale SLS generated catalogue; rebuild exact dedicated target')
    engine=dest/'engine-sls';engine.mkdir(parents=True,exist_ok=True)
    module=next((p for p in (build/'sls.mjs',build/'sls.js') if p.is_file()),None)
    if module is None:raise ValueError('SLS qualified Wasm module missing')
    shutil.copyfile(module,engine/'sls.mjs');shutil.copyfile(build/'sls.wasm',engine/'sls.wasm');(engine/'models.json').write_bytes(expected)
    shutil.copyfile(definition,engine/(MODEL+'.json'));shutil.copyfile(approval_path,engine/'approval.json');shutil.copyfile(record,engine/'review.json')
    source=(ROOT/'docs/reviews/sls-comsol63-scientific-v1/README.md').read_text()
    (engine/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SLS scientific review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;font:inherit}</style><h1>SLS independent scientific review</h1><p><a href="../index.html#laboratory?model='+MODEL+'">General atlas laboratory</a> · <a href="review.json">Checklist</a> · <a href="approval.json">Approval and limitations</a></p><pre>'+html.escape(source)+'</pre></html>')
    for name in COMPONENTS:shutil.copyfile(ROOT/'web'/name,dest/name)
    identity=dict(model=MODEL,model_sha256=sha(definition),catalogue_hash=json.loads(expected)['sha256'],catalogue_file_sha256=sha(engine/'models.json'),module_sha256=sha(engine/'sls.mjs'),wasm_sha256=sha(engine/'sls.wasm'),approval_sha256=sha(engine/'approval.json'),review_sha256=sha(record),review_html_sha256=sha(engine/'review.html'),component_sha256={name:sha(dest/name) for name in COMPONENTS},source_sha256='cf019ac6a6900d3fd6af91023cd806530d500812b100086062a91bfb1723cfcf',release_revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    names=[*COMPONENTS,*('engine-sls/'+name for name in ('sls.mjs','sls.wasm','models.json',MODEL+'.json','approval.json','review.json','review.html','identity.json'))]
    (engine/'package-manifest.json').write_text(json.dumps(dict(kind='sls-general-atlas-laboratory-v1',files={name:sha(dest/name) for name in sorted(names)}),indent=2)+'\n')
if __name__=='__main__':bundle(*sys.argv[1:])
