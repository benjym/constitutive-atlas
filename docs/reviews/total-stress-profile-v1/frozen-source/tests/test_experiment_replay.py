import copy
import json
import math
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

from atlas.dsl import ValidationError
from atlas.experiment_replay import digest, prepare_replay, read_json
from atlas.model import ROOT, load
from atlas.recorded import execute_recorded


def synthetic():
    """Construct observations from isotropic elasticity, independently of DSL."""
    E, nu = 3e7, .25
    rows = []
    for eps, radial in [(0,1e5),(.001,102000),(-.0002,99000),
                        (-.0002,99000),(.0007,101000),(0,1e5)]:
        axial = 103000 + E*eps + 2*nu*(radial-1e5)
        volume = (1-2*nu)*eps + 2*(1+nu)*(1-2*nu)*(radial-1e5)/E
        rows.append({'axial_strain':.02+eps, 'p':(axial+2*radial)/3,
                     'q':axial-radial, 'volumetric_strain':volume})
    experiment = {'schema_version':'0.1','kind':'experiment','id':'synthetic-elastic',
                  'material':'analytical fixture','protocol':'drained-triaxial',
                  'conventions':{'stress':'compression-positive','strain':'compression-positive',
                                 'stress_unit':'Pa','strain_unit':'1'},
                  'provenance':{'source_url':'https://github.com/benjym/constitutive-atlas',
                                'member_sha256':'0'*64,'archive_sha256':'0'*64},
                  'initial':{'effective_stress':[103000,100000,100000,0,0,0]}, 'rows':rows}
    config = {'version':'experimental-drained-replay-0.1','model':'linear-elastic',
              'parameters':{'p_ref':100000,'E':E,'nu':nu}, 'initial_history':{'e':.7},
              'initial_strain':[.001,.002,.002,0,0,0],
              'declarations':{'kinematics':'fixed-frame-axisymmetric-x',
                              'p':'mean-effective-stress',
                              'q':'signed-axial-minus-radial-effective-stress',
                              'strain_origin':'first-observation',
                              'radial_control':'replay-measured-effective-stress',
                              'evidence_url':'https://github.com/benjym/constitutive-atlas',
                              'evidence_locator':'tests/test_experiment_replay.py synthetic()',
                              'initialization_note':'Analytical fixture; e=.7 at row zero.'}}
    return experiment, config


class ConversionTests(unittest.TestCase):
    def test_retained_examples_match_analytical_fixture(self):
        e,c=synthetic()
        self.assertEqual(read_json(ROOT/'tests/fixtures/experiments/synthetic-drained-elastic.json'),e)
        self.assertEqual(read_json(ROOT/'protocols/drained-elastic-replay.json'),c)

    def test_order_origin_duplicates_and_no_mutation(self):
        e,c=synthetic(); before=copy.deepcopy((e,c)); bundle=prepare_replay(e,c)
        self.assertEqual((e,c),before)
        path=bundle['request']['path']
        self.assertEqual([k['coordinate'] for k in path['knots']],list(range(6)))
        self.assertEqual(path['knots'][2]['targets'],path['knots'][3]['targets'])
        self.assertLess(path['knots'][2]['targets'][0],path['knots'][1]['targets'][0])
        self.assertEqual(path['knots'][0]['targets'][0],.001)
        self.assertEqual(bundle['request']['initial'],[103000,100000,100000,0,0,0,.7])
        self.assertEqual(bundle['provenance']['request_sha256'],digest(bundle['request']))

    def test_named_order_and_settings(self):
        e,c=synthetic(); c['parameters']=dict(reversed(list(c['parameters'].items())))
        c['control_settings']={'max_iterations':40}; c['restart_settings']={}
        r=prepare_replay(e,c)['request']
        self.assertEqual(r['parameters'],[100000,3e7,.25])
        self.assertEqual(r['control_settings'],{'max_iterations':40})
        self.assertEqual(r['restart_settings'],{})

    def test_closed_explicit_contract(self):
        for mutate in [lambda e,c:c.update(typo=True),
                       lambda e,c:c['parameters'].pop('nu'),
                       lambda e,c:c['initial_history'].clear(),
                       lambda e,c:c['initial_history'].update(sigma=[0]*6),
                       lambda e,c:c['initial_history'].update(e=[0]*6),
                       lambda e,c:c['parameters'].update(nu=.5),
                       lambda e,c:c['declarations'].update(evidence_locator=' '),
                       lambda e,c:c['declarations'].update(p='total-stress'),
                       lambda e,c:c.update(initial_strain=[0,0,1,0,0,0]),
                       lambda e,c:c.update(initial_strain=[0,0,0,1,0,0]),
                       lambda e,c:c.update(model='../escape')]:
            with self.subTest(mutate=mutate):
                e,c=synthetic(); mutate(e,c)
                with self.assertRaises(ValidationError):prepare_replay(e,c)

    def test_unsupported_experiments(self):
        for mutate in [lambda e:e.update(protocol='undrained-triaxial'),
                       lambda e:e['rows'][1].pop('p'),
                       lambda e:e['rows'][1].update(p=float('nan')),
                       lambda e:e.update(rows=e['rows'][:1]),
                       lambda e:e.update(rows=e['rows']*834),
                       lambda e:e['initial'].update(effective_stress=[0]*6),
                       lambda e:e['conventions'].update(stress='tension-positive')]:
            e,c=synthetic(); mutate(e)
            with self.subTest(mutate=mutate),self.assertRaises(ValidationError):prepare_replay(e,c)

    def test_no_implicit_time(self):
        e,c=synthetic(); m=load(ROOT/'models/linear-elastic.json')
        m['schema_version']='0.2'
        with self.assertRaises(ValidationError):prepare_replay(e,c,model=m)

    def test_void_ratio_disagreement_requires_explicit_override(self):
        e,c=synthetic(); e['initial']['void_ratio']=.9
        with self.assertRaises(ValidationError):prepare_replay(e,c)
        c['initial_void_ratio_override_note']='Deliberate sensitivity case, not measured initialization.'
        p=prepare_replay(e,c)['provenance']['initial_void_ratio_comparison']
        self.assertEqual(p['source'],.9); self.assertEqual(p['supplied_e'],.7)
        self.assertEqual(p['override_note'],c['initial_void_ratio_override_note'])
        c['initial_void_ratio_override_note']=' '
        with self.assertRaises(ValidationError):prepare_replay(e,c)

    def test_named_tensor_history_follows_model_order(self):
        e,c=synthetic(); m=load(ROOT/'models/hypoplastic-sand-igs97.json')
        c['model']=m['id']; c['parameters']={k:v['default'] for k,v in reversed(list(m['parameters'].items()))}
        h=[1e-6,2e-6,3e-6,4e-6,5e-6,6e-6]
        c['initial_history']={'h':h,'e':.7}
        r=prepare_replay(e,c)['request']
        self.assertEqual(r['initial'][6:],[.7,*h])
        self.assertEqual(r['parameters'],[v['default'] for v in m['parameters'].values()])
        c['initial_history']['h']=0
        with self.assertRaises(ValidationError):prepare_replay(e,c)

    def test_reject_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'duplicate.json'; p.write_text('{"p":1,"p":2}')
            with self.assertRaises(ValidationError):read_json(p)

    def test_finite_derived_targets(self):
        e,c=synthetic(); e['rows'][1].update(p=1.7e308,q=-1.7e308)
        with self.assertRaises(ValidationError):prepare_replay(e,c)

    def test_cli_provenance_and_input_protection(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d); e,c=synthetic()
            experiment=directory/'experiment.json'; config=directory/'config.json'
            experiment.write_text(json.dumps(e)); config.write_text(json.dumps(c))
            output=directory/'request.json'
            command=[sys.executable,'-m','atlas.cli','prepare-replay',str(experiment),str(config),'--output']
            process=subprocess.run(command+[str(output)],capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr)
            provenance=read_json(output.with_suffix('.json.provenance.json'))
            self.assertEqual(provenance['request_sha256'],digest(read_json(output)))
            import hashlib
            self.assertEqual(provenance['input_file_sha256']['experiment'],
                             hashlib.sha256(experiment.read_bytes()).hexdigest())
            before=experiment.read_bytes()
            process=subprocess.run(command+[str(experiment)],capture_output=True,text=True)
            self.assertNotEqual(process.returncode,0)
            self.assertEqual(experiment.read_bytes(),before)

    @unittest.skipUnless(os.environ.get('ATLAS_RECORDED_SOLVER'), 'set ATLAS_RECORDED_SOLVER for one serial native replay')
    def test_native_analytical_history(self):
        e,c=synthetic(); bundle=prepare_replay(e,c)
        result=execute_recorded(bundle['request'],os.environ['ATLAS_RECORDED_SOLVER'])
        self.assertTrue(result['ok'],result.get('message'))
        self.assertEqual(len(result['points']),len(e['rows']))
        for observation,point in zip(e['rows'],result['points']):
            state=point['state']; strain=point['strain']
            self.assertAlmostEqual(state[0]-state[1],observation['q'],delta=1e-4)
            self.assertAlmostEqual(sum(state[:3])/3,observation['p'],delta=1e-4)
            self.assertAlmostEqual(sum(strain[:3])-sum(c['initial_strain'][:3]),
                                   observation['volumetric_strain'],delta=1e-10)
            self.assertAlmostEqual(state[6],1.7*math.exp(-observation['volumetric_strain'])-1,delta=1e-10)
        self.assertEqual(result['points'][2]['state'],result['points'][3]['state'])


if __name__=='__main__':unittest.main()
