"""Bundle exact agent-approved J2 law and a dedicated common-engine laboratory."""
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.agent_review import approval_entry,validate_review
MODEL='j2-linear-isotropic-hardening-be'
MODEL_SHA256='a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b'
APPROVAL='docs/admission/j2-approved-v2/approval.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bundle(dest,build):
    dest,build=Path(dest),Path(build)
    approval=json.loads((ROOT/APPROVAL).read_text())
    review_path=ROOT/approval['review']['path']
    review=validate_review(review_path,for_approval=True)
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    if [entry for entry in registry if entry['model_id']==MODEL]!=[approval] or approval!=approval_entry(review_path):
        raise ValueError('J2 exact approval/registry/review mismatch')
    model=ROOT/approval['definition']['path']
    if approval['definition']['sha256']!=MODEL_SHA256 or sha(model)!=MODEL_SHA256 or review['model']['id']!=MODEL:
        raise ValueError('J2 approved model identity changed')
    if sha(review_path)!=approval['review']['sha256']:
        raise ValueError('J2 exact accepted review changed')
    # validate_review verifies supporting-file receipts against exact originals or explicit immutable archives.
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,[model]);expected=(Path(tmp)/'models.json').read_bytes()
    catalogue=build/'generated/models.json'
    if not catalogue.is_file() or catalogue.read_bytes()!=expected:
        raise ValueError('Stale J2 generated catalogue: rebuild dedicated target')
    # Read all build inputs before creating a partial package on missing-artifact failure.
    for name in ('j2.js','j2.wasm'):
        if not (build/name).is_file():raise ValueError('Missing dedicated J2 engine artifact: '+name)
    engine=dest/'engine-j2';engine.mkdir(parents=True,exist_ok=True)
    for name in ('j2.js','j2.wasm'):shutil.copyfile(build/name,engine/name)
    shutil.copyfile(catalogue,engine/'models.json')
    shutil.copyfile(model,engine/(MODEL+'.json'))
    shutil.copyfile(ROOT/APPROVAL,dest/'j2-approval.json')
    shutil.copyfile(review_path,dest/'j2-agent-review.json')
    for name in ('j2.html','j2-contract.mjs'):shutil.copyfile(ROOT/'web'/name,dest/name)
    review_text=(ROOT/'docs/reviews/j2-scientific-v2/README.md').read_text()
    (dest/'j2-review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>J2 independent scientific review</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>J2 independent scientific review v2</h1><p><a href="j2.html">J2 laboratory</a> · <a href="j2-agent-review.json">Hash-bound accepted checklist</a> · <a href="j2-approval.json">Bounded approval</a></p><pre>'+html.escape(review_text)+'</pre></html>')
    delivery_text=(ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/PUBLIC_DELIVERY.md').read_text()
    delivery_text+='\n\n'+(ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/README.md').read_text()
    delivery_text+='\n\n'+(ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/integration-addendum/README.md').read_text()
    (dest/'j2-delivery.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>J2 interface qualification</title><style>body{max-width:85ch;margin:2rem auto;padding:1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>J2 interface qualification</h1><p><a href="j2.html">J2 laboratory</a> · <a href="j2-review.html">Historical law review</a></p><pre>'+html.escape(delivery_text)+'</pre></html>')
    identity=dict(model=MODEL,model_sha256=MODEL_SHA256,catalogue_hash=json.loads(expected)['sha256'],catalogue_sha256=sha(engine/'models.json'),module_sha256=sha(engine/'j2.js'),wasm_sha256=sha(engine/'j2.wasm'),approval_sha256=sha(dest/'j2-approval.json'),review_sha256=sha(dest/'j2-agent-review.json'))
    (engine/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    root_names={'j2-delivery.html','j2.html','j2-contract.mjs','j2-review.html','j2-approval.json','j2-agent-review.json'}
    manifest={str(p.relative_to(dest)):sha(p) for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='package-manifest.json' and (p.parent==engine or (p.parent==dest and p.name in root_names))}
    (engine/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return identity
if __name__=='__main__':bundle(*sys.argv[1:])
