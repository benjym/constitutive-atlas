"""Prepare actual-current source drafts only; no approval, installation or engine."""
from pathlib import Path
import hashlib,json,shutil,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];V2=Path('/private/tmp/atlas-bingham-release-v2')
OLD=V2/'docs/ingestion/bingham-comsol63/interface-v4-preparation-v1/ci-build-receipts-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,data):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data)
assert sha(OLD/'MANIFEST.json')=='51ca5aec8da90f894a0c4eb8d5fa4c240a250bf9ecac1dd9dd8f53fa4ebd2d39'
composition=json.loads((OLD/'COMPOSITION.json').read_text());assert sha(OLD/'COMPOSITION.json')=='54acfdbb3db836eaa6a683070b311f6a6f6efeb8739dd7d19a5b68c1dc5adc66'
for n,h in composition['candidate_files'].items():assert sha(OLD/'candidates'/n)==h
for n in composition['candidate_files']:put('candidates/'+n,(OLD/'candidates'/n).read_bytes())
# Exact current hooks, with only Bingham additions.
name='web/app.js';text=(ROOT/name).read_text();text="import {setupBinghamLaboratory} from './bingham-laboratory.mjs';\n"+text
needle='timedView=createLaboratoryControllerRouter([';assert text.count(needle)==1;text=text.replace(needle,needle+"setupBinghamLaboratory({chart,cancelOrdinary:()=>cancel('')}),")
put('candidates/'+name,text.encode())
name='tools/build_web.py';text=(ROOT/name).read_text();needle='    args=parser.parse_args()';assert text.count(needle)==1
text=text.replace(needle,"    parser.add_argument('--bingham-wasm-dir',type=Path,default=ROOT/'build-bingham-public',help='Exact independently reviewed Bingham physical-time engine')\n"+needle)
needle='    from build_burgers_web import bundle as bundle_burgers';assert text.count(needle)==1
text=text.replace(needle,"    from build_bingham_laboratory import bundle as bundle_bingham\n    bundle_bingham(dest,args.bingham_wasm_dir)\n    subprocess.run(['node',str(ROOT/'tools/test_bingham_package.mjs'),str(dest)],check=True)\n"+needle);put('candidates/'+name,text.encode())
name='tests/test_j2_main_routing.mjs';text=(ROOT/name).read_text();needle='// Execute the exact ordinary import function';assert text.count(needle)==1
addition='''assert.equal(setups.filter(name=>name==='setupBinghamLaboratory').length,1);checks++;
assert.ok(registration.includes("setupBinghamLaboratory({chart,cancelOrdinary:()=>cancel('')})"));checks++;
assert.ok(source.includes("import {setupBinghamLaboratory} from './bingham-laboratory.mjs';"));checks++;
''';text=text.replace(needle,addition+needle);put('candidates/'+name,text.encode())
# The only current-main workflow change relative to exact d74 predecessor is
# the independently qualified Lade/NorSand unit-alias path; retain it exactly.
pre=V2/'docs/ingestion/bingham-comsol63/current-preservation-v2/current-bytes/88a8f98d24f90d8c465d877dd5bb21d3a2685cc9760861cf569d481d0a27d1a6/.github/workflows/verify.yml'
current=(ROOT/'.github/workflows/verify.yml').read_text();oldline='--controlled-path-wasm-dir docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand'
newline=oldline+'-unit-alias-v1';assert pre.read_text().count(oldline)==2 and current==pre.read_text().replace(oldline,newline)
p=HERE/'candidates/.github/workflows/verify.yml';text=p.read_text();assert text.count('--controlled-path-wasm-dir build-controlled-path-public')==2
p.write_text(text.replace('--controlled-path-wasm-dir build-controlled-path-public',newline))
# Select tiny strict response-symlink correction; old51ca remains immutable.
p=HERE/'candidates/tools/record_cmake_profile_build.py';p.write_bytes((HERE/'response-symlink-fix-v1/candidates/tools/record_cmake_profile_build.py').read_bytes())
extras=['web/bingham-laboratory.mjs','web/bingham-atlas-contract.mjs','web/bingham-atlas-worker.mjs','tools/build_bingham_laboratory.py','tools/test_bingham_package.mjs','tools/provision_bingham_assets.py','tools/provision_bingham_dependency_assets.py','tests/test_bingham_laboratory_contract.mjs']
for n in extras:put('candidates/'+n,(V2/n).read_bytes())
policy=HERE/'candidates/docs/ingestion/bingham-comsol63/interface-v4/POLICY.json';value=json.loads(policy.read_text());value['pipeline']['build_receipts']['tool']['sha256']=sha(HERE/'candidates/tools/record_cmake_profile_build.py');value['pipeline']['current_release_context']={'base':'e6f06114','current_atlas_policy':'docs/ingestion/bingham-comsol63/current-atlas-v4/POLICY.md','source_preparation':'Prospective current-main merge after compiled v5 observations; original physical references/settings/gates remain unchanged, no new numerical freeze implied','response_symlink_fix_manifest':{'path':str((HERE/'response-symlink-fix-v1/MANIFEST.json').relative_to(ROOT)),'sha256':sha(HERE/'response-symlink-fix-v1/MANIFEST.json')},'independent_status':'pending exact composition review; superseded51ca changes requested for strict response symlink policy'};policy.write_text(json.dumps(value,indent=2)+'\n')
# Remove stale d74-count policy from selected candidate set. Keep its original
# exact bytes under before, rather than silently rewriting that frozen identity.
stale=HERE/'candidates/docs/ingestion/bingham-comsol63/current-atlas-v3/POLICY.md';put('before/superseded-current-atlas-v3-POLICY.md',stale.read_bytes());stale.unlink()
# Preserve exact current ten paths even where future coordinator edits are TBD.
targets=['web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','docs/STATUS.md','ROADMAP.md','IMPLEMENTATION_PLAN.md','web/model-profile-data.mjs','tests/test_j2_main_routing.mjs']
inputs={n:sha(ROOT/n) for n in targets}
for n in targets:put('before/shared/'+n,(ROOT/n).read_bytes())
for n in ['CMakeLists.txt','atlas/agent_review.py','atlas/research.py','tools/build_database.py','docs/ingestion/bingham-comsol63/source-v1/candidate.json']:
 inputs[n]=sha(ROOT/n)
put('INPUTS.json',(json.dumps({'kind':'bingham-current-e6f06114-integration-inputs-v3','release_inputs':inputs,'archive_targets':targets,'prior_ci_composition':{'path':str(OLD/'COMPOSITION.json'),'sha256':sha(OLD/'COMPOSITION.json'),'status':'changes requested; select distinct response correction'},'source_only':True,'installed':False},indent=2)+'\n').encode())
for n in ['web/app.js','tools/build_web.py','tests/test_j2_main_routing.mjs','.github/workflows/verify.yml']:
 put('diffs/'+n+'.diff',''.join(difflib.unified_diff((ROOT/n).read_text().splitlines(True),(HERE/'candidates'/n).read_text().splitlines(True),fromfile=n,tofile='candidate/'+n)).encode())
print(json.dumps({'candidate_files':sum(p.is_file() for p in (HERE/'candidates').rglob('*')),'archive_targets':len(targets),'current_workflow_lade_alias_preserved':True,'compiled_calls':0,'installed':False},indent=2))
