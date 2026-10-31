"""Bounded OCC source-constraint reference; no compiled or author-code execution."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'docs/ingestion/original-cam-clay/smooth-reference-v1'
spec=importlib.util.spec_from_file_location('occ_smooth_reference',HERE/'reference.py')
reference=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)

class OriginalCamClaySmoothReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=json.loads((HERE/'prospective.json').read_text())
        cls.report=reference.run()

    def test_frozen_three_resolution_study_passes(self):
        assessment=self.report['assessment']
        self.assertTrue(assessment['passed'])
        self.assertEqual([p['steps'] for p in assessment['paths']],[16,32,64])
        self.assertEqual(sum(len(p['rows']) for p in self.report['trajectories']),115)
        self.assertFalse(self.report['general_material_update'])
        self.assertFalse(self.report['independent_scientific_review'])
        self.assertEqual(self.report['compiled_calls'],0)

    def test_corrupted_hardening_is_not_hidden_by_exact_pressure_and_q(self):
        trajectories=copy.deepcopy(self.report['trajectories'])
        for path in trajectories:
            path['rows'][-1]['state'][2] += .001
        self.assertFalse(reference.assess(self.policy,trajectories)['passed'])

    def test_incomplete_or_reordered_coordinate_frames_are_rejected(self):
        for mutation in ['missing_path','missing_point','changed_coordinate']:
            paths=copy.deepcopy(self.report['trajectories'])
            if mutation=='missing_path':paths.pop()
            elif mutation=='missing_point':paths[0]['rows'].pop()
            else:paths[0]['rows'][1]['coordinate']+=1e-6
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                reference.assess(self.policy,paths)

    def test_source_vertex_and_critical_mechanism_are_excluded(self):
        parameters=self.policy['parameters'];state,volume=reference.exact(.002,parameters)
        for candidate in [(state[0],0,state[2]),(state[0],parameters['M']*state[0],state[2]),(-1,state[1],state[2])]:
            with self.subTest(candidate=candidate),self.assertRaises(ValueError):
                reference.rates(candidate,parameters,volume)

    def test_boolean_nonfinite_and_invalid_step_inputs_rejected(self):
        parameters=self.policy['parameters'];state,volume=reference.exact(.002,parameters)
        for value in [True,float('nan'),float('inf')]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                reference.rates((value,state[1],state[2]),parameters,volume)
        for count in [True,0,-1,16.0]:
            with self.subTest(count=count),self.assertRaises(ValueError):
                reference.integrate(self.policy,count)

    def test_no_undrained_volume_change_is_silently_reinitialized(self):
        paths=copy.deepcopy(self.report['trajectories']);paths[0]['specific_volume']+=1e-5
        with self.assertRaisesRegex(ValueError,'specific volume changed'):
            reference.assess(self.policy,paths)

if __name__=='__main__':unittest.main()
