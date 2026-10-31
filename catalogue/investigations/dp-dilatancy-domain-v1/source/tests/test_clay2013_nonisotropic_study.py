import copy,unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch
from tools.clay2013_nonisotropic_study import run
from atlas.model import load
from tools.clay2013_integration_study import MODEL_PATH,request,TOLERANCES
from tools.clay2013_path_reference import study
from tools.clay2013_nonisotropic_study import assess,digest,checked_cases

def synthetic(model,ref):
 records=[]
 for case in ref['cases']:
  c=case['input'];scale=sum(c['initial'][:3])/3
  for tol in TOLERANCES:
   initial=c['initial'][:];calls=[]
   for j,strain in enumerate(c['increments'],1):
    r=request(model,initial,strain,tol,stress_scale=scale)
    z=case['grids'][-1]['trajectory'][j]['state'][:];z[0]+={1e-4:.1,1e-6:.01,1e-8:.001}[tol]
    settings=dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
    a=dict(ok=True,**{k:copy.deepcopy(r[k])for k in ('model','parameters','initial','strain')},state=z,catalogue_hash=digest([model]),integration_settings=settings,diagnostics=dict(iterations=0,substeps=2,rejected=0,error=tol/2,increment_fractions=[.5,.5]))
    calls.append(dict(request=r,response=a));initial=z[:]
   records.append(dict(case=c['id'],tolerance=tol,calls=calls))
 return records
class ComparisonContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.model=load(MODEL_PATH);cls.ref=study();cls.records=synthetic(cls.model,cls.ref)
 def check(self,records):return assess(records,self.model,self.ref)
 def test_complete_synthetic_matrix(self):self.assertEqual(len(self.check(self.records)),12)
 def test_missing_duplicate_and_segment_order(self):
  for mutate in [lambda x:x.pop(),lambda x:x.append(copy.deepcopy(x[0])),lambda x:x[0]['calls'].reverse(),lambda x:x[0]['calls'].pop()]:
   x=copy.deepcopy(self.records);mutate(x)
   with self.assertRaises(ValueError):self.check(x)
 def test_corrupt_request_echo_settings_and_catalogue(self):
  for target,key in [('request','initial'),('request','parameters'),('request','strain'),('request','settings'),('response','initial'),('response','parameters'),('response','strain')]:
   x=copy.deepcopy(self.records);x[0]['calls'][0][target][key][0]+=1
   with self.subTest(target=target,key=key),self.assertRaises(ValueError):self.check(x)
  for key,value in [('catalogue_hash','x'),('integration_settings',{}),('ok',False)]:
   x=copy.deepcopy(self.records);x[0]['calls'][0]['response'][key]=value
   with self.assertRaises(ValueError):self.check(x)
 def test_corrupt_all_state_channels_and_nonfinite(self):
  for channel in range(7):
   x=copy.deepcopy(self.records);x[0]['calls'][0]['response']['state'][channel]+=1000
   with self.subTest(channel=channel),self.assertRaises(ValueError):self.check(x)
  for bad in (float('nan'),float('inf'),True):
   x=copy.deepcopy(self.records);x[0]['calls'][0]['response']['state'][0]=bad
   with self.assertRaises(ValueError):self.check(x)
 def test_corrupt_diagnostics_and_unrefined_matrix(self):
  for key,value in [('substeps',True),('error',float('nan')),('increment_fractions',[.4,.4])]:
   x=copy.deepcopy(self.records);x[0]['calls'][0]['response']['diagnostics'][key]=value
   with self.assertRaises(ValueError):self.check(x)
  x=copy.deepcopy(self.records)
  # Keep requests/chaining valid but reverse the prescribed error refinement.
  for g in x:
   for j,c in enumerate(g['calls']):
    if j:c['request']['initial']=g['calls'][j-1]['response']['state'][:];c['response']['initial']=c['request']['initial'][:]
    ref=next(z for z in self.ref['cases']if z['input']['id']==g['case'])
    c['response']['state'][0]=ref['grids'][-1]['trajectory'][j+1]['state'][0]+{1e-4:.001,1e-6:.01,1e-8:.1}[g['tolerance']]
  with self.assertRaises(ValueError):self.check(x)
 def test_raw_records_retained_before_assessment(self):
  responses=[copy.deepcopy(c['response'])for g in self.records for c in g['calls']]
  with tempfile.TemporaryDirectory()as folder:
   raw=Path(folder)/'raw.json'
   with patch('tools.clay2013_nonisotropic_study.native_call',side_effect=responses),patch('tools.clay2013_nonisotropic_study.assess',side_effect=ValueError('deliberate assessment failure')):
    with self.assertRaisesRegex(ValueError,'deliberate'):run(Path('no-native-execution'),raw,self.ref)
   saved=json.loads(raw.read_text());self.assertEqual(len(saved),12);self.assertEqual(sum(len(g['calls'])for g in saved),36)
 def test_reference_parameter_mismatch(self):
  m=copy.deepcopy(self.model);m['parameters']['nu']['default']=.3
  with self.assertRaisesRegex(ValueError,'parameter mismatch'):assess(self.records,m,self.ref)
class StrictReplayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.reference=study()
 def rejection(self,mutate):
  r=copy.deepcopy(self.reference);mutate(r)
  with self.assertRaises(ValueError):checked_cases(r)
 def test_fresh_reference_accepts(self):self.assertEqual(len(checked_cases(self.reference)),4)
 def test_five_retained_counterexamples_reject(self):
  mutations=[lambda r:r.update(source_sha256='0'*64),lambda r:r.update(dependency_sha256={'bogus':'0'*64}),lambda r:r['cases'][0]['grids'][0]['trajectory'][0]['state'].__setitem__(0,1234567.),lambda r:r['cases'][0]['fine_difference'].__setitem__('stress',float('nan')),lambda r:r['cases'][0]['grids'][-1]['trajectory'][3]['state'].__setitem__(0,r['cases'][0]['grids'][-1]['trajectory'][3]['state'][0]+1e-4)]
  for i,mutate in enumerate(mutations):
   with self.subTest(case=i):self.rejection(mutate)
 def test_metadata_and_type_identity_reject(self):
  for key,value in [('basis','Voigt'),('zero_spin',False),('zero_spin',1),('resolutions',[8,16,64]),('rotation',[]),('contract','other'),('scope','overclaim')]:
   with self.subTest(key=key,value=value):self.rejection(lambda r:r.update({key:value}))
 def test_derived_convergence_and_covariance_cannot_be_forged(self):
  for key in ('coarse_difference','fine_difference','refinement_ratio','richardson_estimate'):
   with self.subTest(key=key):self.rejection(lambda r:r['cases'][0][key].__setitem__('stress',.123))
  self.rejection(lambda r:r['covariance'][0]['difference'].__setitem__('stress',1.))
 def test_nonfinite_and_extra_fields_reject(self):
  self.rejection(lambda r:r['cases'][0]['grids'][0]['trajectory'][0]['state'].__setitem__(0,float('inf')))
  self.rejection(lambda r:r.update(unknown=True))


if __name__=='__main__':unittest.main()
