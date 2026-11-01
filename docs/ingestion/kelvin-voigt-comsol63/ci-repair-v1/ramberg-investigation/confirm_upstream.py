"""Run exact committed upstream test in isolation; no root test mutation."""
from pathlib import Path
import importlib.util,sys,unittest
B=Path(__file__).resolve().parent;ROOT=B.parents[4];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('upstream_ramberg_test',B/'upstream-test_ramberg_osgood.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from tests import test_historical_generation
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(module),unittest.defaultTestLoader.loadTestsFromModule(test_historical_generation)])
raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
