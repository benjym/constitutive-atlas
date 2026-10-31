"""Source-reference comparisons and kinematic scope of the Terracotta draft."""
import copy,json,math,os,subprocess,unittest
from pathlib import Path
from atlas.model import ROOT,load,interpret,observe,validate
from atlas.dsl import Type,ValidationError,parse,infer,evaluate
from atlas.schedule import schedule_command

DEFINITION=ROOT/'models/research/terracotta-2024-fig1.json'
REFERENCE=ROOT/'tests/reference/terracotta-2024-author-rhs.json'
SOLVER=Path(os.environ.get('ATLAS_RESEARCH_SOLVER',ROOT/'build/atlas_research_solver'))
TIME_SOLVER=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))
def hold(q='strain'):return {'quantity':q,'kind':'hold'}
def rate(v,q='strain'):return {'quantity':q,'kind':'rate','value':v}
def make_spec(controls,duration=5):return {'schema_version':'0.2','units':'SI','model':'terracotta-2024-fig1','start_time':0,'segments':[{'id':'load','duration':duration,'samples':4,'controls':controls}], 'solver':{'method':'backward-euler-step-doubling','relative_tolerance':1e-6,'absolute_scale_fraction':1e-10,'maximum_substeps':100000}}
def controls_for(kind,value):
    if kind=='txu':return [rate(value),rate(-value/2),rate(-value/2)]+[hold() for _ in range(3)]
    if kind=='iso':return [rate(value) for _ in range(3)]+[hold() for _ in range(3)]
    if kind=='oed':return [rate(value)]+[hold() for _ in range(5)]
    return [hold() for _ in range(6)]
def reference_spec(case,rtol=1e-6):
    s=make_spec([]);s['segments']=[dict(id=f'stage-{i}',duration=stage['duration'],samples=4,controls=controls_for(stage['kind'],stage['rate'])) for i,stage in enumerate(case['stages'])]
    s['solver']['relative_tolerance']=rtol;return s

class TerracottaRepresentationTests(unittest.TestCase):
    def test_constructor_and_signed_work_conjugacy(self):
        expr=parse('sym(2/3,-1/3,-1/3,0,0,0)');self.assertEqual(infer(expr,{}),Type('sym'))
        from atlas.dsl import dot,Sym
        basis=evaluate(expr,{});D=Sym((-.002,.001,.001,0,0,0));self.assertAlmostEqual(dot(D,basis),-.002)
        for bad in ['sym(1,2)','sym(I,1,1,1,1,1)','sym(p,1,1,1,1,1)']:
            with self.subTest(bad=bad),self.assertRaises(ValidationError):infer(parse(bad),{'I':Type('sym'),'p':Type(dim=(1,-1,-2))})
    def test_initial_stress_units_and_temperature_production(self):
        m=load(DEFINITION);z={f['name']:f['initial'] for f in m['state']}
        self.assertAlmostEqual(observe(m,z,[0]*6,time=0)['pressure'],100000,places=8)
        self.assertEqual(m['parameters']['Gamma']['default'],.001)
        response=interpret(m,z,None,[2e-5,-1e-5,-1e-5,0,0,0],time=0)
        self.assertAlmostEqual(response['Tm'],6e5*(2e-5)**2,places=14)
        self.assertAlmostEqual(response['es_e'],2e-5,places=14)
        bad=copy.deepcopy(m);bad['state'][2]['scale']='Tm'
        with self.assertRaises(ValidationError):validate(bad)
    def test_interpreter_rejects_non_axisymmetric_rates(self):
        m=load(DEFINITION);z={f['name']:f['initial'] for f in m['state']}
        for D in [[0,1e-5,0,0,0,0],[0,0,0,1e-10,0,0]]:
            with self.assertRaises(ValueError):interpret(m,z,None,D,time=0)
        m=load(ROOT/'tests/fixtures/time/maxwell-axisymmetric.json')
        with self.assertRaises(ValueError):observe(m,{'sigma':[140000,80000,70000,0,0,0]},[0]*6,time=0)

@unittest.skipUnless(SOLVER.exists(),'research solver not built')
class TerracottaNumericalTests(unittest.TestCase):
    def execute(self,s,ok=True,solver=SOLVER):
        r=subprocess.run(schedule_command(s,solver),capture_output=True,text=True,timeout=60);d=json.loads(r.stdout)
        self.assertEqual(d['ok'],ok,d.get('message'));self.assertEqual(r.returncode==0,ok);return d
    def test_author_rhs_reference_histories(self):
        reference=json.loads(REFERENCE.read_text())
        for case in reference['cases']:
            with self.subTest(case=case['id']):
                data=self.execute(reference_spec(case));points=[p for p in data['points'] if p['segment']>=0 and p['side']=='left']
                self.assertEqual(len(points),len(case['points']))
                for actual,wanted in zip(points,case['points']):
                    self.assertEqual(actual['time'],wanted['time'])
                    for i,(a,b) in enumerate(zip(actual['state'],wanted['state'])):self.assertAlmostEqual(a,b,delta=1e-5 if i!=2 else 2e-6)
                    self.assertAlmostEqual(actual['observables'][6],wanted['pressure'],delta=100)
                    self.assertAlmostEqual(actual['observables'][7],wanted['signed_q'],delta=100)
    def test_temperature_and_density_closed_forms(self):
        for kind in ['txu','iso']:
            d=self.execute(make_spec(controls_for(kind,2e-5),10));last=d['points'][-1]
            Dv=6e-5 if kind=='iso' else 0;Ds=2e-5 if kind=='txu' else 0
            production=6e5*(Dv**2+Ds**2);steady=math.sqrt(production/150)
            exact=steady*math.tanh(math.sqrt(150*production)*10)
            self.assertAlmostEqual(last['state'][2],exact,delta=2e-6)
            self.assertAlmostEqual(last['state'][3],.423*math.exp(Dv*10),delta=1e-8)
    def test_refinement_improves_source_agreement(self):
        case=json.loads(REFERENCE.read_text())['cases'][1];wanted=case['points'][-1]['signed_q']
        coarse=self.execute(reference_spec(case,1e-4))['points'][-1]['observables'][7]
        fine=self.execute(reference_spec(case,1e-6))['points'][-1]['observables'][7]
        self.assertLess(abs(fine-wanted),abs(coarse-wanted))
    def test_mixed_radial_control_and_scope_rejection(self):
        s=make_spec([rate(2e-5),hold('stress'),hold('stress')]+[hold() for _ in range(3)])
        d=self.execute(s);last=d['points'][-1]
        self.assertAlmostEqual(last['strain'][0],1e-4,places=12)
        self.assertEqual(last['strain'][1],last['strain'][2])
        self.assertAlmostEqual(last['observables'][1],100000,places=5)
        self.assertEqual(last['observables'][1],last['observables'][2])
        bad=copy.deepcopy(s);bad['segments'][0]['controls'][2]=hold()
        self.assertEqual(self.execute(bad,ok=False)['points'],[])
        bad=copy.deepcopy(s);bad['segments'][0]['controls'][3]=rate(1e-7)
        self.assertEqual(self.execute(bad,ok=False)['points'],[])
    def test_native_material_rejects_out_of_scope_and_bad_state(self):
        for initial,D in [('',[0,1e-5,0,0,0,0]),('',[0,0,0,1e-10,0,0]),('0,0,0,.423',[0]*6),('.0518,0,-.001,.423',[0]*6),('.0518,0,0,1.1',[0]*6)]:
            command=[str(SOLVER),'--mode','integrate-time','--model','terracotta-2024-fig1','--strain-rate',','.join(map(str,D)),'--duration','1']
            if initial:command.extend(['--initial',initial])
            r=subprocess.run(command,capture_output=True,text=True);self.assertFalse(json.loads(r.stdout)['ok'])
    def test_axisymmetric_stress_hold_against_maxwell_creep(self):
        s=make_spec([hold('stress') for _ in range(3)]+[hold() for _ in range(3)],4);s['model']='test-maxwell-axisymmetric'
        d=self.execute(s,solver=TIME_SOLVER);last=d['points'][-1]
        self.assertAlmostEqual(last['strain'][0],40000/(2*12e6*2)*4,places=12)
        self.assertEqual(last['strain'][1],last['strain'][2])

        s['initial']=[140000,80000,70000,0,0,0]
        self.assertEqual(self.execute(s,ok=False,solver=TIME_SOLVER)['points'],[])
