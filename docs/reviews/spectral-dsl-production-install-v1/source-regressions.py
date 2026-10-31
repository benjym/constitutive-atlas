import sys,importlib.util,unittest,os,json
from pathlib import Path
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root));os.environ.pop('ATLAS_RESEARCH_SOLVER',None);os.environ['PYTHONDONTWRITEBYTECODE']='1'
suite=unittest.TestSuite()
for name in ('test_atlas','test_history','test_initialization','test_formulation','test_expression_finiteness','test_spectral_dsl'):
 spec=importlib.util.spec_from_file_location('installed_'+name,root/'tests'/f'{name}.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(module.LanguageTests)if name=='test_atlas'else unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
Path('/private/tmp/atlas-spectral-installed-regressions-v1.json').write_text(json.dumps({'run':result.testsRun,'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),'compiled_observations':0,'passed':result.wasSuccessful()},indent=2)+'\n')
raise SystemExit(not result.wasSuccessful())
