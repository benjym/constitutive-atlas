"""Portable tests for the bounded source analytical packet only."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('occ_ingestion_check',HERE/'check_packet.py')
packet=importlib.util.module_from_spec(spec);spec.loader.exec_module(packet)


class AnalyticalPacketTests(unittest.TestCase):
    def test_complete_algebra(self):
        result=packet.diagnostics()
        self.assertTrue(result['passed']);self.assertEqual(result['compiled_calls'],0)
        self.assertFalse(result['general_constitutive_evaluator'])
    def test_invalid_parameters(self):
        for kw in [dict(M=True),dict(M=0),dict(lam=.04),dict(kap=0),dict(p_ref=-1),dict(Gamma=math.nan)]:
            with self.subTest(kw=kw),self.assertRaises(ValueError):packet.parameters(**kw)
    def test_invalid_path_domain(self):
        for kw in [dict(eps_s=True),dict(eps_s=-.1),dict(eps_s=math.inf),dict(eps_s=0,p0=0),dict(eps_s=0,Gamma=-1)]:
            with self.subTest(kw=kw),self.assertRaises(ValueError):packet.virgin_undrained(**kw)
    def test_source_hash_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'not-the-source.pdf';f.write_bytes(b'altered private source')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):packet.verify_source(f)
    def test_small_positive_distortion_not_lost(self):
        x=packet.virgin_undrained(1e-20)
        self.assertGreater(x['q'],0.)
        self.assertEqual(x['v'],packet.virgin_undrained(0.)['v'])
    def test_no_MCC_critical_pressure_substitution(self):
        M=1.2;pc=100000.;p=pc/2
        self.assertGreater(abs(packet.yield_f(p,M*p,pc,M)),1000.)


if __name__=='__main__':unittest.main(verbosity=2)
