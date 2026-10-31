"""Independent analytical checks of timed strain/stress controls and observables."""
import copy,json,math,os,subprocess,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT,load,observe,validate
from atlas.dsl import ValidationError
from atlas.schedule import validate_schedule,schedule_command

SOLVER=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))
FIXTURES=ROOT/'tests/fixtures/time'
def hold(quantity='strain'):return {'quantity':quantity,'kind':'hold'}
def rate(value,quantity='strain'):return {'quantity':quantity,'kind':'rate','value':value}
def segment(name,duration,controls,samples=4):return {'id':name,'duration':duration,'samples':samples,'controls':controls}
def spec(model,segments):return {'schema_version':'0.2','units':'SI','model':model,'start_time':0,'segments':segments,'solver':{'method':'backward-euler-step-doubling','relative_tolerance':1e-8,'absolute_scale_fraction':1e-11}}

class ScheduleContractTests(unittest.TestCase):
    def test_bad_controls_and_ambiguous_histories(self):
        valid=spec('test-maxwell',[segment('hold',1,[hold() for _ in range(6)])])
        changes=[lambda s:s['segments'][0].update(duration=0),lambda s:s['segments'][0]['controls'][0].update(value=1),lambda s:s['segments'][0]['controls'].pop(),lambda s:s.update(units='kPa'),lambda s:s['solver'].update(method='BDF'),lambda s:s['solver'].update(relative_tolerance=0)]
        for change in changes:
            bad=copy.deepcopy(valid);change(bad)
            with self.subTest(change=change),self.assertRaises(ValidationError):validate_schedule(bad)
        bad=copy.deepcopy(valid);bad['segments']*=2
        with self.assertRaises(ValidationError):validate_schedule(bad)
        bad=copy.deepcopy(valid);bad['start_time']=1e100
        with self.assertRaises(ValidationError):validate_schedule(bad)
    def test_observable_types_and_namespace(self):
        m=load(FIXTURES/'kelvin.json')
        wrong=copy.deepcopy(m);wrong['observables'][0]['unit']='1'
        with self.assertRaises(ValidationError):validate(wrong)
        wrong=copy.deepcopy(m);wrong['observables'][0]['shape']='scalar';wrong['observables'][0]['expr']='trace(sigma)'
        with self.assertRaises(ValidationError):validate(wrong)
        wrong=copy.deepcopy(m);wrong['equations']['sigma']='stress / tau'
        with self.assertRaises(ValidationError):validate(wrong)
        wrong=copy.deepcopy(m);wrong['observables'].append(copy.deepcopy(wrong['observables'][0]))
        with self.assertRaises(ValidationError):validate(wrong)
    def test_python_rate_dependent_output(self):
        m=load(FIXTURES/'kelvin.json');z={'sigma':m['state'][0]['initial']}
        out=observe(m,z,[.001,-.0005,-.0005,0,0,0],time=0)
        self.assertEqual(out['stress'].v,(148000,76000,76000,0,0,0))

@unittest.skipUnless(SOLVER.exists(),'schedule fixture solver has not been built')
class ScheduleNumericalTests(unittest.TestCase):
    def execute(self,specification,ok=True):
        r=subprocess.run(schedule_command(specification,SOLVER),capture_output=True,text=True,timeout=30)
        data=json.loads(r.stdout)
        for point in data.get('points',[]):
            self.assertLessEqual(point['nonlinear_residual_norm'],specification['solver'].get('nonlinear_tolerance',1e-10))
        self.assertEqual(data['ok'],ok,data.get('message'));self.assertEqual(r.returncode==0,ok)
        return data
    def test_maxwell_creep_solved_under_stress_hold(self):
        data=self.execute(spec('test-maxwell',[segment('creep',4,[hold('stress') for _ in range(6)])]))
        last=data['points'][-1]
        self.assertEqual(last['time'],4)
        self.assertAlmostEqual(last['strain'][0],40000/(2*12e6*2)*4,places=12)
        self.assertAlmostEqual(sum(last['strain'][:3]),0,places=12)
        for point in data['points']:
            for actual,wanted in zip(point['observables'],[140000,80000,80000,0,0,0]):self.assertAlmostEqual(actual,wanted,places=5)
        # Do not pretend that an unconstrained instantaneous boundary rate is known.
        self.assertEqual(data['points'][1]['strain_rate'],[None]*6)
    def test_relaxation_and_temporal_refinement(self):
        s=spec('test-maxwell',[segment('relax',4,[hold() for _ in range(6)])])
        fine=self.execute(s)['points'][-1]['state'][0];exact=100000+40000*math.exp(-2)
        self.assertLess(abs(fine-exact),2)
        s['solver']['relative_tolerance']=1e-4
        coarse=self.execute(s)['points'][-1]['state'][0]
        self.assertLess(abs(fine-exact),abs(coarse-exact))
    def test_rate_jump_changes_output_without_state_jump(self):
        s=spec('test-kelvin',[segment('load',1,[rate(.001),rate(-.0005),rate(-.0005),hold(),hold(),hold()]),segment('relax',2,[hold() for _ in range(6)])])
        data=self.execute(s);boundary=[p for p in data['points'] if p['time']==1]
        self.assertEqual(len(boundary),2);left,right=boundary
        self.assertEqual(left['side'],'left');self.assertEqual(right['side'],'right')
        self.assertEqual(left['state'],right['state']);self.assertEqual(left['strain'],right['strain'])
        self.assertAlmostEqual(left['observables'][0]-right['observables'][0],48000,places=5)
        self.assertEqual(data['points'][-1]['state'],right['state'])
    def test_kelvin_stress_ramp_and_creep(self):
        controls=[rate(40000,'stress'),rate(-20000,'stress'),rate(-20000,'stress')]+[hold('stress') for _ in range(3)]
        s=spec('test-kelvin',[segment('ramp',1,controls),segment('creep',2,[hold('stress') for _ in range(6)])])
        s['solver']['maximum_substeps']=100000  # strict BE refinement needs more than the default budget
        data=self.execute(s);last=data['points'][-1]
        tau=2;at_ramp_end=40000*(1-tau*(1-math.exp(-1/tau)))
        exact=40000+(at_ramp_end-40000)*math.exp(-2/tau)
        self.assertAlmostEqual(last['state'][0]-100000,exact,delta=3)
        self.assertAlmostEqual(last['strain'][0],exact/(2*12e6),delta=2e-7)
        self.assertAlmostEqual(last['observables'][0],140000,places=4)
        entry=[p for p in data['points'] if p['time']==1 and p['side']=='left'][0]
        self.assertGreater(last['strain'][0],entry['strain'][0])
    def test_mixed_control_and_target(self):
        controls=[{'quantity':'strain','kind':'target','value':.001},hold('stress'),hold('stress'),hold(),hold(),hold()]
        data=self.execute(spec('test-kelvin',[segment('drained',2,controls)]));last=data['points'][-1]
        self.assertAlmostEqual(last['strain'][0],.001,places=12)
        self.assertAlmostEqual(last['observables'][1],100000,places=4)
        self.assertAlmostEqual(last['observables'][2],100000,places=4)
    def test_sampling_preserves_history_and_restart(self):
        s=spec('test-maxwell',[segment('creep',4,[hold('stress') for _ in range(6)],samples=1)])
        a=self.execute(s);s['segments'][0]['samples']=8;b=self.execute(s)
        self.assertAlmostEqual(a['points'][-1]['strain'][0],b['points'][-1]['strain'][0],places=12)
        restart=spec('test-maxwell',[segment('continue',1,[hold('stress') for _ in range(6)])])
        end=a['points'][-1];restart.update(start_time=end['time'],initial=end['state'],initial_strain=end['strain'],initial_strain_rate=end['strain_rate'])
        c=self.execute(restart)
        self.assertAlmostEqual(c['points'][-1]['strain'][0],40000/(2*12e6*2)*5,places=12)
    def test_failure_retains_last_committed_sample(self):
        s=spec('test-maxwell',[segment('load',1,[hold('stress') for _ in range(6)],samples=4)])
        s['parameters']=[2e7,1.2e7,2,.6]
        data=self.execute(s,ok=False);last=data['points'][-1]
        self.assertEqual(last['time'],.5)
        self.assertEqual(last['state'],[140000,80000,80000,0,0,0])
        self.assertAlmostEqual(last['strain'][0],40000/(2*12e6*2)*.5,places=12)
    def test_substep_budget_failure_rolls_back_output_interval(self):
        s=spec('test-maxwell',[segment('relax',4,[hold() for _ in range(6)])])
        s['solver']['maximum_substeps']=2
        data=self.execute(s,ok=False)
        self.assertEqual(data['points'][-1]['time'],0)
        self.assertEqual(data['points'][-1]['state'],[140000,80000,80000,0,0,0])
    def test_json_cli_reproduces_direct_schedule(self):
        s=spec('test-maxwell',[segment('creep',1,[hold('stress') for _ in range(6)])])
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'spec.json';dest=Path(folder)/'result.json';source.write_text(json.dumps(s))
            r=subprocess.run(['python3','-m','atlas.cli','run',str(source),'--solver',str(SOLVER),'--output',str(dest)],cwd=ROOT,text=True,capture_output=True,timeout=30)
            self.assertEqual(r.returncode,0,r.stderr)
            result=json.loads(dest.read_text());self.assertEqual(result['specification'],s)
            self.assertEqual(result['points'],self.execute(s)['points'])
