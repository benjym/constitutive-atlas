"""Contract-only checks: no integration, binaries, or model capability inference."""
import copy
import math
import json
from pathlib import Path
import unittest
from atlas.dsl import ValidationError
from atlas.recorded import validate_recorded_path


def example():
    return {'version':'experimental-recorded-path-0.1',
        'coordinate':{'name':'loading order','unit':'1','meaning':'path_order'},
        'initial_strain':[0]*6,
        'controls':[{'kind':'strain','coefficients':[int(i==j) for j in range(6)]} for i in range(6)],
        'knots':[{'coordinate':x,'targets':[0]*6} for x in (-2,0,1)]}


class RecordedPathContractTests(unittest.TestCase):
    def assert_invalid(self,s):
        with self.assertRaises(ValidationError):validate_recorded_path(s)

    def test_repository_drained_reversal_example(self):
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/'protocols/recorded-drained-reversal.json').read_text())
        self.assertIs(validate_recorded_path(spec),spec)
        self.assertEqual(spec['knots'][2]['targets'],spec['knots'][3]['targets'])
        self.assertLess(spec['knots'][2]['targets'][0],0.)

    def test_preserves_order_values_identity_and_input(self):
        s=example();s['knots'][1]['targets']=[1,0,0,0,0,0]
        s['knots'][2]['targets']=[0]*6
        before=copy.deepcopy(s)
        self.assertIs(validate_recorded_path(s),s)
        self.assertEqual(s,before)
        # Nonmonotonic and repeated targets represent reversals/holds.
        self.assertEqual(s['knots'][0]['targets'],s['knots'][2]['targets'])

    def test_closed_fields_and_physical_time_rejected(self):
        for location in ('root','coordinate','control','knot'):
            s=example();target={'root':s,'coordinate':s['coordinate'],
                'control':s['controls'][0],'knot':s['knots'][0]}[location]
            target['time']=0
            with self.subTest(location=location):self.assert_invalid(s)
        for key,value in [('unit','s'),('meaning','physical_time'),('name','  ')]:
            s=example();s['coordinate'][key]=value;self.assert_invalid(s)
        for key,value in [('model','x'),('parameters',{}),('initial',[])]:
            s=example();s[key]=value;self.assert_invalid(s)

    def test_strict_order_and_finite_coordinates(self):
        for coordinates in ([0,0,1],[0,2,1],[0,math.inf,2],[0,math.nan,2],[0,True,2]):
            s=example()
            for knot,x in zip(s['knots'],coordinates):knot['coordinate']=x
            self.assert_invalid(s)
        s=example();s['knots'][1]['coordinate']=math.nextafter(-2,math.inf)
        validate_recorded_path(s)

    def test_nonfinite_and_non_numeric_vectors(self):
        for bad in (math.nan, math.inf, -math.inf, 10**400, True, '0', None):
            for location in ('strain','coefficients','targets'):
                s=example()
                vector={'strain':s['initial_strain'],'coefficients':s['controls'][0]['coefficients'],
                        'targets':s['knots'][0]['targets']}[location]
                vector[0]=bad
                with self.subTest(value=bad,location=location):self.assert_invalid(s)

    def test_lengths_and_version(self):
        for location in ('strain','controls','coefficients','targets'):
            s=example();vector={'strain':s['initial_strain'],'controls':s['controls'],
                'coefficients':s['controls'][0]['coefficients'],'targets':s['knots'][0]['targets']}[location]
            vector.pop();self.assert_invalid(s)
        for count in (1,5002):
            s=example();s['knots']=[{'coordinate':i,'targets':[0]*6} for i in range(count)]
            self.assert_invalid(s)
        s=example();s['knots']=[{'coordinate':i,'targets':[0]*6} for i in range(5001)]
        validate_recorded_path(s)
        s=example();s['version']='0.1';self.assert_invalid(s)

    def test_zero_and_invalid_control_kind(self):
        for kind in ('strain','stress'):
            s=example();s['controls'][0]={'kind':kind,'coefficients':[0]*6};self.assert_invalid(s)
        s=example();s['controls'][0]['kind']='rate';self.assert_invalid(s)

    def test_all_strain_rank_dependency(self):
        s=example();s['controls'][1]['coefficients']=s['controls'][0]['coefficients'].copy()
        self.assert_invalid(s)
        s=example();s['controls'][5]['coefficients']=[1,1,1,1,1,0]
        self.assert_invalid(s)
        # Triangular non-coordinate controls remain valid.
        s=example()
        for i in range(6):s['controls'][i]['coefficients']=[int(j<=i) for j in range(6)]
        validate_recorded_path(s)

    def test_rank_scaling_and_near_dependence(self):
        s=example()
        for i,row in enumerate(s['controls']):
            row['coefficients']=[v*([1e-300,1e300][i%2]) for v in row['coefficients']]
        before=copy.deepcopy(s);validate_recorded_path(s);self.assertEqual(s,before)
        s=example();s['controls'][1]['coefficients']=[1,1e-16,0,0,0,0]
        self.assert_invalid(s)
        s['controls'][1]['coefficients'][1]=1e-10;validate_recorded_path(s)

    def test_mixed_controls_defer_stiffness_rank(self):
        s=example();s['controls'][1]={'kind':'stress','coefficients':s['controls'][0]['coefficients'].copy()}
        validate_recorded_path(s)
        for row in s['controls']:row['kind']='stress';row['coefficients']=[1,0,0,0,0,0]
        validate_recorded_path(s)

    def test_initial_target_consistency_is_deferred(self):
        s=example();s['knots'][0]['targets']=[100]*6
        validate_recorded_path(s)

if __name__=='__main__':unittest.main()
