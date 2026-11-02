from pathlib import Path
import ast,hashlib,importlib.util,json,unittest
O=Path(__file__).resolve().parent;R=O.parents[3];P=O.parent/'ci-dependency-alias-v1';ctx=O/'portable-context'
s=importlib.util.spec_from_file_location('portabletests',ctx/'tests/test_cmake_profile_build_v2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);T=m.TOOL
class Extra(m.ReceiptTests):
 def test_post_identity_seal(self):
  self.add_alias();v=T.capture(self.req,self.pre);T.verify(self.pre,T.digest(self.pre),self.post);post=json.loads(self.post.read_text());identities=v['snapshot']['dependency_identities'];self.assertEqual(post['dependency_identities_sha256'],hashlib.sha256(T.canonical(identities)).hexdigest());self.assertEqual(post['dependency_records_verified'],len(identities))
 def test_ancestor_retarget_same_header_bytes(self):
  target,alias,dep=self.add_alias(True);T.capture(self.req,self.pre);other=self.root/'sdk/other';other.mkdir();(other/'sched.h').write_bytes(target.read_bytes());alias.parent.unlink();alias.parent.symlink_to('other',target_is_directory=True)
  with self.assertRaises(ValueError):T.verify(self.pre,T.digest(self.pre),self.post)
 def test_alias_order_change(self):
  target,alias,dep=self.add_alias();T.capture(self.req,self.pre);text=dep.read_text();dep.write_text(text.replace(str(alias)+' '+str(target),str(target)+' '+str(alias)))
  with self.assertRaises(ValueError):T.verify(self.pre,T.digest(self.pre),self.post)
 def test_malformed_dependency_records(self):
  obj=self.objects[self.target][0];dep=Path(str(obj)+'.d')
  for text in ['no colon',str(obj)+':',str(obj)+': "unterminated',': '+str(self.root/'cpp/main.cpp')]:
   with self.subTest(text=text):
    dep.write_text(text)
    with self.assertRaises(ValueError):T.dependencies(dep,self.build,obj,{})
suite=unittest.TestSuite(Extra(n) for n in ['test_post_identity_seal','test_ancestor_retarget_same_header_bytes','test_alias_order_change','test_malformed_dependency_records']);result=unittest.TextTestRunner(verbosity=2).run(suite);assert result.wasSuccessful()
oldpath=R/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/response-symlink-fix-v1/tests/test_build_receipts.py'
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
a=methods(oldpath);b=methods(ctx/'tests/test_cmake_profile_build_v2.py');assert len(a)==40 and len(b)==55 and all(b[n]==v for n,v in a.items())
B=Path('/private/tmp/atlas-time-profile-v2/build-time-v2');saved=[]
for target in ['atlas_schedule_predictor_tests','atlas_time_tests','atlas_time_solver']:
 p=next((B/'CMakeFiles'/(target+'.dir')).rglob('*.o.d'));ids={};paths=T.dependencies(p,B,Path(str(p)[:-2]),ids);v=ids[str(p)];saved.append({'path':str(p),'sha256':T.digest(p),'ordered_members':len(v['ordered_members']),'canonical_members':len(paths),'aliases':v['canonical_alias_groups'],'identity_sha256':hashlib.sha256(T.canonical(v)).hexdigest()})
x={'extra_independent_tests':4,'original_methods_AST_exact':40,'new_methods':15,'saved_local_depfile_checks':saved,'scope':'Source/mock and saved .d parsing only; no actual build/material/module/remote; exact CI depfiles not available'};(O/'EXTRA-CHECKS.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
