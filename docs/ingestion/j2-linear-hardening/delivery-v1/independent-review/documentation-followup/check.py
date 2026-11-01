#!/usr/bin/env python3
"""Saved-only verification of documentation embedding; executes no engine/builder."""
import hashlib,html,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
REVIEW=HERE.parent;BASE=REVIEW.parent;ROOT=REVIEW.parents[4]
sys.path.insert(0,str(REVIEW))
from check_saved_numerics import run as numerics

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(site):
    freeze=json.loads((BASE/'interface-freeze-v2.json').read_text());final=json.loads((BASE/'final-integration-freeze.json').read_text())
    retained=json.loads((REVIEW/'integration-addendum/source-receipts.json').read_text())
    for item in retained['files']:
        assert final['files'][item['path']]==item['stage_sha256']
        assert sha(REVIEW/'integration-addendum/stage'/item['path'])==item['stage_sha256']
    old=(HERE/'builder-before.py').read_bytes();new=(HERE/'builder-after.py').read_bytes()
    assert hashlib.sha256(old).hexdigest()==freeze['files']['tools/build_j2_web.py']
    assert hashlib.sha256(new).hexdigest()==final['files']['tools/build_j2_web.py']
    assert (ROOT/'tools/build_j2_web.py').read_bytes()==new
    lines=new.decode().splitlines(True)
    additions=[line for line in lines if line.startswith("    delivery_text+='\\n\\n'+")]
    assert len(additions)==2
    assert ''.join(line for line in lines if line not in additions).encode()==old
    expected=["independent-review/README.md","independent-review/integration-addendum/README.md"]
    assert all(x in line for x,line in zip(expected,additions))
    manifest=json.loads((BASE/'copied-package-manifest.json').read_text())
    for p,h in manifest.items():
        assert sha(pathlib.Path('/private/tmp/atlas-j2-delivery-v1/site')/p)==h,p
        if p!='j2-delivery.html':assert sha(site/p)==h,p
    documents=[BASE/'PUBLIC_DELIVERY.md',REVIEW/'README.md',REVIEW/'integration-addendum/README.md']
    page=(site/'j2-delivery.html').read_text();actual=html.unescape(page.split('<pre>',1)[1].split('</pre>',1)[0])
    assert actual=='\n\n'.join(p.read_text() for p in documents)
    assert numerics()['passed']
    return dict(passed=True,verdict='accept exact documentation-only embedding',builder_before_sha256=hashlib.sha256(old).hexdigest(),builder_after_sha256=hashlib.sha256(new).hexdigest(),added_lines=2,public_document_sha256=sha(site/'j2-delivery.html'),actual_public_review_text_exact=True,unchanged_package_assets=10,original_recorded_package_assets=11,saved_numerics_passed=True,compiled_calls_by_reviewer=0,limitations=['Historical navigation18b9be frozen pin remains unrecovered; exact scoped integration identity reviewed separately.','No remote CI/Pages/live verification claimed.'])
if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-j2-delivery-v1/publish-site')),indent=2))
