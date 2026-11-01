#!/usr/bin/env python3
"""Source/saved-response fixture audit; no compiled engine calls."""
import difflib,hashlib,json,pathlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[5]
BASE=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for group in ['inputs','outputs']:
  for name,h in manifest[group].items():assert sha(ROOT/name)==h,name
 identity=json.loads((BASE/'before-identities.json').read_text())
 changes={}
 for name,h in identity['files'].items():
  old=(BASE/'before'/name).read_text();new=(ROOT/name).read_text()
  assert sha(BASE/'before'/name)==h
  # No old assertion line was removed or replaced. Only VM context/scaffolding changes.
  removed=[line[2:] for line in difflib.ndiff(old.splitlines(),new.splitlines()) if line.startswith('- ')]
  assert len(removed)==1 and 'vm.runInNewContext(' in removed[0] and 'assert.' not in removed[0]
  oldassert=[line for line in old.splitlines() if 'assert.' in line]
  assert all(line in new.splitlines() for line in oldassert)
  assert "app.match(/^function specialLaboratoryActive\\(\\).*$/m)[0]" in new
  assert "for(const profile of ['j2View','timedView'])vm.runInNewContext" in new
  changes[name]=dict(original_assertion_lines_preserved=len(oldassert),removed_vm_scaffolding_lines=1,real_helper_extracted=True,active_profiles_exercised=2)
 result=subprocess.run(['python3','-B','-m','unittest','tests.test_laboratory_view','tests.test_web_effective_scope'],cwd=ROOT,capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
 assert 'Ran 2 tests' in result.stderr and '\nOK' in result.stderr
 return dict(passed=True,verdict='accept bounded VM-fixture repair',fixtures=changes,python_wrapper_tests=2,reviewer_compiled_calls=0,production_changes_reviewed=False,limits=['CI rerun and release verification remain coordinator-owned.','Archive-map redirects are separate evidence provenance changes, not reviewed here.'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
