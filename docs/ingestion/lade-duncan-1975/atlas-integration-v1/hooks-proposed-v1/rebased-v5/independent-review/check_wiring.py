"""Independent root-authored prospective wiring checks; no builds/material calls."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[6]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import approval_entry
A=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';V6=A/'hooks-proposed-v1/rebased-v6';V5=V6.parent/'rebased-v5';W=A/'workflow-v1';M=A/'maxwell-rebind-v1';Q=A/'qualified-assets-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def test(name,condition):
    assert condition,name
    checks.append(dict(name=name,passed=True))
def fn(s,name):
    start=s.index('function '+name+'(');return s[start:s.index('\n}',start)+2]
def main():
    proposal=json.loads((V6/'PROPOSAL.json').read_bytes())
    for group in ['before','proposed']:
        for name,pin in proposal[group].items():
            test(group+' exact '+name,sha(V6/group/name)==pin)
            if group=='before':test('live remains before '+name,sha(ROOT/name)==pin)
    for name in ['tools/build_web.py','catalogue/manifest.json','catalogue/publications.json']:
        test('v4 accepted bytes retained '+name,(V6/'proposed'/name).read_bytes()==(V6.parent/'proposed'/name).read_bytes())
    v5=(V5/'proposed/web/app.js').read_text();v6=(V6/'proposed/web/app.js').read_text();before=(V6/'before/web/app.js').read_text()
    test('single v6 synchronization edit',v6==v5.replace('const active=timedView.select(id);','const active=timedView.select(id);\n    if(active)$(\'model\').value=id;'))
    for name in ['activateLaboratoryModel','route']:
        test('ordinary deeplink function unchanged '+name,fn(v6,name)==fn(before,name))
    test('startup route initial unchanged','route({initial:true});simulate();' in v6)
    builder=(V6/'proposed/tools/build_web.py').read_text();ast.parse(builder)
    test('all profile calls retained',all(call in builder for call in ['bundle_maxwell(dest,args.maxwell_wasm_dir)','bundle_implicit_path(dest,args.implicit_path_wasm_dir)','bundle_controlled_path(dest,args.controlled_path_wasm_dir)']))
    test('package report outside guarded engine and unique',"check_root=dest/'implicit-path-package-checks'" in builder and 'tempfile.mkdtemp(' in builder and 'check=True' in builder)
    wp=json.loads((W/'PROPOSAL.json').read_bytes());wf=(W/'verify-proposed.yml').read_text();wb=(W/'verify-before.yml').read_text()
    test('workflow before exact live',sha(ROOT/'.github/workflows/verify.yml')==wp['before']['.github/workflows/verify.yml']==sha(W/'verify-before.yml'))
    test('workflow after exact pin',sha(W/'verify-proposed.yml')==wp['proposed']['.github/workflows/verify.yml'])
    restore='          python -B tools/provision_implicit_path_assets.py\n';preset='          node tools/test_implicit_path_public_presets.mjs web/dist/engine-implicit-path "$RUNNER_TEMP/lade-public-presets.json" web/dist/engine-implicit-path/identity.json\n'
    test('exactly two restores and required presets',wf.count(restore)==2 and wf.count(preset)==2)
    test('every previous workflow byte/gate retained',wf.replace(restore,'').replace(preset,'')==wb)
    for job in ['wasm','wasm-linux']:
        # YAML job boundaries, not execution. Original workflow syntax is retained.
        import re
        section=re.search(r'^  '+job+r':\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)',wf,re.M|re.S).group(1)
        test(job+' correct guarded ordering',section.index('tools/provision_maxwell_assets.py')<section.index('tools/provision_implicit_path_assets.py')<section.index('python tools/build_web.py')<section.index('node tools/test_implicit_path_public_presets.mjs')<section.index('Upload tested website') if job=='wasm' else section.index('tools/provision_maxwell_assets.py')<section.index('tools/provision_implicit_path_assets.py')<section.index('python tools/build_web.py')<section.index('node tools/test_implicit_path_public_presets.mjs'))
    b=json.loads((M/'QUALIFIED_BINDING.json').read_bytes());old=(M/'provision_maxwell_assets-before.py').read_text();new=(M/'provision_maxwell_assets-proposed.py').read_text();ast.parse(new)
    test('Maxwell exact old live/proposed pins',sha(ROOT/'tools/provision_maxwell_assets.py')==sha(M/'provision_maxwell_assets-before.py')==b['helper_before_sha256'] and sha(M/'provision_maxwell_assets-proposed.py')==b['helper_proposed_sha256'])
    transformed=old.replace("'docs/ingestion/maxwell-itasca900/atlas-ci-v2'","'docs/ingestion/lade-duncan-1975/atlas-integration-v1/maxwell-rebind-v1'").replace('2bfe6239807e33a55e9800df831c333b21ead5ba4d1c8720c947d7a89e0080c2',b['qualification_sha256']).replace('7c240bbad74a80d1d3c754711f1b41c5d690d07d53663cd2565f2767357e31d0',b['build_review_sha256']).replace('independent-review/final-v1/build-review.json','independent-review/build-review.json')
    test('Maxwell only four declared constant/path edits',new==transformed)
    review=json.loads((M/'independent-review/build-review.json').read_bytes());qualification=json.loads((M/'maxwell-qualification.json').read_bytes());receipt=json.loads((M/'independent-review/review-receipt.json').read_bytes())
    test('Maxwell genuine separate acceptance',receipt['status']=='accepted' and receipt['reviewer_run']=='/root/lade_source_review' and review['status']=='accepted')
    test('Maxwell accepted record and qualification exact',sha(M/'maxwell-qualification.json')==b['qualification_sha256'] and sha(M/'independent-review/build-review.json')==b['build_review_sha256'])
    test('Maxwell same accepted binding and gates',qualification['binding']==review['binding'] and qualification['gates']==review['gates'] and all(qualification['gates'].values()))
    test('Maxwell archive pin unchanged',"ARCHIVE_SHA256 = '"+b['archive_sha256']+"'" in old and "ARCHIVE_SHA256 = '"+b['archive_sha256']+"'" in new)
    rp=json.loads((Q/'REGISTRY_PROPOSAL.json').read_bytes());oldreg=json.loads((ROOT/'catalogue/approved-models.json').read_bytes());newreg=json.loads((Q/'approved-models-proposed.json').read_bytes());entry=json.loads((Q/'approval-entry.json').read_bytes())
    test('registry exact before/after pins',sha(ROOT/'catalogue/approved-models.json')==rp['old_sha256'] and sha(Q/'approved-models-proposed.json')==rp['new_sha256'])
    generated=approval_entry(ROOT/'catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json',ROOT)
    test('registry entry canonically generated from validated independent E5',generated==entry)
    test('registry append only, every prior value retained',newreg==dict(oldreg,models=oldreg['models']+[entry]))
    for packet,status,tool in [('asset-provision-review-v2','accepted-prospective-source','tools/provision_implicit_path_assets.py'),('public-ci-review','accepted-to-study','tools/test_implicit_path_public_presets.mjs')]:
        r=json.loads((ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review'/packet/'review-receipt.json').read_bytes())
        test('accepted separate dependency '+packet,r['status']==status and not r['blocking_findings'] and r['reviewer_run']=='/root/lade_source_review' and r['files'][tool]==sha(ROOT/tool))
    tp=json.loads((W/'TEST_PROPOSAL.json').read_bytes());tb=(W/'test_j2_main_routing-before.mjs').read_text();ta=(W/'test_j2_main_routing-proposed.mjs').read_text()
    test('J2 marker before/current and proposal exact',sha(ROOT/'tests/test_j2_main_routing.mjs')==sha(W/'test_j2_main_routing-before.mjs')==tp['before']['tests/test_j2_main_routing.mjs'] and sha(W/'test_j2_main_routing-proposed.mjs')==tp['proposed']['tests/test_j2_main_routing.mjs'])
    expected=tb.replace('"import {setupJ2Laboratory}",','"import {setupJ2Laboratory}","import {setupImplicitPathLaboratory}",').replace("setupMaxwellLaboratory({chart,cancelOrdinary:()=>cancel('')})])","setupMaxwellLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupImplicitPathLaboratory({chart,cancelOrdinary:()=>cancel('')})])")
    test('J2 all other assertions unchanged',ta==expected)
    witness=json.loads((HERE/'dropdown-witness-v6.json').read_bytes())
    test('actual unchanged controller dropdown synchronized by root hook',witness['dropdown_synchronized'] is True and witness['app_sha256']==sha(V6/'proposed/web/app.js'))
    test('actual catalogue/hash hook avoids duplicate auto run',witness['duplicate_auto_run'] is False and witness['after_hash_change']['runs']==1)
    (HERE/'wiring-check-results.json').write_text(json.dumps(dict(passed=True,checks=checks,compiledCalls=0,scope='Root-authored v6 hook, workflow, Maxwell constants and append-only registry wiring only; no scientific re-review or artifact execution'),indent=2)+'\n')
    print(json.dumps(dict(passed=True,checks=len(checks))))
if __name__=='__main__':main()
