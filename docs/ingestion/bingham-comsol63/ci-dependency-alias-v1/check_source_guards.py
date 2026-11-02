"""Current source/canonical evidence guards only; no engine or compiler calls."""
from pathlib import Path
import ast,gzip,hashlib,json,runpy,sys
H=Path(__file__).resolve().parent;R=H.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns=runpy.run_path(str(R/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/check_preparation.py'));closure=ns['closure'];closure.__globals__['ROOT']=R
index=json.loads(Path('/private/tmp/atlas-bingham-release-v2/docs/ingestion/bingham-comsol63/frozen-engine-packaging-plan-v1/capsules/INDEX.json').read_text());selected={p.relative_to(H/'candidates').as_posix() for p in (H/'candidates').rglob('*') if p.is_file()};groups={}
for group,count in [('maxwell',149),('norsand',121)]:
 actual=closure(group);assert actual==index['groups'][group]['source_files'] and len(actual)==count;assert not selected.intersection(actual);groups[group]=count
sys.path.insert(0,str(R));from atlas.agent_review import validate_review;from atlas.evidence import checked_receipt
v=validate_review(R/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json',root=R,for_approval=True)
doc='docs/ingestion/bingham-comsol63/execution-v5/source-bindings.json';s=json.loads((R/doc).read_text())['source_files'];assert not selected.intersection(s)
for n,h in s.items():assert sha(checked_receipt(R,doc,n,h))==h
old=R/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/response-symlink-fix-v1/tests/test_build_receipts.py';new=H/'candidates/tests/test_cmake_profile_build_v2.py'
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for c in ast.parse(p.read_text()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old);b=methods(new);assert all(b[n]==value for n,value in a.items());assert sum(n.startswith('test_') for n in a)==40
before=(H/'before/.github/workflows/verify.yml').read_text();after=(H/'candidates/.github/workflows/verify.yml').read_text();removed=after.replace('          python -B tests/test_cmake_profile_build_v2.py\n','').replace('tools/record_cmake_profile_build_v2.py','tools/record_cmake_profile_build.py');assert removed==before;assert after.count('          python -B tests/test_cmake_profile_build_v2.py\n')==3
assert (R/'tools/record_cmake_profile_build.py').read_bytes()==(H/'before/tools/record_cmake_profile_build.py').read_bytes();assert (R/'.github/workflows/verify.yml').read_bytes()==(H/'before/.github/workflows/verify.yml').read_bytes()
report={'passed':True,'current_old_source_closures':groups,'actual_qualified_v5_source_bindings':len(s),'E5_artifacts':len(v['artifacts']),'candidate_intersections_with_scientific_closures':0,'original_test_methods_preserved_AST_exact':40,'new_test_methods':sum(n.startswith('test_') for n in b)-40,'workflow_other_bytes_exact':True,'source_mock_commands_added':3,'old_helper_unchanged':True,'compiler_tool_material_calls':0}
(H/'SOURCE-GUARDS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
