"""Independent scalar integral witnesses and saved diagnostic rejection checks."""
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

PACKET=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-partition-diagnostic-v1'
SPEC=importlib.util.spec_from_file_location('partition_analysis_test',PACKET/'analyze.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)


class PartitionDiagnosticTests(unittest.TestCase):
    def test_constant_and_sign_crossing_linear_difference_integrals(self):
        reference=[{'axial_strain':0,'q':0},{'axial_strain':1,'q':0}]
        constant=[{'axial_strain':0,'q':2},{'axial_strain':1,'q':2}]
        cross=[{'axial_strain':0,'q':1},{'axial_strain':1,'q':-1}]
        self.assertEqual(A.interval_localization(reference,constant,2)['normalized_rms'],1)
        self.assertAlmostEqual(A.interval_localization(reference,cross,1)['normalized_rms'],math.sqrt(1/3))

    def test_redundant_linear_sampling_preserves_integral(self):
        reference=[{'axial_strain':x,'q':0} for x in (0,.5,1)]
        prediction=[{'axial_strain':x,'q':1-2*x} for x in (0,.5,1)]
        result=A.interval_localization(reference,prediction,1)
        self.assertAlmostEqual(result['normalized_rms'],math.sqrt(1/3))
        self.assertAlmostEqual(result['top_three_squared_difference_share'],1)
        bad=[dict(p) for p in prediction];bad[1]['axial_strain']=.4
        with self.assertRaises(ValueError):A.interval_localization(reference,bad,1)

    def fixture(self,path,substeps=4,rejected=1,steps=1):
        raw={'target':.001,'steps':steps,'points':[{}, {'substeps':substeps,'rejected':rejected}]}
        (path/'out').write_text(json.dumps(raw))
        (path/'processes.json').write_text(json.dumps([{}, {'command':['solver','--target','.001','--steps',str(steps)],'stdout':'out'}]))
        (path/'prediction.json').write_text(json.dumps({'diagnostics':{'substeps':substeps,'rejected':rejected}}))

    def test_diagnostic_mean_is_travel_over_reported_count_not_caller_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary);self.fixture(path)
            segments,stats=A.segment_stats(path,.001)
            self.assertEqual(segments[0]['mean_axial_travel_per_reported_substep'],.00025)
            self.assertEqual(stats['caller_steps'],1)
            self.assertEqual(stats['reported_substeps'],4)
            self.assertEqual(stats['reported_rejected'],1)

    def test_inconsistent_tree_counts_and_ceiling_policy_reject(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)
            for kwargs in ({'substeps':6,'rejected':1},{'steps':2},{'rejected':True}):
                self.fixture(path,**kwargs)
                with self.assertRaises(ValueError):A.segment_stats(path,.001)


if __name__=='__main__':unittest.main()
