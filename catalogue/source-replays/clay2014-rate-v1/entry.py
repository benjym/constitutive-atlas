"""Unchanged original retained clay2014 rate audit; no binary execution."""
import json,subprocess,unittest
from unittest.mock import patch
from tests import test_clay2014_rate_evidence as original
suite=unittest.defaultTestLoader.loadTestsFromModule(original)
with patch.object(subprocess,'Popen',side_effect=AssertionError('external execution forbidden in rate replay')):
 result=unittest.TestResult();suite.run(result)
if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
if result.testsRun!=1 or result.skipped or result.expectedFailures or result.unexpectedSuccesses:raise ValueError('original assertions incomplete or reclassified')
print(json.dumps({'original_groups':1,'original_assertions_passed':True,'original_wasm_audit_negative_retained':True,'compiled_execution':False,'admission':False},sort_keys=True))
