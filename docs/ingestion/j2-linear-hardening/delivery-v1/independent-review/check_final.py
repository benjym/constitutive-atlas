#!/usr/bin/env python3
"""Independent saved-only final interface check; hashes bytes, never executes engine."""
import hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[4]; BASE=HERE.parent
sys.path.insert(0,str(HERE))
from check_saved_numerics import run as numerical

def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(site):
    n=numerical();assert n['passed']
    freeze=read(BASE/'interface-freeze-v2.json');assert freeze['package_compiled_calls_before_this_revision']==0
    source_mismatches=[]
    for p,h in freeze['files'].items():
        actual=digest(ROOT/p)
        if actual!=h:
            assert p in ['.github/workflows/verify.yml','web/app.js'],p
            source_mismatches.append(dict(path=p,frozen_sha256=h,current_sha256=actual))
    manifest=read(BASE/'copied-package-manifest.json')
    for p,h in manifest.items():assert digest(site/p)==h,p
    identity=read(BASE/'copied-identity.json');assert identity==read(site/'engine-j2/identity.json')
    report=read(BASE/'package-v2-report.json')
    for k in ['passed','immutableIdentity','exactReplay','preset','actualHistory','failedPrefix','recovery','corruptImportRejected']:assert report[k] is True,k
    assert report['identity']==identity
    assert (report['calls'],report['stateComparisons'],report['tangentComparisons'])==(327,1264,192)
    assert identity['model_sha256']==digest(ROOT/'models/research/j2/j2-linear-isotropic-hardening-be.json')
    for key,path in [('module_sha256','engine-j2/j2.js'),('wasm_sha256','engine-j2/j2.wasm'),('approval_sha256','j2-approval.json'),('review_sha256','j2-agent-review.json'),('catalogue_sha256','engine-j2/models.json')]:assert identity[key]==manifest[path]
    unchanged=read(BASE/'unchanged-root-engine.json');assert unchanged['before_sha256']==unchanged['after_sha256'] and unchanged['constitutive_root_engine_change'] is False
    for p,h in unchanged['after_sha256'].items():assert digest(site/p)==h,p
    contract=read(HERE/'pure-contract-tests.json');assert contract['passed'] and contract['assertions']==51 and contract['compiledCalls']==0
    browser=read(BASE/'browser-observations-v2.json');assert browser['source_freeze']=='interface-freeze-v2.json' and browser['compiled_package_report']=='package-v2-report.json'
    assert len(browser['checks'])==6 and len(browser['limitations'])==2
    return dict(passed=True,review_type='independent automated source and saved-evidence technical review',compiled_calls_by_reviewer=0,source_files=len(freeze['files']),source_mismatches_outside_dedicated_endpoint=source_mismatches,copied_package_files=len(manifest),unchanged_root_assets=3,numerical_review_passed=n['passed'],package_report=report,pure_contract_assertions=51,browser_evidence='Coordinator-recorded actual IAB observations; reviewer assessed saved record, did not operate browser',limitations=['Runtime failure GUI observation predates loader fix; final copied-package failure-prefix test passes.','Corrupt import rejection is pure-contract/copied-package evidence, not a separate GUI corrupt-file upload.','No live CI/Pages verification, human scientific signature, experimental validation or broad parameter-envelope claim.'])
if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-j2-delivery-v1/site')),indent=2))
