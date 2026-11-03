"""Reproduce six pure failures without permitting subprocess/material execution."""
import unittest
from unittest.mock import patch
NAMES=['tests.test_tresca_certified_corners.TrescaCertifiedCornerTests.test_all_original_saved_gates_without_material_execution','tests.test_tresca_mixed_catalogue.MixedCatalogueTests.test_complete_saved_gate_without_build_or_material_execution','tests.test_tresca_solution_constraints.TrescaSolutionConstraintTests.test_complete_saved_gates_and_generic_failure_checks','tests.test_catalogue.CatalogueTests.test_database_keeps_candidate_and_executable_sources','tests.test_catalogue.CatalogueTests.test_directory_coverage_has_resolvable_provenance','tests.test_controlled_time.ControlledTimeTests.test_generated_layout_and_old_bytes']
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromNames(NAMES)
 with patch('subprocess.run',side_effect=AssertionError('No material/build execution authorized')):result=unittest.TextTestRunner(verbosity=2).run(suite)
 raise SystemExit(not result.wasSuccessful())
