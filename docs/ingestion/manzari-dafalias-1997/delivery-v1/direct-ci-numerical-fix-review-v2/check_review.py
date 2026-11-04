"""Finite frozen successor review, source/inert mocks only."""
from pathlib import Path
import json,hashlib,runpy,tempfile,ast
O=Path(__file__).resolve().parent;B=O.parent;A=B/'direct-ci-numerical-fix-v2';V=B/'direct-ci-numerical-fix-v1';S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
count=0
def check(v,n):
 global count
 count+=1
 if not v:raise ValueError(n)
def main():
 check(sha(A/'manifest.json')=='c4ac8e40151a337d9c44c51e992b797b27799ccefc641a703c553b62b70da569','exact successor')
 m=json.loads((A/'manifest.json').read_text())
 for n,v in m['files'].items():check(sha(Path(n))==v['sha256'] and Path(n).stat().st_size==v['bytes'],'frozen '+n)
 for n,v in m['candidate_paths'].items():check(sha(S/n)==v['sha256'],'candidate '+n)
 for n in ['.github/workflows/qualification.yml','tools/check_native_fixture_contracts.py']:check((A/'proposed'/n).read_bytes()==(V/'proposed'/n).read_bytes(),'unchanged v1 '+n)
 r=A/'proposed/tools/check_md1997_numerical_ci.py';code=r.read_text();ast.parse(code);g=runpy.run_path(str(r));inv=g['source_inventory'];unchanged=g['require_unchanged'];refusals=[]
 with tempfile.TemporaryDirectory(prefix='inert-',dir=O) as temp:
  root=Path(temp)
  for name in ['atlas','cpp/include','cpp/scalar-functions','schemas','models','tests','cmake','tools/md1997_decimal_reference_current17_v1']:(root/name).mkdir(parents=True,exist_ok=True)
  for name in ['CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tests/test_solver.cpp','tools/check_md1997_numerical_ci.py']:(root/name).write_text('inert')
  for name in g['REFERENCE_FILES']:(root/'tools/md1997_decimal_reference_current17_v1'/name).write_text('inert')
  inv.__globals__['ROOT']=root
  for name in ['pow.c','libm.h']:(root/'cpp/scalar-functions'/name).write_text('inert')
  first=inv()
  for name in ['pow.c','libm.h']:
   f=root/'cpp/scalar-functions'/name;f.write_text('changed');after=inv();check(first!=after,'B1 scalar change visible '+name)
   try:unchanged(first,after)
   except ValueError:refusals.append('scalar mutation '+name)
   else:raise ValueError('scalar mutation accepted')
   f.write_text('inert')
 check("negative_env.pop('ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256',None)"in code,'binding removed for binary64')
 check("negative_env['ATLAS_NUMERICAL_FIXTURES']='md1997-source-admissible-current17-v1'"in code,'closed negative selector')
 check(code.index('negative_code=run_process')<code.index('code=run_process(argv,str(build),env'),'negative actual invocation before positive')
 check("type(negative_code)is int and negative_code==1"in code,'exact negative integer1')
 check(r"b'MD AD/FD residual Jacobian mismatch\n'"in code and r"models=17\n'"in code,'exact binary64 raw contracts')
 check("write(output/'binary64-process.json',negative)"in code,'negative raw process retained')
 # Replay author pure mocks in owned namespace only. Its subprocess hook is replaced before run.
 # Source copied verbatim except owned output directory; no author evidence is overwritten.
 fixture=(A/'check_source.py').read_text();fixture=fixture.replace("P=Path(__file__).absolute().parent;SOURCE=", "P=Path("+repr(str(O))+ ");SOURCE=",1)
 exec(compile(fixture,str(A/'check_source.py'),'exec'),{'__file__':str(A/'check_source.py'),'__name__':'independent_saved_mock_replay'})
 replay=json.loads((O/'checks.json').read_text());check(replay['assertions']==34 and replay['refusals']==24 and replay['actual_compiled_calls']==0,'all frozen source/mock cases reproduced')
 (O/'mock-replay.json').write_text(json.dumps(replay,indent=2)+'\n')
 out={'identity':'independent-direct-ci-successor-checks-v2','passed':True,'independent_assertions':count,'independent_scalar_refusals':refusals,'supplemental_mock_replay':replay,'closed_blockers':['B1','B2'],'compiled_calls':0,'temporary_fixtures_cleaned':True,'actual_CI_observation':False}
 (O/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'independent_assertions':count,'mock_assertions':34,'mock_refusals':24}))
if __name__=='__main__':main()
