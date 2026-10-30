import copy
import hashlib
import json
import math
import os
from pathlib import Path
import unittest

from atlas.initialization import canonical_hash
from atlas.model import ROOT,load
from tools.reference_terracotta_creep import advance,creep_rates,elastic,generate,PARAMETERS,total_stress
from tools.terracotta_creep_study import assess_study,compare_response,run

REFERENCE=ROOT/'tests/reference/terracotta-2024-scalar-creep.json'
EVIDENCE=ROOT/'catalogue/investigations/terracotta-creep-v1'


class ScalarCreepTests(unittest.TestCase):
    def test_frozen_reference_pins_and_regeneration(self):
        reference=json.loads(REFERENCE.read_bytes())
        self.assertEqual(reference['generator_sha256'],hashlib.sha256((ROOT/'tools/reference_terracotta_creep.py').read_bytes()).hexdigest())
        self.assertEqual(reference['model_sha256'],canonical_hash(load(ROOT/'models/research/terracotta-2024-fig1.json')))
        fresh=generate()
        self.assertEqual([c['id'] for c in fresh['cases']],['compression','extension','isotropic'])
        for a,b in zip(reference['cases'],fresh['cases']):
            for x,y in zip(a['points'],b['points']):
                for field in ('state','strain','rate'):
                    for actual,wanted in zip(x[field],y[field]):self.assertAlmostEqual(actual,wanted,delta=1e-12)
            for key in ('rk4_state_last_pair','rk4_strain_last_pair','rk4_rate_last_pair'):
                self.assertLess(max(a['reference_errors'][key]),1e-10)
            self.assertEqual([g['steps_per_sample'] for g in a['rk4_refinement']],[128,256,512])

    def test_preparation_analytic_temperature_density_and_entry_rates(self):
        reference=json.loads(REFERENCE.read_bytes())
        for case in reference['cases']:
            prep=case['preparation'];z=prep['prepared_extended_state'];Dv,Ds=prep['rates_Dv_Ds'];p=reference['parameters']
            production=p['alpha']*Dv**2+p['gamma']*Ds**2
            temperature=math.sqrt(production/p['eta'])*math.tanh(math.sqrt(production*p['eta'])*10)
            self.assertAlmostEqual(z[2],temperature,delta=1e-13)
            self.assertAlmostEqual(z[3],.423*math.exp(Dv*10),delta=1e-13)
            rates=creep_rates(z,(case['targets']['pressure'],case['targets']['signed_q']),p)
            for actual,wanted in zip(rates,(Dv,Ds)):self.assertAlmostEqual(actual,wanted,delta=1e-15)
            self.assertGreater(abs(case['points'][-1]['strain'][0]-case['points'][0]['strain'][0]),1e-5)
            for point in case['points']:self.assertGreater(point['state'][2],0)

    def test_signed_symmetry_and_stress_elimination(self):
        cases=json.loads(REFERENCE.read_bytes())['cases'];positive,negative=cases[:2]
        for a,b in zip(positive['points'],negative['points']):
            self.assertEqual(a['state'][0],b['state'][0]);self.assertEqual(a['state'][1],-b['state'][1])
            self.assertEqual(a['state'][2:],b['state'][2:])
        p=PARAMETERS.copy();z=[.05,.005,.001,.423,0,0];wanted=(7e-5,-9e-5)
        targets=total_stress(z,wanted,p)
        for actual,expected in zip(creep_rates(z,targets,p),wanted):self.assertAlmostEqual(actual,expected,delta=1e-16)
        with self.assertRaises(ValueError):creep_rates([.05,0,0,.423,0,0],targets,p)
        with self.assertRaises(ValueError):advance(z,1,0,lambda z:wanted,p)

    def test_retained_full_matrix_and_hashes(self):
        m=json.loads((EVIDENCE/'manifest.json').read_bytes())
        for path,sha in m['implementation_and_inputs'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha,path)
        for path,sha in m['artifacts'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/path).read_bytes()).hexdigest(),sha,path)
        records=json.loads((EVIDENCE/'native.json').read_bytes())
        self.assertEqual(len(assess_study(records,json.loads(REFERENCE.read_bytes()),m['runtime']['catalogue_hash'])),3)

    def test_corrupt_responses_metrics_grid_and_settings_rejected(self):
        records=json.loads((EVIDENCE/'native.json').read_bytes());reference=json.loads(REFERENCE.read_bytes())
        for mutate in (lambda r:r.pop(),
                       lambda r:r.append(copy.deepcopy(r[0])),
                       lambda r:r[0]['response'].update(ok=False),
                       lambda r:r[0]['response'].update(catalogue_hash='0'*64),
                       lambda r:r[0]['response']['points'][2].update(temporal_error_norm=float('nan')),
                       lambda r:r[0]['response']['points'][2].update(nonlinear_residual_norm=1),
                       lambda r:r[0]['response']['points'][2]['observables'].__setitem__(0,0),
                       lambda r:r[0]['response']['points'][2].update(time=2.5),
                       lambda r:r[0]['response']['points'][2]['state'].__setitem__(0,float('nan')),
                       lambda r:r[0]['response']['points'][1]['strain_rate'].__setitem__(0,0),
                       lambda r:r[0]['response']['solver'].update(relative_tolerance=1),
                       lambda r:r[0]['response']['solver'].update(maximum_depth=0),
                       lambda r:r[0]['maximum_errors']['state'].__setitem__(0,0),
                       lambda r:r[0]['request']['initial'].__setitem__(0,.1)):
            broken=copy.deepcopy(records);mutate(broken)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):assess_study(broken,reference)

    @unittest.skipUnless(os.environ.get('ATLAS_RESEARCH_SOLVER'),'set existing research solver; no build required')
    def test_native_creep_three_preparations_three_tolerances(self):
        reference=json.loads(REFERENCE.read_bytes());records=run(reference,os.environ['ATLAS_RESEARCH_SOLVER'])
        self.assertEqual(len(assess_study(records,reference)),3)


if __name__=='__main__':unittest.main()
