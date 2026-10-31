from pathlib import Path
import sys,shutil,importlib.util,unittest,os
r=Path('/Users/bmar5496/code/constitutive-atlas');s=Path('/private/tmp/atlas-spectral-dsl-candidate-v1')
for name in ('fixtures','tests/fixtures','initialization'):
 shutil.copytree(r/name,s/name,dirs_exist_ok=True)
sys.path.insert(0,str(s));os.environ.pop('ATLAS_RESEARCH_SOLVER',None)
suite=unittest.TestSuite()
for name in ('test_atlas','test_history','test_initialization','test_formulation','test_expression_finiteness'):
 spec=importlib.util.spec_from_file_location('staged_'+name,r/'tests'/f'{name}.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(mod.LanguageTests)if name=='test_atlas'else unittest.defaultTestLoader.loadTestsFromModule(mod))
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
