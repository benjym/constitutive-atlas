"""Run source/mock tests with process creation explicitly blocked."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import unittest
S=Path('/private/tmp/atlas-md1997-decimal-ci-v1/source');sys.path.insert(0,str(S))
def guard(event,args):
 if event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:raise RuntimeError('No process execution permitted by source/mock review')
sys.addaudithook(guard)
suite=unittest.TestLoader().loadTestsFromNames(['tests.test_native_fixture_dispatch','tests.test_native_fixture_contracts','tests.test_ci_profiles'])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
