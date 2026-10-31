"""Three unchanged original source review suites and complete original results."""
import hashlib,importlib,importlib.util,json,subprocess,sys,unittest
from unittest.mock import patch
from atlas.model import ROOT
FAMILIES=[("sand-v1","docs/ingestion/barodesy-sand/rate-review-v1","audit","test_review.py","findings.json",3),("clay-v1","docs/ingestion/hypoplastic-clay-2005/rate-review-v1","probe","test_audit.py","evidence.json",4),("clay-guard-v2","docs/ingestion/hypoplastic-clay-2005/guard-review-v2","audit","test_audit.py","results.json",4)]
results=[]
with patch.object(subprocess,"Popen",side_effect=AssertionError("external execution forbidden in reviews replay")):
 for name,relative,helper,testfile,report,count in FAMILIES:
  # Original packet-local modules have shared names. Each family gets its own
  # explicit search path and newly imported local modules; atlas remains frozen.
  for module in ("audit","probe","reference","check","check_study","support","test_audit","test_review"):
   sys.modules.pop(module,None)
  sys.path[:]=[p for p in sys.path if "/docs/ingestion/"not in p]
  folder=ROOT/relative;sys.path.insert(0,str(folder))
  api=importlib.import_module(helper)
  if api.run(ROOT)!=json.loads((folder/report).read_bytes()):raise ValueError("complete original report changed:"+name)
  spec=importlib.util.spec_from_file_location("original_"+name.replace("-","_"),folder/testfile)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  suite=unittest.defaultTestLoader.loadTestsFromModule(module)
  result=unittest.TestResult();suite.run(result)
  if result.errors or result.failures:raise ValueError(name+":"+repr(result.errors+result.failures))
  if result.testsRun!=count or result.skipped or result.expectedFailures or result.unexpectedSuccesses:raise ValueError("original review assertions incomplete or reclassified:"+name)
  results.append({"family":name,"original_groups":count,"original_result_exact":True,"original_result_sha256":hashlib.sha256((folder/report).read_bytes()).hexdigest()})
print(json.dumps({"families":results,"original_groups":11,"compiled_execution":False,"admission":False},sort_keys=True))
