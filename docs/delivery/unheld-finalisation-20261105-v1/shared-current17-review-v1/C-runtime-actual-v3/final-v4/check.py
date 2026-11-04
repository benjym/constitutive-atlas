"""Finite saved-data/source audit only; never invokes any engine."""
from pathlib import Path
import json,hashlib,importlib.util,re
H=Path(__file__).resolve().parent;N=H.parents[2];A=N/'rate-restoration-qualification-actual-v4';V3=N/'rate-restoration-qualification-actual-v3';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def test(label,value):assert value,label;checks.append(label)
def verify(p):q=Path(p['path']);test('pin '+str(q),q.stat().st_size==p['bytes']and sha(q)==p['sha256'])
p=N/'C-qualification-complete-v4/manifest.json';test('exact frozen parent complete manifest',sha(p)=='99be54a79e461c250fb818a5a0b943cfc30e0408674385372d6eeb61772e4bc8');manifest=read(p);test('153 exact unique evidence files',len(manifest['files'])==153 and len({r['path']for r in manifest['files']})==153)
for row in manifest['files']:verify(row)
test('exact recorded complete size',sum(r['bytes']for r in manifest['files'])==32454982)
P=N/'rate-restoration-qualification-plan-v3';spec=importlib.util.spec_from_file_location('_C_saved_source_only',P/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_execution_freeze(read(V3/'execution-freeze.json'));test('entire original execution/source/generated/tool/build validation still passes after legacy build (pure)',True)
for p in read(N/'rate-restoration-qualification-plan-v4/predecessor-pins.json'):verify(p)
review=N/'shared-current17-review-v1/C-supplement-plan-v4/decision.json';test('genuine separate exact v4 source review',sha(review)=='1d57d65f66c2cc94d42f9d93a7da80ed000c792028fc7ec08b56cc7adc665942');r=read(review);test('v4 author reviewer distinct',r['author_run']!=r['reviewer_run'])
receipts=[]
for phase in ['extra-native','extra-wasm','extra-pair','legacy-build','recorded74']:
 r=read(A/('outer-'+phase)/'receipt.json');receipts.append(r);test(phase+' genuinely passed/reaped',r['status']=='passed'and r['returncode']==0 and r['reaped_returncode']==0 and r['mandatory_reap']is True and r['cleanup_errors']==[]);verify(r['stdout']);verify(r['stderr']);test(phase+' source cwd',r['cwd']=='/private/tmp/atlas-baseline-delivery-20261105/source')
for x,y in zip(receipts,receipts[1:]):test('successor phases serial',x['ended_epoch']<=y['started_epoch'])
r=read(A/'recorded-legacy-build/receipt.json');test('actual historical target correctCatalogue/currentbuild/reaped',r['status']=='passed'and r['returncode']==0 and r['post_bindings_unchanged']is True and r['historical_catalogue']=='1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c'and r['observations_are_current_build_step']is True);test('legacy serial single target',r['argv'][-4:]==['--target','atlas_recorded_legacy_solver','--parallel','1']);verify(r['artifact']);test('legacy source before after exact',r['source_before']==r['source_after']);before={p['path']:p for p in r['configured_before']['files']};after={p['path']:p for p in r['configured_after']['files']};test('legacy all original configure/compiler/link pins exact with only generated dependency added',all(after[k]==v for k,v in before.items())and set(after)-set(before)=={str(Path(r['artifact']['path']).parent/'CMakeFiles/atlas_recorded_legacy_solver.dir/cpp/main.cpp.o.d')});test('legacy resolved compiler unchanged',r['configured_before']['resolved_cxx']==r['configured_after']['resolved_cxx']);[verify(p)for p in after.values()]
for group in ['source_before','source_after','tools']:
 for p in r[group].values():verify(p)
for p in r['generated']:verify(p)
metadata=read(Path(r['generated'][0]['path']));test('genuine five archived0.1 definitions',metadata['sha256']==r['historical_catalogue']and len(metadata['models'])==5 and all(x['schema_version']=='0.1'for x in metadata['models']))
text=(A/'outer-recorded74/stderr.raw').read_text();test('original74 exact no skip failure error',re.search(r'\nRan 74 tests in [0-9.]+s\n\nOK\n',text)is not None and 'skipped='not in text and ' ... skipped'not in text and ' ... FAIL'not in text and ' ... ERROR'not in text);test('74 actual individual cases',len(re.findall(r'^test_.* \.\.\. ok$',text,re.M))==74);test('historical original disabled response oracle exercised','test_disabled_legacy_responses_exact (tests.test_recorded_restarts.RestartNativeTests.test_disabled_legacy_responses_exact) ... ok'in text)
replayed=read(H/'supplement-replay-attempt2.json');test('independent saved original strict supplement assessor',replayed['passed']is True and replayed['compiled_calls']==0 and replayed['request_count']==12 and replayed['named_original702_per_backend']==9 and replayed['IGS_initial_points']==101);test('own original701pair replay exactly retained',read(H.parent/'original-pair-replay.json')==read(V3/'pair.json'))
test('earlier completed70 source/data checks passed',len(read(H.parent/'completed-checks-attempt3.json')['checks'])==70)
print(json.dumps({'identity':'C-complete-v4-independent-saved-checks','passed':True,'checks':checks,'check_count':len(checks),'supplement_checks':replayed['checks'],'actual_engine_calls_by_reviewer':0,'remaining_browser_package_live_fullCI_gates':True},indent=2))
