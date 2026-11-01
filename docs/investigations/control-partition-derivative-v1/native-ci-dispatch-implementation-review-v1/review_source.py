"""Independent bounded source closure and dispatch contract review."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess,re
D=Path(__file__).resolve().parent;C=D.parent;ROOT=C.parents[2];A=C/'native-ci-dispatch-implementation-v1';PLAN=C/'native-ci-dispatch-plan-v2';PR=C/'native-ci-dispatch-plan-v2-review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):checks.append({'id':n,'passed':bool(v)});assert v,n
for folder,h in [(A,'fb9fc1318324e6f542af5fe68ac058af18afc14a1364675c36efe52d5243767d'),(PLAN,'27325aae9a3f5f0d2ea7c4b7cc30ff6ccf80cd5ac454f14bbc234e14bfeb8710'),(PR,'5e304443eab3bb8dd4cb909256e854f3b2ca2a4dcbab736c9dc729050c56d237')]:
 ck('manifest/'+folder.name,sha(folder/'manifest.json')==h)
 ck('all packet bytes/'+folder.name,all(sha(folder/n)==v for n,v in load(folder/'manifest.json').items()))
f=load(A/'source-freeze.json');S=Path(f['source_directory']);pre=load(A/'preparation.json');O=Path(pre['original_source'])
ck('exact591 source inventory',len(f['source_files'])==591 and sorted(f['source_files'])==sorted(str(p.relative_to(S))for p in S.rglob('*')if p.is_file()))
ck('all591 source bytes exact',all(sha(S/n)==v for n,v in f['source_files'].items()))
ck('original582 unmodified',len(pre['original582'])==582 and all(sha(O/n)==v for n,v in pre['original582'].items()))
changed=[n for n,h in pre['original582'].items()if f['source_files'][n]!=h]
added=sorted(set(f['source_files'])-set(pre['original582']))
ck('only old profile test changed',changed==['tests/test_ci_profiles.py'])
ck('exact9 authorized new/overlay paths',added==sorted(['.github/workflows/verify.yml','catalogue/laboratory-package-policy.json','tests/test_native_fixture_dispatch.py','tools/build_ci_targets.py','tools/check_md1997_native_fixture_contract.py','tools/check_native_fixture_contracts.py','tools/check_native_fixture_dispatch.py','tools/ci_exact_replays.json','tools/run_ci_tests.py']))
ck('all public source copies equal isolated',all((S/p.relative_to(A/'files')).read_bytes()==p.read_bytes()for p in (A/'files').rglob('*')if p.is_file()))
ck('no caches or symlinks',not any(p.is_symlink()or '__pycache__'in p.parts or p.suffix in ['.pyc','.pyo']for p in S.rglob('*')))
base='37d70660e3561c342bb114716c233a3d06651bcb'
for name in ['tools/check_native_fixture_contracts.py','catalogue/laboratory-package-policy.json','tools/build_ci_targets.py','tools/run_ci_tests.py','tools/ci_exact_replays.json']:
 blob=subprocess.check_output(['git','show',base+':'+name],cwd=ROOT)
 ck('published exact unchanged dependency/'+name,(S/name).read_bytes()==blob)
wfproof=load(PLAN/'workflow-diff-proof.json');pub=(PLAN/'published-37d/.github/workflows/verify.yml').read_text();wf=(S/'.github/workflows/verify.yml').read_text()
ck('workflow exact accepted proposal',pub.replace(wfproof['replaced_original_block'],wfproof['proposed_block'],1)==wf)
ck('all non-native workflow bytes unchanged',wf.replace(wfproof['proposed_block'],wfproof['replaced_original_block'],1)==pub)
ck('strict before positive and always retention','if: always()'in wfproof['proposed_block']and wf.index('contracts.json')<wf.index('--suite macos-main')and 'continue-on-error'not in wf)
dispatch=(S/'tools/check_native_fixture_dispatch.py').read_text();md=(S/'tools/check_md1997_native_fixture_contract.py').read_text()
ck('fixed exact platform filters',"SUITES={'macos-main':['-E','^atlas_recorded$'],'linux-main':['-E','^(atlas_python|atlas_recorded)$'],'recorded':['-R','^atlas_recorded$']}"in dispatch)
ck('strict full16 before unchanged15 projection',dispatch.index("mapping==IDENTITIES[meta['route']]['models']")<dispatch.index("del mapping['manzari-dafalias-1997-constant-m-be-v1']")<dispatch.index("mapping==IDENTITIES['15']['models']")<dispatch.index('return helper.check_recorded_failure'))
ck('unchanged14/15 helper subprocess delegation',"if size in ['14','15']:"in dispatch and "str(source/'tools/check_native_fixture_contracts.py')"in dispatch and "require(len(report['processes'])==4"in dispatch)
ck('both selector variables sanitize before calls',"for key in SELECTORS:env.pop(key,None)"in md and "SELECTORS=('ATLAS_NATIVE_FIXTURES','ATLAS_NUMERICAL_FIXTURES')"in md)
ck('new selector only16 main suites',"md.NUMERICAL if meta['route']=='16' and suite!='recorded' else None"in dispatch)
ck('unknown context before calls','meta,helper=context('in dispatch and dispatch.index('meta,helper=context(')<dispatch.index("if operation=='check':check_contracts"))
ck('strict8 routes no positive success masked',"original_contracts(size)+md.contracts()"in dispatch and "returncode=1"in md and "row['returncode']==0,'positive CTest suite failed'"in dispatch)
ck('raw bytes retained before strict decoding',dispatch.index("row[key+'_base64']")<dispatch.index("row[key]=data.decode('utf-8',errors='strict')"))
ck('source and main artifacts checked after successful observations',"after,_=context("in dispatch and "require(meta==after,'source/build/artifact identity changed during observations')"in dispatch)
ck('binding/build receipt distinction disclosed','not a substitute for a separate actual build' in (A/'README.md').read_text())
ck('fixture deliberately original582 not composedv3',sha(S/'tests/test_solver.cpp')=='3407c01bfdb6ca511a26a41bf43384fca8b3ed254d484b84d616a0a44aebf71c')
ck('prospective16 requires exact15policy context',"'16':'915a91d2c6ee5ce7fba70f484a50beba313f4f4dc340283af0e2c4a823983029'"in dispatch)
ctnames=re.findall(r'add_test\(NAME ([^ ]+) COMMAND',(S/'CMakeLists.txt').read_text());ck('source actually mandates all10native registrations',len(ctnames)==10)
# The intentional weak point assertions document findings, never acceptance.
ck('B1 expected selected tests derived only from live registration',"names=re.findall(r'^add_test"in dispatch and "expected=[n for n in names"in dispatch)
ck('B2 CTest hash missing postflight check',dispatch.count("ctest_executable_sha256")==1)
ck('B3 positive label uses substring not line identity',"require(POSITIVE_STDOUT in section"in md)
probes=load(D/'probes-v2/transport-probes.json')
ck('independent3false-acceptance witnesses retained',[w['id']for w in probes['witnesses']]==['B1','B2','B3']and all(x['passed']for x in probes['checks']))
(D/'source-checks.json').write_text(json.dumps({'identity':'independent-native-ci-source-review-v1','source_checks':len(checks),'checks':checks,'changed_original_paths':changed,'added_paths':added,'native_registration_names':ctnames,'compiled_calls':0,'compiler_calls':0,'builds':0,'decision':'BLOCKED','blocking_findings':['B1','B2','B3'],'concerns':['C1']},indent=2)+'\n')
(D/'inputs.json').write_text(json.dumps({'author_manifest_sha256':sha(A/'manifest.json'),'author_source_freeze_sha256':sha(A/'source-freeze.json'),'accepted_plan_manifest_sha256':sha(PLAN/'manifest.json'),'accepted_plan_review_manifest_sha256':sha(PR/'manifest.json'),'published_Git_base':base,'prior_fixture_v3_review_manifest_sha256':sha(C/'native-admissible-fixture-implementation-review-v3/manifest.json')},indent=2)+'\n')
print(json.dumps({'source_checks':len(checks),'decision':'BLOCKED','compiled_calls':0}))
