"""Original finite-study audit groups; no collector or compiled execution."""
import importlib,json,subprocess,unittest
from unittest.mock import patch
from atlas.model import ROOT
GROUPS={'barodesy-isotropic': ['test_barodesy2017_integration_study', 'test_barodesy2017_finite_diagnostics', 'test_barodesy2017_integration_evidence'], 'barodesy-wider': ['test_barodesy2017_wider_study', 'test_barodesy2017_wider_parity_review', 'test_barodesy2017_wider_evidence'], 'clay-original-failed': ['test_clay2014_path_study', 'test_clay2014_path_raw_parity', 'test_clay2014_path_negative_diagnosis'], 'clay-controlled': ['test_clay2014_controlled_study', 'test_clay2014_controlled_evidence']}
results=[]
with patch.object(subprocess,'Popen',side_effect=AssertionError('compiled or external execution forbidden in finite replay')):
 for name,modules in GROUPS.items():
  suite=unittest.TestSuite()
  for module in modules:suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module('tests.'+module)))
  result=unittest.TestResult();suite.run(result)
  if result.errors or result.failures:raise ValueError(name+':'+repr(result.errors+result.failures))
  if result.skipped or result.expectedFailures or result.unexpectedSuccesses:raise ValueError('original assertions skipped or reclassified')
  results.append({'family':name,'original_groups':result.testsRun,'original_assertions_passed':True})
paths=ROOT/'catalogue/investigations'
original=json.loads((paths/'clay2014-paths-v1/manifest.json').read_bytes())
controlled=json.loads((paths/'clay2014-controlled-resolution-v1/manifest.json').read_bytes())
if original['outcome']!='failed' or controlled['outcome']!='passed' or controlled['original_failed_study_replaced']:raise ValueError('historical outcomes relabelled')
print(json.dumps({'families':results,'clay_original_outcome':'failed','clay_controlled_outcome':'passed','original_failed_study_replaced':False,'compiled_execution':False,'admission':False},sort_keys=True))
