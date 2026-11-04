"""Effective experiment mapping is guarded independently of model execution support."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.experiment_replay import prepare_replay
from atlas.model import ROOT, all_models, load, migrate_formulation
from tests.test_experiment_replay import synthetic


class EffectiveReplayScopeTests(unittest.TestCase):
    def setUp(self):
        self.model=migrate_formulation(load(ROOT/'models/linear-elastic.json'))
        self.experiment,self.config=synthetic()

    def test_total_unknown_and_observable_stress_are_not_effective_state_inputs(self):
        for binding in [dict(source='state',name='sigma',measure='cauchy',scope='total'),
                        dict(source='state',name='sigma',measure='cauchy',scope='unknown'),
                        dict(source='observable',name='sigma',measure='cauchy',scope='effective'),
                        None]:
            model=copy.deepcopy(self.model);model['formulation']['stress']=binding
            with self.subTest(binding=binding),self.assertRaisesRegex(ValidationError,'effective Cauchy'):
                prepare_replay(self.experiment,self.config,model=model)

    def test_guard_survives_future_semantic_total_profile_support(self):
        self.model['formulation']['stress']['scope']='total'
        with patch('atlas.experiment_replay.validate',return_value=self.model) as validation:
            with self.assertRaisesRegex(ValidationError,'effective Cauchy'):
                prepare_replay(self.experiment,self.config,model=self.model)
            validation.assert_not_called()

    def test_supplied_definitions_cannot_bypass_model_validation(self):
        for mutation in ['version','equation','convention','extra']:
            model=copy.deepcopy(self.model)
            if mutation=='version':model['schema_version']='9.9'
            if mutation=='equation':model['equations']['sigma']='unsupported_symbol'
            if mutation=='convention':model['formulation']['stress_sign']='tension_positive'
            if mutation=='extra':model['unrecognized_field']=True
            with self.subTest(mutation=mutation),self.assertRaises((ValidationError,ValueError)):
                prepare_replay(self.experiment,self.config,model=model)

    def test_all_nine_current_effective_model_bundles_match_exact_prior_converter(self):
        previous=json.loads((ROOT/'docs/reviews/effective-replay-scope-v1/previous-sources.json').read_text())
        path=ROOT/previous['atlas/experiment_replay.py']['archived_path']
        spec=importlib.util.spec_from_file_location('atlas._prior_experiment_replay_scope_test',path)
        prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
        models=all_models();self.assertEqual(len(models),9)
        for model in models:
            configuration=copy.deepcopy(self.config);configuration['model']=model['id']
            configuration['parameters']={name:field['default'] for name,field in model['parameters'].items()}
            configuration['initial_history']={field['name']:copy.deepcopy(field['initial']) for field in model['state'][1:]}
            with self.subTest(model=model['id']):
                expected=prior.prepare_replay(self.experiment,configuration,model=model)
                actual=prepare_replay(self.experiment,configuration,model=model)
                self.assertEqual(actual,expected)


if __name__=='__main__':unittest.main()
