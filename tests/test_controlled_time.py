import unittest,json,math,tempfile,hashlib
from copy import deepcopy
from dataclasses import asdict,replace
from fractions import Fraction as F
from pathlib import Path
from atlas.model import ROOT,load,validate,interpret
from atlas.dsl import ValidationError
from atlas.controlled_time import *
FIXTURE=ROOT/'tests/fixtures/controlled-time/transport.json'
def model():return load(FIXTURE)
def controls():return dict(strain=[0.]*6,temperature=300.,suction=200000.)
def context(m):return initialize(m,dict(sigma=[10000,20000,30000,4000,-5000,6000],clock_memory=-3.5,e=.8,memory=2.),11.,controls(),dict(strain=[.0001,-.0002,.0003,.0004,-.0005,.0006],temperature=2.,suction=-300.),{n:f['default'] for n,f in m['parameters'].items()})
def endpoint():return dict(strain=[.001,-.0003,.0002,.0004,-.0005,.0006],temperature=330.,suction=350000.)
class ControlledTimeTests(unittest.TestCase):
 def test_exact_transport_clock_and_fullstate(self):
  m=model();p=context(m);before=deepcopy(asdict(p));r=advance(m,p,4,p.controls,endpoint(),Settings(relative_tolerance=1e-10));s=r.context.state
  extra=F(3,10)*150000+100*30+F(7)*4*F(630,600)
  for i,(a,de) in enumerate(zip(p.state['sigma'],endpoint()['strain'])):self.assertLessEqual(abs(s['sigma'][i]-float(F(a)+2000000*F(str(de))+(extra if i<3 else 0))),1e-7+1e-12*abs(s['sigma'][i]))
  self.assertAlmostEqual(s['clock_memory'],9.5,places=10);self.assertLess(abs(s['memory']-2*math.exp(-2)),1e-8+2e-7*2*math.exp(-2))
  self.assertLess(abs(s['e']-(1.8*math.exp(-.0009)-1)),1e-8)
  self.assertEqual(r.context.time,15);self.assertEqual(r.context.controls,endpoint());self.assertEqual(asdict(p),before)
  for partitions in [2,4]:
   q=p
   for i in range(1,partitions+1):v,_=stage_controls(m,p.controls,endpoint(),4,i/partitions);q=advance(m,q,4/partitions,q.controls,v).context
   self.assertAlmostEqual(q.state['clock_memory'],9.5,places=10)
   for a,b in zip(q.state['sigma'],s['sigma']):self.assertLess(abs(a-b),1e-6)
   self.assertEqual(context_from_dict(m,asdict(q)),q)
 def test_hold_and_stage_time(self):
  m=model();p=context(m);r=advance(m,p,4,p.controls,p.controls)
  self.assertEqual(r.context.control_rates,dict(strain=[0.]*6,suction=0.,temperature=0.))
  for i,v in enumerate(r.context.state['sigma']):self.assertAlmostEqual(v,p.state['sigma'][i]+(28 if i<3 else 0),places=8)
  for dt,expected in [(0,11/4),(2,13/4),(4,15/4)]:self.assertEqual(evaluate_stage(m,p.state,p.parameters,11+dt,p.controls,p.control_rates)[0]['clock_memory'],expected)
  mid=advance(m,p,2,p.controls,p.controls).context;self.assertAlmostEqual(mid.state['clock_memory'],2.5,places=10)
  self.assertAlmostEqual(advance(m,mid,2,mid.controls,mid.controls).context.state['clock_memory'],9.5,places=10)
 def test_each_component_and_fields(self):
  m=model();p=context(m)
  for i in range(6):
   end=controls();end['strain'][i]=.0007;r=advance(m,p,1,p.controls,end)
   for j,v in enumerate(r.context.state['sigma']):self.assertAlmostEqual(v-p.state['sigma'][j],(1400 if i==j else 0)+(7 if j<3 else 0),places=7)
  for key,val in [('suction',100000.),('temperature',270.)]:
   end=controls();end[key]=val;r=advance(m,p,2,p.controls,end)
   extra=.3*(val-200000) if key=='suction' else 100*(val-300)
   extra+=7*2*((300+val)/600 if key=='temperature' else 1)
   for j,v in enumerate(r.context.state['sigma']):self.assertAlmostEqual(v-p.state['sigma'][j],extra if j<3 else 0,places=7)
 def test_reject_mutated_contracts(self):
  mutators=[lambda m:m['formulation']['inputs']['equation']['suction_rate'].update(unit='Pa'),lambda m:m['formulation']['controls']['strain'].update(shape='scalar'),lambda m:m['formulation']['inputs']['equation']['suction_rate']['binding'].update(derivative_order=0),lambda m:m['formulation']['inputs']['equation']['suction_rate']['binding'].update(control='missing'),lambda m:m['formulation'].update(equation_form='path_ode'),lambda m:m['equations'].update(clock_memory='time/tau'),lambda m:m['equations'].update(clock_memory='clock_memory_n/tau'),lambda m:m['state'][1]['semantics'].update(role='increment_unknown')]
  for mutate in mutators:
   with self.subTest(mutation=mutate):
    m=model();mutate(m)
    with self.assertRaises(ValueError):validate(m)
 def test_bounds(self):
  m=model()
  for i in range(24):m['formulation']['controls']['field'+str(i)]={'quantity':'field','shape':'scalar','unit':'1','constraint':'finite'}
  validate(m) # 6+2+24=32; controls can be required even when no equation input uses them.
  m['formulation']['controls']['over']={'quantity':'field','shape':'scalar','unit':'1','constraint':'finite'}
  with self.assertRaisesRegex(ValueError,'32 control'):validate(m)
  m=model()
  for i in range(23):m['state'].append(dict(name='history'+str(i),shape='scalar',unit='1',initial=0,scale='one',semantics=dict(role='persistent',quantity='synthetic',transformation='scalar_invariant')));m['equations']['history'+str(i)]='one/tau';m['initialization']['required_state'].append('history'+str(i))
  validate(m)
  m['state'].append(deepcopy(m['state'][-1]));m['state'][-1]['name']='overflow';m['equations']['overflow']='one/tau';m['initialization']['required_state'].append('overflow')
  with self.assertRaisesRegex(ValueError,'32 state'):validate(m)
 def test_exact_all_capacity_bounds(self):
  m=load(ROOT/'tests/fixtures/controlled-time/capacity-max.json')
  self.assertEqual((len(m['parameters']),sum(size(f) for f in m['formulation']['controls'].values()),sum(size(f) for f in m['formulation']['inputs']['equation'].values()),sum(size(f) for f in m['state']),len(m['observables']),sum(size(f) for f in m['observables'])),(256,32,65,32,24,144))
  params={n:f['default'] for n,f in m['parameters'].items()};state={f['name']:f['initial'] for f in m['state']};values={f['name']:([0.]*6 if f['shape']=='sym' else 0.) for f in control_fields(m)};values.update(temperature=300.,suction=200000.);rates={f['name']:([0.]*6 if f['shape']=='sym' else 0.) for f in control_fields(m)};rates['field23']=.0625
  rr,oo,_=evaluate_stage(m,state,params,11,values,rates);self.assertEqual(rr['history22'],124.5625);self.assertEqual(len(oo),24)
  for key,mutate in [('parameters',lambda x:x['parameters'].update(overflow=dict(default=1,min=0,max=2,unit='1'))),('inputs',lambda x:x['formulation']['inputs']['equation'].update(overflow=dict(quantity='field',shape='scalar',unit='1',sampling='stage',constraint='finite',binding=dict(control='field0',derivative_order=0)))),('observables',lambda x:x['observables'].append(dict(name='overflow',shape='sym',unit='Pa',scale='E',expr='sigma')))]:
   bad=deepcopy(m);mutate(bad)
   with self.subTest(bound=key),self.assertRaises(ValueError):validate(bad)
  from atlas.controlled_time_compiler import generate
  with tempfile.TemporaryDirectory() as d:
   generate(d,[ROOT/'tests/fixtures/controlled-time/capacity-max.json']);row=json.loads((Path(d)/'controlled_time_catalogue.json').read_text())['models'][0];self.assertEqual(row['state'][-1]['offset'],31);self.assertEqual(row['observables'][-1]['offset'],138)
 def test_transaction_recovery_restart_rates(self):
  m=model();p=context(m);before=asdict(p);expected=advance(m,p,1,p.controls,p.controls)
  bads=[(0,p.controls,Settings()),(-1,p.controls,Settings()),(float('nan'),p.controls,Settings()),(1,{**p.controls,'temperature':0},Settings()),(1,{**p.controls,'suction':-1},Settings()),(4,endpoint(),Settings(maximum_trials=1)),(4,endpoint(),Settings(maximum_depth=1,maximum_step_seconds=.001))]
  for duration,end,setting in bads:
   with self.subTest(duration=duration,end=end):
    with self.assertRaises(ValueError):advance(m,p,duration,p.controls,end,setting)
    self.assertEqual(asdict(p),before);self.assertEqual(advance(m,p,1,p.controls,p.controls),expected)
  with self.assertRaises(ValueError):advance(m,p,1,{**p.controls,'suction':1},p.controls)
  bad=asdict(p);bad.pop('control_rates')
  with self.assertRaises(ValueError):context_from_dict(m,bad)
  bad=asdict(p);bad['model_sha256']='0'*64
  with self.assertRaises(ValueError):context_from_dict(m,bad)
 def test_rate_jump_and_initial_checks_only_once(self):
  m=model();m['observables'][0]['expr']='sigma+E*tau*strain_rate';m['initial_checks']=['time < 12*tau'];p=context(m)
  r=advance(m,p,4,p.controls,endpoint());self.assertNotEqual(r.left_observables,r.right_observables);self.assertEqual(p.state,context(m).state)
  m['initial_checks']=['time < 6*tau'];p=context(m);q=advance(m,p,4,p.controls,p.controls).context
  # Restart/continuation after preparation-only time criterion ceased to hold.
  self.assertEqual(context_from_dict(m,asdict(q)),q);advance(m,q,1,q.controls,q.controls)
 def test_old_routes_reject(self):
  from atlas.initialization import initialize_state,validate_recipe
  from atlas.path import initialize as path_initialize
  from atlas.compiler import generate
  m=model();p=context(m)
  with self.assertRaisesRegex(ValueError,'controlled-time'):interpret(m,p.state,None,[0]*6,p.parameters,time=11)
  with self.assertRaisesRegex(ValueError,'controlled-time'):initialize_state(m,p.state,p.parameters,loading=[0]*6,time=11)
  with self.assertRaisesRegex(ValueError,'controlled-time'):path_initialize(m,p.state,0,p.controls,p.parameters)
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'controlled-time'):generate(d,[FIXTURE,ROOT/'models/linear-elastic.json'])
  old=load(ROOT/'tests/fixtures/time/maxwell.json');from atlas.model import migrate_formulation
  old=migrate_formulation(old,stress_scope='total');old['formulation']['stress']['scope']='net'
  with self.assertRaises(ValueError):validate(old)
  from atlas.stress import stress_binding
  with self.assertRaises(ValueError):stress_binding(old)
  self.assertEqual(stress_binding(m)['scope'],'net')
 def test_nonlinear_refinement(self):
  m=model();p=context(m);errors=[]
  for h in [1,.5,.25]:
   r=advance(m,p,4,p.controls,p.controls,Settings(absolute_scale_fraction=1e-6,relative_tolerance=1e-2,maximum_step_seconds=h));errors.append(abs(r.context.state['memory']-2*math.exp(-2)))
  self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2]);self.assertTrue(3<errors[1]/errors[2]<5,errors)
 def test_directional_branch_and_late_domain_rollback(self):
  m=model();m['equations']['clock_memory']='select(suction_rate > 0*C, 2/tau, select(suction_rate < 0*C, -4/tau, 0/tau))'
  # C has pressure/time units, so 0*C is the correctly dimensioned zero pressure rate.
  p=context(m)
  for end,expected in [(350000,.5),(100000,-11.5),(200000,-3.5)]:
   q=advance(m,p,4,p.controls,{**p.controls,'suction':end}).context;self.assertAlmostEqual(q.state['clock_memory'],expected,places=10)
  m=model();m['domain'].append('time < 14*tau/2');p=context(m);before=asdict(p)
  with self.assertRaises(ValueError):advance(m,p,4,p.controls,p.controls,Settings(maximum_depth=8))
  self.assertEqual(asdict(p),before)
  q=advance(m,p,2,p.controls,p.controls).context;self.assertEqual(q.time,13)
 def test_generated_layout_and_old_bytes(self):
  from atlas.controlled_time_compiler import generate
  from atlas.compiler import generate as ordinary
  with tempfile.TemporaryDirectory() as d:
   generate(d,[FIXTURE]);c=json.loads((Path(d)/'controlled_time_catalogue.json').read_text());row=c['models'][0]
   self.assertEqual(c['profile'],PROFILE);self.assertEqual([(f['name'],f['offset'],f['size']) for f in row['controls']],[('strain',0,6),('suction',6,1),('temperature',7,1)])
   code=(Path(d)/'controlled_time_api.cpp').read_text();self.assertIn('controlled_time_advance',code);self.assertIn('disjoint',code);self.assertNotIn('extern "C" int path_advance',code)
   with self.assertRaises(ValueError):generate(d,[ROOT/'models/linear-elastic.json'])
  baseline=ROOT/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/baseline'
  with tempfile.TemporaryDirectory() as d:
   ordinary(d)
   for r in json.loads((baseline/'manifest.json').read_text()):self.assertEqual(hashlib.sha256((Path(d)/Path(r['path']).name).read_bytes()).hexdigest(),r['sha256'])
 def test_native_loader_rejects_stale_same_shape_identity(self):
  from unittest.mock import patch
  from atlas.controlled_time_compiler import generate
  from atlas.controlled_time_native import NativeEngine
  class Fake:
   pass
  with tempfile.TemporaryDirectory() as d:
   generate(d,[FIXTURE]);catalogue=json.loads((Path(d)/'controlled_time_catalogue.json').read_text());fake=Fake();fake.controlled_time_model_hash=lambda index:b'0'*64;fake.controlled_time_catalogue_hash=lambda:catalogue['catalogue_sha256'].encode();fake.controlled_time_catalogue_file_hash=lambda:hashlib.sha256((Path(d)/'controlled_time_catalogue.json').read_bytes()).hexdigest().encode()
   with patch('atlas.controlled_time_native.C.CDLL',return_value=fake):
    with self.assertRaisesRegex(ValueError,'compiled model/catalogue identity'):NativeEngine(FIXTURE,Path(d)/'controlled_time_catalogue.json',model())
 def test_complete_run_and_tamper(self):
  m=model();p=context(m);spec=dict(profile=PROFILE,model=m['id'],context=asdict(p),settings=asdict(Settings()),segments=[dict(id='mixed',duration=4,samples=2,controls_end=endpoint())])
  before=deepcopy(spec);r=run(m,spec);self.assertEqual(spec,before);self.assertEqual(run(m,json.loads(json.dumps(spec))),r)
  self.assertEqual(r['points'][0]['side'],'left');self.assertEqual(r['points'][1]['side'],'right');self.assertEqual(r['context']['time'],15)
  bad=deepcopy(spec);bad['segments'][0]['samples']=1.5
  with self.assertRaises(ValueError):run(m,bad)
  bad=deepcopy(spec);bad['segments'].append(dict(id='latefail',duration=1,samples=1,controls_end={**endpoint(),'temperature':-10}))
  with self.assertRaises(ValueError):run(m,bad)
  self.assertEqual(spec,before)
if __name__=='__main__':unittest.main()
