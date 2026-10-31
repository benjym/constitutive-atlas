"""Frozen project adapter: original source verifier/report and original unit groups."""
import hashlib,json,sys,unittest
from pathlib import Path
from atlas.model import ROOT
FOLDER=ROOT/'docs/ingestion/hypoplastic-clay-2005/rate-study-v2'
sys.path.insert(0,str(FOLDER))
import check_study
actual=check_study.assess(ROOT)
expected=json.loads((FOLDER/'checks.json').read_text())
if actual!=expected:raise ValueError('original complete source report changed')
suite=unittest.defaultTestLoader.discover(str(FOLDER),pattern='test_*.py')
result=unittest.TestResult();suite.run(result)
if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
if result.testsRun!=18:raise ValueError('original test group completeness')
print(json.dumps({'id': 'clay', 'original_report_sha256':hashlib.sha256((FOLDER/'checks.json').read_bytes()).hexdigest(),'original_report_exact':True,'original_python_groups':result.testsRun,'compiled_execution':False,'admission':False},sort_keys=True))
