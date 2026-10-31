"""Calibration-only selection, tie ordering and failed-start exclusion."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1/assess.py'
SPEC=importlib.util.spec_from_file_location('tmd13_selection',PATH)
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)


def start(seed,objective,status='success',evaluation=0,scenario='alternative'):
    return {'record':{'seed':seed,'scenario':scenario},'fit_status':status,
            'best_objective':objective,'evaluation_error':evaluation}


class CalibrationSelectionTests(unittest.TestCase):
    def test_only_calibration_error_within_scenario_selects(self):
        chosen=MODULE.choose_start([start(0,2,evaluation=0),start(17,1,evaluation=100),
                                    start(41,0,scenario='other')],'alternative')
        self.assertEqual(chosen['record']['seed'],17)

    def test_equal_objectives_keep_listed_seed_order(self):
        chosen=MODULE.choose_start([start(0,1),start(17,1)],'alternative')
        self.assertEqual(chosen['record']['seed'],0)

    def test_failed_starts_are_excluded_and_no_success_is_explicit(self):
        failed=start(0,0,status='calibration_failure')
        chosen=MODULE.choose_start([failed,start(17,1)],'alternative')
        self.assertEqual(chosen['record']['seed'],17)
        self.assertIsNone(MODULE.choose_start([failed],'alternative'))


if __name__=='__main__':unittest.main()
