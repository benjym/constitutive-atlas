"""Explicit saved process stand-ins only; never execute fixture/tool binaries."""
import sys
sys.dont_write_bytecode=True
import json,shutil
from pathlib import Path
from unittest.mock import patch
S=Path('/private/tmp/atlas-md1997-decimal-ci-v1/source');sys.path.insert(0,str(S))
def guard(event,args):
 if event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:raise RuntimeError('No compiled/process execution permitted')
sys.addaudithook(guard)
from tests.test_native_fixture_dispatch import DispatchTests,dispatch
P=Path(__file__).resolve().parent
root=Path('/private/tmp/atlas-md1997-decimal-ci-v1/saved-synthetic-v1');root.mkdir(exist_ok=False)
t=DispatchTests();t.base=root/'context';t.base.mkdir();t.pinroot=root/'independent-pins';t.pinroot.mkdir();t.frozen={};t.calls=[]
source,build=t.fixture()
with patch.object(dispatch.shutil,'which',return_value=str(build/'mock-ctest')):
 t.execute(source,build,t.runner(source,'16'),'strict-eleven.json')
 t.calls=[]
 t.execute(source,build,t.direct_run(source,build),'direct.json','decimal')
 for suite in ['macos-main','linux-main']:
  t.execute(source,build,t.ctest_run(source,build,'16',suite),suite+'.json','ctest',suite)
 try:t.execute(source,build,t.direct_run(source,build,lambda x:x['cpp_checks'].update(rotation=False)),'rejected-export.json','decimal')
 except ValueError:pass
 else:raise AssertionError('corrupt export accepted')
out=P/'synthetic-evidence';out.mkdir(exist_ok=False)
for f in t.base.iterdir():
 if f.is_file():shutil.copyfile(f,out/f.name)
 elif f.name.endswith('-decimal'):shutil.copytree(f,out/f.name)
summary=dict(identity='explicit-mocked-process-capture-v1',purpose='synthetic-test-only',native_calls=0,spawned_processes=0,strict_negative_rows=11,positive_assessments=[588,588,588],corrupt_export_rejected=True,working_directory=str(root),note='All executables are nonexecuted text stand-ins. No native/CTest/scientific acceptance.')
(P/'synthetic-capture-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
