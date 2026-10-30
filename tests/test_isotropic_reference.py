import copy
import gzip
import json
import math
from pathlib import Path
import unittest
from atlas.isotropic_reference import cam_clay_isotropic
from tools.analyze_mcc_continuous import analyze,analyze_followups
ROOT=Path(__file__).resolve().parents[1]

class IsotropicReferenceTests(unittest.TestCase):
    def test_elastic_closed_form_and_reversible_cycle(self):
        strains=[0,.001,-.001,0]
        points=cam_clay_isotropic(1e5,2e5,.7,.04,.2,strains)
        for strain,point in zip(strains,points):
            self.assertAlmostEqual(point['p'],1e5*math.exp(1.7*(1-math.exp(-strain))/.04),places=8)
            self.assertEqual(point['pc'],2e5)
        self.assertAlmostEqual(points[-1]['p'],1e5,places=8)

    def test_yield_crossing_split_and_duplicate(self):
        vy=1.7-.04*math.log(2);yield_strain=math.log(1.7/vy)
        unsplit=cam_clay_isotropic(1e5,2e5,.7,.04,.2,[0,.045,.015,.015,.06,0])
        split=cam_clay_isotropic(1e5,2e5,.7,.04,.2,[0,yield_strain,.045,.015,.015,.06,0])
        self.assertAlmostEqual(split[1]['p'],2e5,places=8)
        self.assertAlmostEqual(unsplit[1]['p'],2e5*math.exp((vy-1.7*math.exp(-.045))/.2),places=8)
        self.assertEqual(unsplit[2],unsplit[3])
        for a,b in zip(unsplit[1:],split[2:]):
            for key in ('p','pc','e'):self.assertAlmostEqual(a[key],b[key],places=8)
        self.assertEqual(unsplit[-1]['pc'],unsplit[-2]['pc'])
        self.assertGreater(unsplit[-1]['pc'],2e5)

    def test_units_and_segment_composition(self):
        targets=[0,.045,.015,.06,0]
        base=cam_clay_isotropic(1e5,2e5,.7,.04,.2,targets)
        scaled=cam_clay_isotropic(100,200,.7,.04,.2,targets)
        for a,b in zip(base,scaled):
            self.assertAlmostEqual(a['p']/1000,b['p'],places=10)
            self.assertAlmostEqual(a['pc']/1000,b['pc'],places=10)
        middle=base[1]
        restarted=cam_clay_isotropic(middle['p'],middle['pc'],middle['e'],.04,.2,[0]+[x-targets[1] for x in targets[2:]])
        for a,b in zip(base[1:],restarted):
            for key in ('p','pc','e'):self.assertAlmostEqual(a[key],b[key],places=8)

    def test_domain(self):
        for p,pc,e,k,l,path in [(2e5,1e5,.7,.04,.2,[0]),(1e5,2e5,.7,.2,.04,[0]),
                               (1e5,2e5,.7,.04,.2,[.01]),(1e5,2e5,.7,.04,.2,[0,1]),
                               (1e5,2e5,.7,.04,.2,[0,float('nan')])]:
            with self.assertRaises(ValueError):cam_clay_isotropic(p,pc,e,k,l,path)

class RetainedReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(ROOT/'catalogue/investigations/recorded-refinement-v1/plastic-report.json.gz','rt') as f:cls.report=json.load(f)

    def test_continuous_errors_and_order(self):
        result=analyze(self.report)
        self.assertAlmostEqual(result['reference'][4]['p'],285627.75153069664,places=6)
        self.assertAlmostEqual(result['levels'][-1]['max_pressure_pc_error_Pa'],4496.984914977278,places=6)
        for row in result['orders'][-3:]:self.assertGreater(row['order'],.95);self.assertLess(row['order'],1.05)
        self.assertLess(max(abs(row['e_error']) for level in result['levels'] for row in level['errors']),1e-13)

    def test_corrupted_evidence_rejected(self):
        report=copy.deepcopy(self.report)
        level=report['cases'][1]['levels'][-1]
        level['response']['points'][level['original_indices'][1]]['state'][0]+=100
        with self.assertRaises(ValueError):analyze(report)

    def test_native_followups(self):
        with gzip.open(ROOT/'catalogue/investigations/recorded-resolution-diagnosis-v1/mcc-native-followup.json.gz','rt') as f:followup=json.load(f)
        result=analyze_followups(self.report,followup)
        fine,tight=result['followups']
        self.assertEqual(fine['factor'],64)
        self.assertGreater(result['levels'][-1]['max_pressure_pc_error_Pa']/fine['max_pressure_pc_error_Pa'],1.9)
        self.assertLess(result['levels'][-1]['max_pressure_pc_error_Pa']/fine['max_pressure_pc_error_Pa'],2.1)
        self.assertLess(tight['max_difference_from_default_factor32_Pa'],.01)
        followup['runs'][0]['response']['integration_settings']['residual_tolerance']=.1
        with self.assertRaises(ValueError):analyze_followups(self.report,followup)

    def test_model_identity_and_nonfinite_interior_observation(self):
        changed=copy.deepcopy(self.report);changed['cases'][1]['model_sha256']='0'*64
        with self.assertRaises(ValueError):analyze(changed)
        for key,value in [('state',[0]*8),('state',[float('nan')]+[0]*8),('strain',[0]*5)]:
            with gzip.open(ROOT/'catalogue/investigations/recorded-resolution-diagnosis-v1/mcc-native-followup.json.gz','rt') as f:followup=json.load(f)
            followup['runs'][0]['response']['points'][1][key]=value
            with self.assertRaises(ValueError):analyze_followups(self.report,followup)

if __name__=='__main__':unittest.main()
