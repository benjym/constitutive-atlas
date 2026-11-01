#!/usr/bin/env python3
"""Saved-only main-laboratory review. No engine, builder or browser execution."""
import fractions,hashlib,json,pathlib,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=HERE.parents[4]

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):
    assert len(a)==len(b)==8
    for i,(x,y) in enumerate(zip(a,b)):assert abs(x-y)<=(.002 if i<6 else 2e-10),(i,x,y)
def run(site):
    freeze=read(BASE/'interface-freeze-r3.json');assert freeze['new_package_compiled_calls_before_freeze']==0
    for p,h in freeze['files'].items():assert sha(HERE/'source-r3'/p)==h,p
    for p,h in freeze['reused_engine'].items():assert sha(pathlib.Path(p))==h,p
    browserfreeze=read(BASE/'browser-execution-freeze.json');assert browserfreeze['actual_main_browser_runs_before_freeze']==0
    for p,h in browserfreeze['files'].items():assert sha(ROOT/p)==h,p
    manifest=read(BASE/'package-manifest-r3.json')
    assert manifest==read(site/'material-point-j2/package-manifest.json')
    for p,h in manifest.items():assert sha(site/p)==h,p
    for p in ['web/app.js','web/j2-laboratory.mjs','web/j2-contract.mjs']:assert sha(site/pathlib.Path(p).name)==freeze['files'][p]
    index=subprocess.check_output(['git','show',freeze['source_base']+':web/index.html'],cwd=ROOT)
    assert hashlib.sha256(index).hexdigest()==sha(site/'index.html')
    for p in ['j2.html','sls.html','power-creep.html','recorded.html','publications.html']:assert not (site/p).exists(),p
    for source,target in [('atlas.js','atlas.js'),('atlas.wasm','atlas.wasm'),('generated/models.json','models.json')]:assert sha(site/target)==freeze['reused_engine']['/private/tmp/atlas-j2-delivery-v1/root-wasm/'+source]
    identity=read(site/'material-point-j2/identity.json');browser=read(BASE/'browser-observations.json');assert browser['identity']==identity
    assert browser['interface_freeze']=='interface-freeze-r3.json' and browser['browser_freeze']=='browser-execution-freeze.json'
    checks={x['id']:x for x in browser['checks']}
    required=['direct-route-preset','failed-prefix-reset','custom-all-six','invalid-input','ordinary-roundtrip','actual-identity-retry','late-j2-initialization','late-ordinary-worker','catalogue','actual-import','actual-export','visual','console']
    for p in required:assert checks[p]['result']=='PASS',p
    assert checks['rapid-run-selection']['result']=='bounded-observation'
    export=read(BASE/'browser-export.json');assert sha(BASE/'browser-export.json')==checks['actual-export']['sha256']
    assert export['ok'] and export['provenance']==identity and len(export['points'])==4 and len(export['records'])==3
    # Exact prior independent rational reference; original preset source/reference receipts remain frozen.
    old=BASE.parent/'delivery-v1';oldfreeze=read(old/'interface-freeze-v2.json')
    reference=old/'independent-review/prospective-preset-reference.json'
    assert sha(reference)==oldfreeze['files'][str(reference.relative_to(ROOT))]
    preset=read(reference);request=export['request']
    assert request['parameters']==preset['parameters'] and request['initial']==preset['initial']
    close(export['points'][0]['state'],request['initial'])
    for i,(point,row,record) in enumerate(zip(export['points'][1:],preset['rows'],export['records'])):
        close(point['state'],row['state']);assert point['step']==i+1
        response=record['response'];close(response['state'],point['state']);assert response['ok']
        assert response['initial']==export['points'][i]['state'] and response['strain']==row['increment']
        assert response['parameters']==request['parameters'] and response['catalogue_hash']==identity['catalogue_hash']
        assert response['diagnostics']['increment_fractions']==[1]
    # Independently rederive new custom all-six elastic reference using exact fractions.
    custom=read(BASE/'custom-elastic-ui-reference.json');assert custom['frozen_before_custom_browser_observation']
    F=lambda x:fractions.Fraction(str(x));de=list(map(F,custom['increments'][0]));K=F(custom['parameters'][1]);G=F(custom['parameters'][2]);trace=sum(de[:3]);initial=list(map(F,custom['initial']))
    expected=[initial[i]+2*G*de[i]+((K-2*G/3)*trace if i<3 else 0) for i in range(6)]+initial[6:7]+[F(0)]
    assert list(map(float,expected))==custom['expected_each_row']
    mean=sum(expected[:3])/3;q2=F('1.5')*sum((expected[i]-(mean if i<3 else 0))**2 for i in range(6))
    assert q2<(F(custom['parameters'][3])+F(custom['parameters'][4])*initial[6])**2
    assert custom['increments'][1]==[0]*6
    # Parse the normal-builder saved gate; never invoke it.
    text=(BASE/'package-r3.log').read_text();start=text.index('{');report=json.JSONDecoder().raw_decode(text[start:])[0]
    assert report['passed'] and (report['calls'],report['stateComparisons'],report['tangentComparisons'])==(327,1264,192)
    assert report['identity']==identity
    for k in ['immutableIdentity','exactReplay','preset','actualHistory','failedPrefix','recovery','corruptImportRejected']:assert report[k] is True,k
    ordinary=read(BASE/'ordinary-package.json');assert ordinary['status']=='passed' and len(ordinary['ordinary'])==12
    proposal=read(BASE/'proposal-tests-r3.json');assert proposal['passed'] and proposal['assertions']==56 and proposal['compiledCalls']==0
    init=read(HERE/'r3-full-initialization-witness.json');assert init['descriptorCalls']==2 and init['enginePublished'] and init['errors'][1] is None
    cancellation=read(HERE/'run-cancellation-results.json');assert cancellation['passed'] and len(cancellation['cases'])==2
    for c in cancellation['cases']:assert c['postDeactivationDOMUnchanged'] and c['noResultPublished']
    return dict(passed=True,verdict='accept bounded exact r3 main-laboratory interface',source_files=12,package_assets=len(manifest),unchanged_root_assets=3,main_package_calls=327,state_comparisons=1264,tangent_comparisons=192,export_full_states=4,custom_elastic_exact_derivation=True,coordinator_browser_PASS_scenarios=len(required),pure_proposal_assertions=56,reviewer_compiled_calls=0,limitations=['Actual browser observations are coordinator records assessed by this reviewer.','Uninstrumented rapid200-row browser run does not prove pending timing; separate exact-source deferred-run witness covers cancellation.','Remote CI/Pages/live delivery and later source merges are outside this verdict.','Bounded synthetic material-point evidence; custom inputs exploratory, no broader domain or experimental claim.'])
if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-j2-main-v2/site-r3')),indent=2))
