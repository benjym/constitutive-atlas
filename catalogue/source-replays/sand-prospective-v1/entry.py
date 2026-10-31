"""Original prospective audit and mutation tests against original source pins."""
import json,os,sys,unittest
from atlas.model import ROOT
FOLDER=ROOT/'docs/ingestion/barodesy-sand/compiled-plan-review-v1'
sys.path.insert(0,str(FOLDER));os.environ['ATLAS_REVIEW_REPO']=str(ROOT)
import audit,test_audit
actual=audit.audit(ROOT)
if actual!=json.loads((FOLDER/'evidence.json').read_bytes()):raise ValueError('original prospective audit changed')
result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromModule(test_audit).run(result)
if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
if result.testsRun!=8:raise ValueError('original mutation-test completeness')
print(json.dumps({'original_prospective_audit_exact':True,'original_mutation_groups':8,'rows_per_backend':71,'compiled_execution':False,'admission':False},sort_keys=True))
