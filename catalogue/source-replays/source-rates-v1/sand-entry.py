"""Frozen project adapter: original source verifier/report and original unit groups."""
import hashlib,json,sys,unittest
from pathlib import Path
from atlas.model import ROOT
FOLDER=ROOT/'docs/ingestion/barodesy-sand/rate-study-v2'
sys.path.insert(0,str(FOLDER))
import check
actual=check.run()
expected=json.loads((FOLDER/'python-report.json').read_text())
if actual!=expected:raise ValueError('original complete source report changed')
suite=unittest.defaultTestLoader.discover(str(FOLDER),pattern='test_*.py')
result=unittest.TestResult();suite.run(result)
if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
if result.testsRun!=11:raise ValueError('original test group completeness')
print(json.dumps({'id': 'sand', 'original_report_sha256':hashlib.sha256((FOLDER/'python-report.json').read_bytes()).hexdigest(),'original_report_exact':True,'original_python_groups':result.testsRun,'compiled_execution':False,'admission':False},sort_keys=True))
