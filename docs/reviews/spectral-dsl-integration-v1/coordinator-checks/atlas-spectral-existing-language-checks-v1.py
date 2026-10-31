import sys,unittest,importlib.util
sys.path.insert(0,'/private/tmp/atlas-spectral-dsl-candidate-v1')
spec=importlib.util.spec_from_file_location('atlas_existing_language','/Users/bmar5496/code/constitutive-atlas/tests/test_atlas.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.LanguageTests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
