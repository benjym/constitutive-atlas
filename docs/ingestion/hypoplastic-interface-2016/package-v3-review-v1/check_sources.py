"""Independent lightweight source-only checks; no package/helper main execution."""
from pathlib import Path
import ast,hashlib,json,tempfile,shutil
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
P=BASE/'package-v3'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 report={'scope':'source-only independent prospective review; no package, freeze, compiler, material, browser or remote execution','checks':{}}
 manifest=json.loads((P/'manifest.json').read_text())
 assert digest(P/'manifest.json')=='239bb2307146255172061a74e434ec4ec286a6a557126640fb32c9d580796ef1'
 for n,h in manifest['files'].items():assert digest(P/n)==h,n
 report['checks']['exact_manifest_and_all_five_members']=True
 parsed={n:ast.parse((P/n).read_text()) for n in ['run_package.py','freeze_inputs.py']}
 report['checks']['both_scripts_parse']=True
 old=json.loads((BASE/'package-v2/plan.json').read_text());new=json.loads((P/'plan.json').read_text())
 expected=[v.replace('/release-v2','/release-v3').replace('/site-v2','/site-v3') for v in old['argv']]
 i=expected.index('--output');expected[i:i]=['--perzyna-wasm-dir',new['cwd']+'/build-perzyna-public']
 assert expected==new['argv']
 assert new['parents']==['106a9cf8c327c9c262a97eb86aa04dae3f6cadb8','136636f14ce12b0dd83e65a8c37d3af9a5cc1381']
 report['checks']['v2_full_argv_exact_relocation_plus_perzyna']=True
 report['checks']['exact_ordered_two_parent_requirement']=True
 # Execute only the exact pure sha definition, with stdlib hashlib.
 sha_node=next(n for n in parsed['freeze_inputs.py'].body if isinstance(n,ast.FunctionDef) and n.name=='sha')
 scope={'hashlib':hashlib};exec(compile(ast.Module(body=[sha_node],type_ignores=[]),'extracted-sha','exec'),scope)
 try:scope['sha'](str(P/'freeze_inputs.py'))
 except AttributeError as e:report['hash_string_fault']={'reproduced':True,'type':type(e).__name__,'message':str(e)}
 else:raise AssertionError('Expected frozen helper string argument failure')
 # Execute only the exact wrapper verify function against a synthetic owned fixture.
 verify_node=next(n for n in parsed['run_package.py'].body if isinstance(n,ast.FunctionDef) and n.name=='verify')
 with tempfile.TemporaryDirectory(dir=HERE,prefix='synthetic-') as tmp:
  t=Path(tmp);root=t/'root';root.mkdir();fixture=t/'packet';fixture.mkdir()
  for n in ['source-freeze.json','plan.json','run_package.py','freeze_inputs.py']:(fixture/n).write_text('{}')
  (root/'models').mkdir();(root/'models/declared.json').write_text('{}')
  frozen={'plan_sha256':digest(fixture/'plan.json'),'wrapper_sha256':digest(fixture/'run_package.py'),'freeze_script_sha256':digest(fixture/'freeze_inputs.py'),'source':{'models/declared.json':{'sha256':digest(root/'models/declared.json')}},'qualified_assets_and_ignored_witness':{},'deleted_paths':[]}
  # __file__ uses Path solely to bypass the separately proven string bug; this isolates set closure.
  env={'sha':digest,'HERE':fixture,'freeze_digest':digest(fixture/'source-freeze.json'),'freeze':frozen,'root':root,'Path':Path,'__file__':fixture/'run_package.py'}
  exec(compile(ast.Module(body=[verify_node],type_ignores=[]),'extracted-verify','exec'),env)
  env['verify']()
  (root/'models/unfrozen-added.json').write_text('{"unreviewed":true}')
  env['verify']()
  shutil.copytree(root/'models',t/'packaged-models')
  assert (t/'packaged-models/unfrozen-added.json').exists()
  report['source_set_fault']={'reproduced':True,'exact_verify_accepts_added_model':True,'copytree_includes_added_unfrozen_file':True,'string_bug_isolated_with_Path_filename':True}
 # Fault-inject the exact outer lifecycle block with an inert fake child.
 outer=next(n for n in parsed['run_package.py'].body if isinstance(n,ast.Try))
 with tempfile.TemporaryDirectory(dir=HERE,prefix='lifecycle-') as tmp:
  class FakeChild:
   pid=12345
   alive=True
   def wait(self):raise KeyboardInterrupt('synthetic interruption; no real process')
   def terminate(self):self.alive=False
   def kill(self):self.alive=False
  child=FakeChild()
  class FakeSubprocess:
   @staticmethod
   def Popen(*args,**kwargs):return child
  record={};t=Path(tmp)
  import time
  env={'HERE':t,'subprocess':FakeSubprocess,'plan':new,'root':t,'env':{},'record':record,'save':lambda:None,'verify':lambda:None,'sha':digest,'time':time,'code':1}
  try:exec(compile(ast.Module(body=[outer],type_ignores=[]),'extracted-lifecycle','exec'),env)
  except KeyboardInterrupt:pass
  else:raise AssertionError('Expected propagated synthetic interruption')
  assert child.alive and record['status']=='failed-retained'
  report['interruption_fault']={'reproduced_with_inert_fake_child':True,'child_not_terminated_or_reaped':child.alive,'record_status':record['status'],'closed_log_hashes_retained':sorted(record['logs'])}
 report['inputs']={str(P.relative_to(BASE)/n):digest(P/n) for n in ['manifest.json',*manifest['files']]}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
