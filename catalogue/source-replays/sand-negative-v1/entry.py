"""Re-audit original compiled observations; never execute compiled artifacts."""
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT
STUDY=ROOT/'catalogue/investigations/barodesy2015-rates-v1'
spec=importlib.util.spec_from_file_location('original_sand_negative_tests',ROOT/'tests/test_barodesy2015_rate_evidence.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromModule(module).run(result)
if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
if result.testsRun!=6:raise ValueError('original test completeness')
with tempfile.TemporaryDirectory(prefix='atlas-original-comparison-')as tmp:
 output=Path(tmp)/'comparison.json'
 argv=[sys.executable,'-B','-m','tools.research_rate_parity','--protocol',str(STUDY/'protocol.json'),'--output',str(output)]
 for backend in ('native','wasm'):
  for kind,suffix in [('build','build'),('observation','observation'),('transport','observation.transport')]:
   argv+=['--'+backend+'-'+kind,str(STUDY/(backend+'-'+suffix+'.json'))]
 observed=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=30)
 if observed.returncode!=1 or observed.stdout!='failed\n' or observed.stderr:raise ValueError('original negative CLI status changed: '+repr(observed))
 actual=json.loads(output.read_bytes());expected=json.loads((STUDY/'comparison.json').read_bytes())
 if actual!=expected:raise ValueError('original complete failed comparison changed')
 if actual['outcome']!='failed' or actual['parity']['both_independent_assessments_passed']:raise ValueError('negative evidence relabelled')
print(json.dumps({'original_tests':6,'original_cli_exit':1,'original_complete_comparison_exact':True,'outcome':'failed','parity_passed':actual['parity']['passed'],'failed_case':'valid:audit-trace-cancellation','failed_component':6,'compiled_execution':False,'admission':False},sort_keys=True))
