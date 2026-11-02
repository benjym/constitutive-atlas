from pathlib import Path
import ast,copy,json
O=Path(__file__).resolve().parent;P=O.parent/'ci-dependency-alias-v1';old=ast.parse((P/'before/tools/record_cmake_profile_build.py').read_text());new=ast.parse((P/'candidates/tools/record_cmake_profile_build_v2.py').read_text())
class Normalize(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str):n.value=n.value.replace('atlas-cmake-profile-build-pre-v2','atlas-cmake-profile-build-pre-v1').replace('atlas-cmake-profile-build-post-v2','atlas-cmake-profile-build-post-v1').replace('atlas-cmake-profile-build-failed-v2','atlas-cmake-profile-build-failed-v1')
  return n
 def visit_Assign(self,n):
  if any(isinstance(t,ast.Name) and t.id=='dependency_identities' for t in n.targets):return None
  return self.generic_visit(n)
 def visit_Call(self,n):
  if isinstance(n.func,ast.Name) and n.func.id=='dependencies' and len(n.args)==4:n.args=n.args[:3]
  return self.generic_visit(n)
 def visit_Dict(self,n):
  keep=[i for i,k in enumerate(n.keys) if not isinstance(k,ast.Constant) or k.value not in {'dependency_identities','dependency_identity_contract','dependency_identities_sha256','dependency_records_verified'}];n.keys=[n.keys[i] for i in keep];n.values=[n.values[i] for i in keep];return self.generic_visit(n)
a={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)};b={n.name:n for n in new.body if isinstance(n,ast.FunctionDef)};rows=[]
for name in a:
 if name=='dependencies':continue
 equal=ast.dump(a[name],include_attributes=False)==ast.dump(Normalize().visit(copy.deepcopy(b[name])),include_attributes=False);rows.append({'function':name,'unchanged_after_explicit_receipt_version_and_identity_additions':equal})
assert all(r['unchanged_after_explicit_receipt_version_and_identity_additions'] for r in rows),rows
wold=(P/'before/.github/workflows/verify.yml').read_text();wnew=(P/'candidates/.github/workflows/verify.yml').read_text();line='          python -B tests/test_cmake_profile_build_v2.py\n';assert wnew.count(line)==3;inverse=wnew.replace(line,'').replace('tools/record_cmake_profile_build_v2.py','tools/record_cmake_profile_build.py');assert inverse==wold
(O/'CODE-CHECK.json').write_text(json.dumps({'functions':rows,'new_function':'dependency_identity','changed_function':'dependencies','workflow_inverse_equals_entire_old_workflow':True,'only_workflow_changes':'versioned recorder path and three explicit early source-mock test commands','old_recorder_command_count':wold.count('tools/record_cmake_profile_build.py'),'new_recorder_command_count':wnew.count('tools/record_cmake_profile_build_v2.py')},indent=2)+'\n');print('AST old safeguards retained; workflow inverse exact')
