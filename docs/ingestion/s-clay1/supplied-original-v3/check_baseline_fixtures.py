"""Run the existing unchanged baseline fixture assertions; retain requests/results."""
import os,sys,importlib.util,json,unittest,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];binary=R/'.local/s-clay1-delivery-v3/native/atlas_solver'
os.environ['ATLAS_SOLVER']=str(binary);sys.path.insert(0,str(R))
p=R/'tests/test_atlas.py';spec=importlib.util.spec_from_file_location('baseline_fixtures',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
oldrun=module.run;calls=[]
def run(model,**kwargs):
 r=oldrun(model,**kwargs);calls.append({'model':model,'kwargs':kwargs,'result':r});return r
module.run=run
names=['test_elastic_drained_closed_form','test_elastic_undrained_closed_form','test_elastic_isotropic_closed_form','test_elastic_oedometer_closed_form','test_mcc_yield_hardening_and_unloading']
suite=unittest.TestSuite(module.NumericalTests(n) for n in names);result=unittest.TextTestRunner(verbosity=2).run(suite)
(O/'baseline-fixture-calls.json').write_text(json.dumps(calls,indent=2)+'\n')
(O/'baseline-fixture-results.json').write_text(json.dumps({'ok':result.wasSuccessful(),'tests':names,'tests_run':result.testsRun,'calls':len(calls),'fixture_path':'tests/test_atlas.py','fixture_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'definition_hashes':{n:hashlib.sha256((R/'models'/f'{n}.json').read_bytes()).hexdigest() for n in ['linear-elastic','modified-cam-clay']},'frozen_fixture_manifest':'tests/fixtures/current-fifteen-ramberg-v1.json','scope':'Exact existing unittest analytical elasticity and MCC yield/hardening/unloading assertions, unchanged tolerances'},indent=2)+'\n')
assert result.wasSuccessful()
