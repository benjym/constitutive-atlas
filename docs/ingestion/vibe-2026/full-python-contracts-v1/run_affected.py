"""Bounded affected source/SQLite/saved-report suites; compiled calls forbidden."""
import unittest
from unittest.mock import patch
NAMES=['tests.test_catalogue','tests.test_controlled_time','tests.test_tresca_certified_corners','tests.test_tresca_mixed_catalogue','tests.test_tresca_solution_constraints','tests.test_historical_generation']
suite=unittest.defaultTestLoader.loadTestsFromNames(NAMES)
with patch('subprocess.run',side_effect=AssertionError('Build/material subprocess forbidden')),patch('ctypes.CDLL',side_effect=AssertionError('Compiled module forbidden')):result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
