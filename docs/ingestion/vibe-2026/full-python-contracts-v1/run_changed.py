"""All changed pure contracts, with all external execution forbidden."""
import unittest
from unittest.mock import patch
from run_six import NAMES
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromNames(NAMES),unittest.defaultTestLoader.loadTestsFromName('tests.test_catalogue.CatalogueTests'),unittest.defaultTestLoader.loadTestsFromName('tests.test_controlled_time.ControlledTimeTests.test_historical_baseline_context_fails_closed')])
with patch('subprocess.run',side_effect=AssertionError('No material/build execution authorized')):result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
