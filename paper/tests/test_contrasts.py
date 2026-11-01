"""Controls for the fixed-count design and its paired aggregation."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, read_json
from analysis.contrasts import design_contrasts, root_error
from analysis.pilot import validate_config


def prediction(identifier, q, volume):
    return {'experiment_id':identifier,'status':'success','metrics':{
        'q':{'rmse':q,'scale':1.,'scaled_mse':q*q},
        'volumetric_strain':{'rmse':volume,'scale':1.,'scaled_mse':volume*volume}}}


class MatchedDesign(unittest.TestCase):
    def test_packages_must_have_declared_equal_count(self):
        config=read_json(ROOT/'paper/study/pilot_matched.json')
        config['packages']['density3'].pop()
        with self.assertRaisesRegex(ValueError,'equal test count'):
            validate_config(config)

    def test_groups_cannot_duplicate_or_drop_evaluation_tests(self):
        config=read_json(ROOT/'paper/study/pilot_matched.json')
        config['calibration_design_contrast']['evaluation_groups']['duplicate']=['KFS-TMD1']
        with self.assertRaisesRegex(ValueError,'partition'):
            validate_config(config)

    def test_root_is_taken_after_equal_test_channel_aggregation(self):
        rows=[prediction('a',2.,0.),prediction('b',0.,4.)]
        self.assertAlmostEqual(root_error(rows,['a','b'],.5),5.**.5)
        self.assertAlmostEqual(root_error(rows,['a','b'],.25),6.5**.5)
        self.assertIsNone(root_error(rows,['a','b','missing'],.5))
        rows[1]['status']='integration_failure'
        self.assertIsNone(root_error(rows,['a','b'],.5))

    def test_nonfinite_or_inconsistent_metrics_cannot_enter_contrast(self):
        row=prediction('a',1.,1.)
        row['metrics']['q']['scaled_mse']=.5
        with self.assertRaisesRegex(ValueError,'inconsistent'):
            root_error([row],['a'],.5)
        with self.assertRaisesRegex(ValueError,'weight'):
            root_error([],[],float('nan'))

    def test_weight_sensitivity_can_expose_a_reversal_without_refitting(self):
        config=read_json(ROOT/'paper/study/pilot_matched.json')
        model=config['models'][0]
        config['models']=[model]
        config['optimizer']['seeds']=[0]
        rows=[]
        # Pressure design fits stress; density design fits volume. This is a
        # controlled counterexample to reporting only an aggregate winner.
        for eid in config['evaluation_ids']:
            for package,q,v in [('pressure3',0.,2.),('density3',2.,0.)]:
                row=prediction(eid,q,v)
                row.update(model=model['id'],package=package,seed=0,selected=True)
                rows.append(row)
        output=design_contrasts({'config':config,'predictions':rows})
        changes={r['stress_weight']:r['root_error_change'] for r in output['summaries']
                 if r['group']=='all_evaluation_tests'}
        self.assertLess(changes[.25],0.)
        self.assertEqual(changes[.5],0.)
        self.assertGreater(changes[.75],0.)
        incomplete=copy.deepcopy(rows)
        incomplete.pop()
        output=design_contrasts({'config':config,'predictions':incomplete})
        self.assertFalse(next(r for r in output['summaries'] if r['group']=='all_evaluation_tests')['complete'])


if __name__=='__main__':
    unittest.main()
