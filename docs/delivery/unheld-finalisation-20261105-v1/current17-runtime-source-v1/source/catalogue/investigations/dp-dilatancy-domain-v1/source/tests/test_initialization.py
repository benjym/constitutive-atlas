import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from atlas.dsl import ValidationError
from atlas.experiment_replay import read_json
from atlas.initialization import canonical_hash, initialize, validate_recipe
from atlas.model import ROOT, load, observe
from atlas.schedule import schedule_command


def fixtures():
    return (read_json(ROOT/'initialization/terracotta-2024-fig1-total-stress.json'),
            read_json(ROOT/'initialization/terracotta-2024-kaolin-initialization.json'),
            load(ROOT/'models/research/terracotta-2024-fig1.json'))


class InitializationTests(unittest.TestCase):
    def test_default_and_hashes_without_mutation(self):
        r,c,m=fixtures(); before=copy.deepcopy((r,c,m)); x=initialize(r,c,m)
        self.assertEqual((r,c,m),before)
        self.assertEqual(x['run_fields']['initial'],[f['initial'] for f in m['state']])
        self.assertAlmostEqual(x['observables_at_time_zero']['pressure'],100000,delta=1e-8)
        self.assertEqual(x['provenance']['run_fields_sha256'],canonical_hash(x['run_fields']))

    def test_forward_elastic_cartesian_round_trip(self):
        r,c,m=fixtures()
        # Independent forward energy derivatives, not the inverse DSL expressions.
        for phi in (.3,.423,.7):
            for ev,es in ((.02,0),(.04,.008),(.04,-.008)):
                for temperature,Dv,Ds in ((0,0,0),(.0004,2e-5,-3e-5)):
                    K,G=c['parameters']['Kmod'],c['parameters']['Gmod']
                    pe=phi**6*(K*ev*ev+3*G*es*es)/2
                    qe=3*G*phi**6*ev*es
                    alpha,gamma,Gamma=(c['parameters'][k] for k in ('alpha','gamma','Gamma'))
                    p=pe+(2*alpha*temperature*Dv+temperature**2)/Gamma
                    q=qe+2*gamma*temperature*Ds/Gamma
                    c['inputs'].update(pInput=p,qInput=q,phiInput=phi,TmInput=temperature,DvInput=Dv,DsInput=Ds)
                    with self.subTest(phi=phi,es=es,Tm=temperature):
                        x=initialize(r,c,m);z=x['named_state'];rate=x['run_fields']['initial_strain_rate']
                        self.assertAlmostEqual(z['ev_e'],ev,delta=2e-14)
                        self.assertAlmostEqual(z['es_e'],es,delta=2e-14)
                        self.assertAlmostEqual(sum(rate[:3]),Dv,delta=1e-18)
                        self.assertAlmostEqual(2*(rate[0]-rate[1])/3,Ds,delta=1e-18)
                        self.assertAlmostEqual(x['observables_at_time_zero']['pressure'],p,delta=1e-7)
                        self.assertAlmostEqual(x['observables_at_time_zero']['signed_q'],q,delta=1e-7)

    def test_parameter_changes_reinitialize_pressure(self):
        r,c,m=fixtures(); default=initialize(r,c,m)['named_state']['ev_e']
        for scale in (.5,2,10):
            c['parameters']['Kmod']=13e9*scale;c['parameters']['Gmod']=5e9*scale
            x=initialize(r,c,m)
            self.assertAlmostEqual(x['named_state']['ev_e'],default/math.sqrt(scale),delta=1e-14)
            self.assertAlmostEqual(x['observables_at_time_zero']['pressure'],100000,delta=1e-8)

    def test_model_initial_checks_are_required(self):
        r,c,m=fixtures();m['initial_checks']=['Tm > 0 * sqrt(Gamma * pOne)']
        r['model_sha256']=canonical_hash(m)
        with self.assertRaises(ValidationError):initialize(r,c,m)
        c['inputs']['TmInput']=.001
        self.assertEqual(initialize(r,c,m)['named_state']['Tm'],.001)

    def test_generic_tensor_state_and_unit_guard(self):
        m=load(ROOT/'tests/fixtures/time/maxwell-axisymmetric.json')
        r={'version':'experimental-initialization-recipe-0.1','id':'synthetic-tensor-state',
           'model':m['id'],'model_sha256':canonical_hash(m),
           'sources':[{'url':m['sources'][0]['url'],'locator':'Synthetic Maxwell state initialization test'}],
           'inputs':{'sigmaInput':{'shape':'sym','unit':'Pa'}},'terms':[],
           'state':{'sigma':'sigmaInput'},'initial_strain_rate':'I * (0/tau)'}
        c={'version':'experimental-initialization-input-0.1',
           'parameters':{k:v['default'] for k,v in m['parameters'].items()},
           'inputs':{'sigmaInput':[140000,80000,80000,0,0,0]}}
        x=initialize(r,c,m)
        self.assertEqual(x['run_fields']['initial'],c['inputs']['sigmaInput'])
        c['inputs']['sigmaInput'][2]=70000
        with self.assertRaises(ValidationError):initialize(r,c,m)

    def test_cli_exact_input_hashes_and_protection(self):
        r,c,m=fixtures()
        with tempfile.TemporaryDirectory() as d:
            paths=[Path(d)/name for name in ('recipe.json','config.json','model.json')]
            for p,x in zip(paths,(r,c,m)):p.write_text(json.dumps(x))
            output=Path(d)/'result.json'
            command=[sys.executable,'-m','atlas.cli','initialize',str(paths[0]),str(paths[1]),
                     '--model-definition',str(paths[2]),'--output']
            p=subprocess.run(command+[str(output)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            result=read_json(output)
            import hashlib
            self.assertEqual(result['provenance']['input_file_sha256']['model'],hashlib.sha256(paths[2].read_bytes()).hexdigest())
            before=paths[0].read_bytes()
            p=subprocess.run(command+[str(paths[0])],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(paths[0].read_bytes(),before)

    def test_stable_repeated_root_exact_case(self):
        r,c,m=fixtures();c['parameters'].update(Kmod=3,Gmod=1)
        c['inputs'].update(phiInput=1,pInput=3,qInput=3)
        x=initialize(r,c,m)
        self.assertEqual(x['run_fields']['initial'],[1,1,0,1])
        # Equality follows current draft domain; source-boundary review remains open.

    def test_domain_failures_not_projected(self):
        for values in ({'phiInput':0},{'phiInput':1.1},{'TmInput':-.1},
                       {'pInput':0},{'qInput':2e5},{'TmInput':100},
                       {'TmInput':.01,'DvInput':1}, {'pInput':1e308}):
            r,c,m=fixtures();c['inputs'].update(values)
            with self.subTest(values=values),self.assertRaises(ValidationError):initialize(r,c,m)
        r,c,m=fixtures();c['parameters']['Mcrit']=3
        with self.assertRaises(ValidationError):initialize(r,c,m)

    def test_closed_explicit_inputs_and_dimensions(self):
        for mutate in (lambda r,c,m:c['parameters'].pop('omega'),
                       lambda r,c,m:c['inputs'].update(typo=0),
                       lambda r,c,m:c['inputs'].update(phiInput=[0]*6),
                       lambda r,c,m:c['inputs'].update(phiInput=float('nan')),
                       lambda r,c,m:r['terms'][0].update(expr='pInput+phiInput'),
                       lambda r,c,m:r['terms'][0].update(requires=['pInput']),
                       lambda r,c,m:r['terms'][0].update(expr='futureTerm'),
                       lambda r,c,m:r['terms'][0].update(name='Kmod'),
                       lambda r,c,m:r['state'].pop('Tm'),
                       lambda r,c,m:r.update(initial_strain_rate='pInput * I'),
                       lambda r,c,m:m['parameters']['Kmod'].update(default=12e9)):
            r,c,m=fixtures();mutate(r,c,m)
            with self.subTest(mutate=mutate),self.assertRaises(ValidationError):initialize(r,c,m)

    @unittest.skipUnless(os.environ.get('ATLAS_RESEARCH_SOLVER'),'set existing research solver; no build needed')
    def test_native_rate_jump_and_temperature_decay(self):
        r,c,m=fixtures();c['inputs'].update(qInput=-10000,TmInput=.0004,DvInput=2e-5,DsInput=-3e-5)
        x=initialize(r,c,m);rate=x['run_fields']['initial_strain_rate']
        # Switch directly to zero strain rate: persistent state continuous while
        # viscous stresses jump. Compare the one-sided boundary and exact Tm decay.
        s={'schema_version':'0.2','units':'SI','start_time':0,**x['run_fields'],
           'segments':[{'id':'relax','duration':2,'samples':4,
                        'controls':[{'quantity':'strain','kind':'hold'} for _ in range(6)]}],
           'solver':{'method':'backward-euler-step-doubling','relative_tolerance':1e-7,
                     'absolute_scale_fraction':1e-11,'maximum_substeps':100000}}
        p=subprocess.run(schedule_command(s,os.environ['ATLAS_RESEARCH_SOLVER']),capture_output=True,text=True,timeout=60)
        d=json.loads(p.stdout);self.assertTrue(d['ok'],d.get('message'))
        initial=[p for p in d['points'] if p['time']==0]
        self.assertGreaterEqual(len(initial),2)
        left,right=initial[0],initial[-1]
        self.assertEqual(left['state'],right['state'])
        self.assertAlmostEqual(left['observables'][6],c['inputs']['pInput'],delta=1e-7)
        self.assertAlmostEqual(left['observables'][7],c['inputs']['qInput'],delta=1e-7)
        self.assertAlmostEqual(left['observables'][6]-right['observables'][6],
                               2*c['parameters']['alpha']/.001*.0004*2e-5,delta=1e-7)
        self.assertAlmostEqual(left['observables'][7]-right['observables'][7],
                               2*c['parameters']['gamma']/.001*.0004*(-3e-5),delta=1e-7)
        for point in d['points']:
            exact=.0004/(1+150*.0004*point['time'])
            self.assertAlmostEqual(point['state'][2],exact,delta=2e-8)


if __name__=='__main__':unittest.main()
