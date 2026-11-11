"""Run the current controlled-time contracts without the two archival tests."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_controlled_time import ControlledTimeTests

historical = {'test_generated_layout_and_old_bytes', 'test_historical_baseline_context_fails_closed'}
tests = unittest.defaultTestLoader.getTestCaseNames(ControlledTimeTests)
if not historical.issubset(tests):
    raise RuntimeError('Controlled-time archival test names changed')
suite = unittest.TestSuite(ControlledTimeTests(name) for name in tests if name not in historical)
raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
