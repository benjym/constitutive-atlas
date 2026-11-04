import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from atlas.data import ingest, normalize_member, numeric_rows
from atlas.benchmark import curve_metrics, interpolate, monotonic_channel
from atlas.structure import check
from atlas.model import ROOT
from atlas.dsl import ValidationError

TMD=b'eps1 epsv eps3 epsq Void ratio q p eta = q/p\n[%] [%] [%] [%] [%] [kPa] [kPa] [-]\n\n0 0 0 0 .8 0 100 0\n1 .2 -.4 .8 .796 30 110 .27\n'
TMU=b"eps1 u sigma3 sigma3' sigma1 sigma1' p q\n[%] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa]\n\n0 200 300 100 300 100 100 0\n1 220 300 80 330 110 90 30\n"


class DataTests(unittest.TestCase):
    def test_tmd_units_and_void_ratio_header_anomaly(self):
        m=normalize_member(TMD,'TMD1.dat','a'*64,'b'*64)
        self.assertEqual(m['rows'][1]['axial_strain'],.01);self.assertEqual(m['rows'][1]['q'],30000)
        self.assertEqual(m['rows'][0]['void_ratio'],.8)
        self.assertIn('dimensionless',m['warnings'][0])
        check(m,json.loads((ROOT/'schemas/experiment.schema.json').read_text()))
    def test_tmu_delta_pore_pressure(self):
        m=normalize_member(TMU,'TMU1.dat','a'*64,'b'*64)
        self.assertEqual(m['rows'][1]['pore_pressure'],20000)
        self.assertEqual(m['rows'][1]['pore_pressure_absolute'],220000)
        self.assertNotIn('volumetric_strain',m['rows'][1]);self.assertNotIn('void_ratio',m['initial'])
    def test_malformed_rows_rejected(self):
        for text in ['h\nh\n0 1\n','h\nh\n0 0 0 0 0 0 nan 0\n','h\nh\ncorrupted\n']:
            with self.assertRaises(ValueError):numeric_rows(text)
    def test_raw_immutable_ingestion_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/'test.zip';out=Path(d)/'normalized'
            with zipfile.ZipFile(raw,'w') as z:z.writestr('../../TMD1.dat',TMD)
            digest=hashlib.sha256(raw.read_bytes()).hexdigest();paths=ingest(raw,out);first=paths[0].read_bytes();ingest(raw,out)
            self.assertEqual(first,paths[0].read_bytes());self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),digest)
            self.assertEqual(paths[0].parent,out)
            with zipfile.ZipFile(raw,'w') as z:z.writestr('TMD1.dat',TMD.replace(b'.8 ',b'.9 '))
            with self.assertRaises(ValueError):ingest(raw,out)
    def test_unknown_experiment_field_rejected(self):
        m=normalize_member(TMD,'TMD1.dat','a'*64,'b'*64);m['rows'][0]['secret']=1
        with self.assertRaises(ValidationError):check(m,json.loads((ROOT/'schemas/experiment.schema.json').read_text()))
    def test_no_interpolation_extrapolation(self):
        self.assertEqual(interpolate([(0,1),(1,3)],.5),2)
        with self.assertRaises(ValueError):interpolate([(0,1),(1,3)],2)
    def test_uniform_grid_metrics(self):
        m=curve_metrics([(0,0),(1,1)],[(0,1),(1,2)])
        self.assertAlmostEqual(m['rmse'],1);self.assertAlmostEqual(m['mae'],1)
    def test_reversal_not_silently_sorted(self):
        with self.assertRaises(ValueError):monotonic_channel([dict(axial_strain=0,q=0),dict(axial_strain=.01,q=1),dict(axial_strain=.005,q=2)],'q',.02)
        points,duplicates=monotonic_channel([dict(axial_strain=0,q=0),dict(axial_strain=0,q=1),dict(axial_strain=.01,q=2)],'q',.02)
        self.assertEqual(duplicates,1);self.assertEqual(points[0],(0,1))
