"""Finite independent source review; no compiled/assessor subprocess calls."""
from pathlib import Path
import hashlib,json,ast,tempfile,runpy,copy
O=Path(__file__).resolve().parent;B=O.parent;A=B/'direct-ci-numerical-fix-v1';S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def require(v,n):
 if not v:raise ValueError(n)
 checks.append(n)
def main():
 require(sha(A/'manifest.json')=='4a06db2713dd12724fdb083ef7ac46e0d26c668ba068a7fdfe030a814cacd300','exact subject')
 m=json.loads((A/'manifest.json').read_text())
 for n,v in m['files'].items():
  p=Path(n);require(sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],'packet member '+n)
 for n,v in m['candidate_paths'].items():require(sha(S/n)==v['after']['sha256'],'candidate endpoint '+n)
 runner=A/'proposed/tools/check_md1997_numerical_ci.py';tree=ast.parse(runner.read_text());module=runpy.run_path(str(runner));inv=module['source_inventory']
 with tempfile.TemporaryDirectory(prefix='inert-',dir=O) as name:
  r=Path(name)
  for d in ['atlas','cpp/include','cpp/scalar-functions','schemas','models','tools/md1997_decimal_reference_current17_v1','tests','cmake']:(r/d).mkdir(parents=True,exist_ok=True)
  for n in ['CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tests/test_solver.cpp','tools/check_md1997_numerical_ci.py']:(r/n).write_text('inert')
  for n in module['REFERENCE_FILES']:(r/'tools/md1997_decimal_reference_current17_v1'/n).write_text('inert')
  scalar=r/'cpp/scalar-functions/pow.c';scalar.write_text('inert before')
  inv.__globals__['ROOT']=r;before=inv();scalar.write_text('inert after');after=inv()
  require(before==after and 'cpp/scalar-functions/pow.c'not in after,'B1 reproduced: linked scalar source changes invisible to inventory')
 old=(A/'preimages/qualification.yml').read_text();new=(A/'proposed/.github/workflows/qualification.yml').read_text()
 require('^(atlas_numerical|atlas_recorded)$'in new and '^(atlas_numerical|atlas_python|atlas_recorded)$'in new,'numerical removed from broad CTest as documented')
 helper=(A/'proposed/tools/check_native_fixture_contracts.py').read_text()
 require('source-admissible-current17'not in runner.read_text() and 'source-admissible-current17'not in helper and 'source-admissible-current17'not in new,'B2 reproduced: binary64 required failure not invoked by new mandatory CI path')
 require("for profile in [None,'unknown']"in helper,'existing default and unknown cases retained')
 require("ATLAS_NUMERICAL_FIXTURES','ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256','PYTHONPATH'"in runner.read_text(),'new runner scrubs ambient selectors')
 require("comparisons']==588"in runner.read_text() and "result.get('passed')is True"in runner.read_text(),'mandatory actual external assessment condition')
 require("require_unchanged(before,after)"in runner.read_text() and "require_unchanged(compiled,after_compiled)"in runner.read_text(),'postsource and compiled endpoint guards present')
 require('md1997-decimal-fd-reference-current17-v1'in runner.read_text() and 'explicit-gis20-occ-restart-duncan-sclay1-v6'in runner.read_text(),'new closed selectors')
 out={'identity':'independent-direct-ci-source-checks-v1','source_checks_passed':True,'assertions':len(checks),'blocking_findings_reproduced':['B1','B2'],'compiled_calls':0,'mock_calls':'only source_inventory on owned tiny inert files; cleaned','retained_author_failure':'initial SyntaxError retained in author packet; no subject changes'}
 (O/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
