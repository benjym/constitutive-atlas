import copy
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from atlas.dsl import I, Sym, Type, ValidationError, cube_trace, dev, dot, infer, parse
from atlas.model import ROOT, all_models, defaults, interpret, load, validate
from atlas.compiler import generate

SOLVER = Path(os.environ.get('ATLAS_SOLVER',ROOT/'build/atlas_solver'))


def csv(values): return ','.join(format(v,'.17g') for v in values)
def run(model, **kwargs):
    args=[str(SOLVER),'--model',model]
    args += [s for key,value in kwargs.items() for s in ('--'+key.replace('_','-'),str(value))]
    result=subprocess.run(args,text=True,capture_output=True,timeout=30)
    data=json.loads(result.stdout)
    if data['ok'] != (result.returncode==0): raise AssertionError(result.stderr)
    return data


class LanguageTests(unittest.TestCase):
    def test_all_models_validate(self):
        self.assertGreaterEqual(len(all_models()),5)
    def test_injection_and_unsupported_syntax(self):
        for expression in ["__import__('os').system('true')",'sigma[0]','(lambda: 1)()', 'x.__class__','[1,2]', 'sum(x for x in y)']:
            with self.subTest(expression=expression),self.assertRaises(ValidationError): infer(parse(expression),{'x':Type()})
    def test_dimension_mismatch(self):
        for expression in ['p + e','exp(p)','p ** e', 'dot(p, p)']:
            with self.subTest(expression=expression),self.assertRaises(ValidationError):
                infer(parse(expression),{'p':Type(dim=(1,-1,-2)),'e':Type()})
    def test_undefined_symbol(self):
        with self.assertRaises(ValidationError): infer(parse('missing + 1'),{})
    def test_dimensioned_sqrt(self):
        self.assertEqual(infer(parse('sqrt(p*p)'),{'p':Type(dim=(1,-1,-2))}),Type(dim=(1,-1,-2)))
    def test_missing_equation_and_bad_scale(self):
        m=load(ROOT/'models/linear-elastic.json');del m['equations']['e']
        with self.assertRaises(ValidationError):validate(m)
        m=load(ROOT/'models/linear-elastic.json');m['state'][0]['scale']='e'
        with self.assertRaises(ValidationError):validate(m)
    def test_reserved_name(self):
        m=load(ROOT/'models/linear-elastic.json');m['parameters']['double']=m['parameters'].pop('E')
        with self.assertRaises(ValidationError):validate(m)
    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'m.json';p.write_text('{"id":"x","id":"y"}')
            with self.assertRaises(ValidationError):load(p)
    def test_deterministic_codegen(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            generate(a);generate(b)
            self.assertEqual((Path(a)/'models.hpp').read_bytes(),(Path(b)/'models.hpp').read_bytes())
    def test_mandel_contraction(self):
        # A physical xy shear of 2 maps to sqrt(2)*2; its Frobenius square is 8.
        a=Sym((0,0,0,2*math.sqrt(2),0,0));self.assertAlmostEqual(dot(a,a),8)
        self.assertAlmostEqual(dot(dev(I),dev(I)),0)
    def test_cube_trace(self):
        a=Sym((1,2,3,math.sqrt(2)*.5,math.sqrt(2)*.25,math.sqrt(2)*.75))
        matrix=[[1,.5,.75],[.5,2,.25],[.75,.25,3]]
        expected=sum(matrix[i][j]*matrix[j][k]*matrix[k][i] for i in range(3) for j in range(3) for k in range(3))
        self.assertAlmostEqual(cube_trace(a),expected)


@unittest.skipUnless(SOLVER.exists(),'native solver has not been built')
class NumericalTests(unittest.TestCase):
    def require(self,data):
        self.assertTrue(data['ok'],data.get('message'));return data
    def test_elastic_drained_closed_form(self):
        r=self.require(run('linear-elastic',protocol=1,target=.001,steps=20));last=r['points'][-1]
        self.assertAlmostEqual(last['q_signed'],30e6*.001,places=3)
        self.assertAlmostEqual(last['strain'][1],-.25*.001,places=10)
        self.assertAlmostEqual(last['state'][1],1e5,places=3)
    def test_elastic_undrained_closed_form(self):
        r=self.require(run('linear-elastic',protocol=2,target=.001,steps=10));last=r['points'][-1]
        self.assertAlmostEqual(last['q_signed'],3*12e6*.001,places=4)
        self.assertAlmostEqual(last['p'],1e5,places=5)
        self.assertAlmostEqual(sum(last['strain'][:3]),0,places=12)
        self.assertAlmostEqual(last['u'],12e6*.001,places=4)
    def test_elastic_isotropic_closed_form(self):
        r=self.require(run('linear-elastic',protocol=4,target=.001,steps=10))
        self.assertAlmostEqual(r['points'][-1]['p'],160000,places=4)
        self.assertAlmostEqual(r['points'][-1]['q'],0,places=5)
    def test_elastic_oedometer_closed_form(self):
        r=self.require(run('linear-elastic',protocol=0,target=.001,steps=10))
        self.assertAlmostEqual(r['points'][-1]['state'][0],136000,places=4)
        self.assertAlmostEqual(r['points'][-1]['state'][1],112000,places=4)
    def test_stress_control_closed_form(self):
        r=self.require(run('linear-elastic',protocol=3,target=10000,steps=64,cycles=2))
        for pt in r['points']:
            self.assertAlmostEqual(pt['q_signed'],pt['control'],places=3)
            self.assertAlmostEqual(pt['strain'][0],pt['control']/36e6,places=10)
    def test_cycle_returns_elastic_state(self):
        r=self.require(run('linear-elastic',protocol=2,target=.001,steps=100,cycles=2))
        for a,b in zip(r['initial'],r['points'][-1]['state']):self.assertAlmostEqual(a,b,places=5)
    def test_drucker_prager_yield_and_complementarity(self):
        r=self.require(run('drucker-prager',protocol=2,target=.02,steps=120))
        for pt in r['points']:
            gamma=pt['state'][7];f=pt['q']-1.2*pt['p']-10000
            self.assertLessEqual(f,.001);self.assertGreaterEqual(gamma,-1e-9)
            self.assertLess(abs(gamma*f),.001)
        self.assertGreater(r['points'][-1]['state'][7],0)
    def test_mcc_yield_hardening_and_unloading(self):
        r=self.require(run('modified-cam-clay',protocol=4,target=.025,steps=160))
        last=r['points'][-1];self.assertGreater(last['state'][7],200000)
        for pt in r['points']:
            f=pt['q']**2+1.2**2*pt['p']*(pt['p']-pt['state'][7])
            self.assertLessEqual(f/1e10,1e-7)
        unloaded=self.require(run('modified-cam-clay',mode='integrate',initial=csv(last['state']),strain=csv([-.0001]*3+[0]*3)))
        self.assertAlmostEqual(unloaded['state'][7],last['state'][7],delta=.01)
    def test_small_step_convergence(self):
        for name in ['hypoplastic-sand-vw96','modified-cam-clay']:
            results=[self.require(run(name,protocol=2,target=.005,steps=n))['points'][-1]['q'] for n in (20,40,80)]
            self.assertLess(abs(results[2]-results[1]),max(abs(results[1]-results[0])*.8,.1))
    def test_igs_small_strain_stiffness(self):
        h=self.require(run('hypoplastic-sand-igs97',protocol=2,target=1e-8,steps=1))
        b=self.require(run('hypoplastic-sand-vw96',protocol=2,target=1e-8,steps=1))
        self.assertAlmostEqual(h['points'][-1]['q']/b['points'][-1]['q'],5,delta=.002)
    def test_rate_zero_increment(self):
        for name in ['hypoplastic-sand-vw96','hypoplastic-sand-igs97']:
            r=self.require(run(name,mode='integrate',strain='0,0,0,0,0,0'))
            self.assertEqual(r['state'][:3],[100000]*3)
    def test_invalid_state_rollback(self):
        z=[-100000]*3+[0,0,0,.7,200000,0]
        r=run('modified-cam-clay',mode='integrate',initial=csv(z),strain='0.001,0,0,0,0,0')
        self.assertFalse(r['ok']);self.assertEqual(z,r['state'])
    def test_invalid_inputs(self):
        for kwargs in [dict(steps=0),dict(steps=1.5),dict(target='nan'),dict(protocol=9),dict(parameters='1'),dict(initial='1'),dict(target=.5),dict(nonsense=1)]:
            self.assertFalse(run('linear-elastic',**kwargs)['ok'])
    def test_initial_yield_admissibility(self):
        z=[300000,300000,300000,0,0,0,.7,200000,0]
        r=run('modified-cam-clay',mode='integrate',initial=csv(z),strain='0,0,0,0,0,0')
        self.assertFalse(r['ok']);self.assertEqual(r['state'],z)
    def test_native_description_matches_model_source(self):
        data=json.loads(subprocess.check_output([str(SOLVER),'--describe'],text=True))
        self.assertEqual(data['models'],all_models())
    def test_interpreter_generated_equations_agree(self):
        for m in all_models():
            previous={f['name']:f['initial'] for f in m['state']};current=copy.deepcopy(previous)
            current['sigma']=[110000,95000,100000,100,50,25]
            de=[.00002,-.00001,-.00001,.000003,0,0]
            expected=interpret(m,current,previous,de)
            flat=lambda s:[x for f in m['state'] for x in (s[f['name']] if f.get('shape')=='sym' else [s[f['name']]])]
            result=self.require(run(m['id'],mode='evaluate',current=csv(flat(current)),initial=csv(flat(previous)),strain=csv(de)))
            wanted=[x for f in m['state'] for x in (expected[f['name']].v if isinstance(expected[f['name']],Sym) else [expected[f['name']]])]
            for a,b in zip(wanted,result['values']):self.assertAlmostEqual(a,b,delta=1e-9*max(1,abs(a)))


if __name__=='__main__': unittest.main()
