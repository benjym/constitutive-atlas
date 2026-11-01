#!/usr/bin/env python3
"""Check retained scoped integration sources without builds or engine execution."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    receipt=json.loads((HERE/'source-receipts.json').read_text())
    for item in receipt['files']:
        for kind in ['base','stage']:
            assert sha(HERE/kind/item['path'])==item[kind+'_sha256']
    before=json.loads((HERE/'base/catalogue/manifest.json').read_text());after=json.loads((HERE/'stage/catalogue/manifest.json').read_text())
    added=[x for x in after['models'] if x['id']=='j2-linear-isotropic-hardening-be'];assert len(added)==1
    trimmed=dict(after);trimmed['models']=[x for x in after['models'] if x['id']!=added[0]['id']];assert trimmed==before
    assert added[0]['material_laboratory']=='j2.html' and added[0]['executable'] is False and added[0]['status']=='reviewed'
    app=(HERE/'stage/web/app.js').read_text();assert 'Open strain-increment laboratory' in app and 'complete starting-history controls' in app
    workflow=(HERE/'stage/.github/workflows/verify.yml').read_text()
    oldworkflow=(HERE/'base/.github/workflows/verify.yml').read_text()
    assert workflow.count('cmake --build build-j2 --target atlas_j2_solver --parallel 1')==1
    assert workflow.count('cmake --build build-j2-wasm --target atlas_j2_solver --parallel 1')==2
    for fixture in ['explicit-gis20-v2']:
        assert workflow.count(fixture)==oldworkflow.count(fixture)
    builder=(HERE/'stage/tools/build_web.py').read_text();assert 'bundle_j2(dest,args.j2_wasm_dir)' in builder
    assert "str(ROOT/'tools/test_j2_package.mjs'),str(dest)],check=True" in builder
    tests=(HERE/'stage/tests/test_catalogue.py').read_text()
    for text in ["checked_receipt(ROOT, document, evidence['path'], evidence['sha256'])","self.assertEqual(json.loads((ROOT / document).read_text()), record)","self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), evidence['sha256'])"]:assert text in tests
    return dict(passed=True,base_commit=receipt['base_commit'],source_files=6,manifest_other_entries_semantically_unchanged=True,workflow_prior_fixtures_unchanged=True,serial_explicit_J2_targets=True,package_checker_failure_propagates=True,approval_full_object_and_receipt_checks_retained=True,compiled_calls_by_reviewer=0,verdict='accept exact retained scoped integration sources; live delivery excluded')
if __name__=='__main__':print(json.dumps(run(),indent=2))
