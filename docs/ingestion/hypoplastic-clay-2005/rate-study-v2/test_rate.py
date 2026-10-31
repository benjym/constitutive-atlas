"""Python-only source/interpreter witnesses; no compiled artifact execution."""
import copy,json,math,unittest
from pathlib import Path
import reference as ref
from atlas.model import load,defaults,prepare_increment,interpret,evaluation_environment

HERE=Path(__file__).resolve().parent


class SourceRates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=load(HERE/'model.json');cls.params=defaults(cls.model)

    def env(self,z,E,params=None):
        state=dict(sigma=z[:6],e=z[6]);p=self.params|(params or {})
        prepare_increment(self.model,state,E,p)
        return evaluation_environment(self.model,state,state,E,p)

    def test_frozen_reference_replay(self):
        self.assertEqual(json.loads((HERE/'reference.json').read_text()),ref.build_reference())

    def test_all_seven_source_rates(self):
        for c in ref.build_reference()['cases']:
            with self.subTest(c=c['id']):
                r=self.env(c['state'],c['increment'],c['parameters']);got=list(r['stress_rate'].v)+[r['e_rate']]
                if not c['diagnostics']['exact_sphere']:self.assertGreaterEqual(c['diagnostics']['j2'],1e-8)
                for a,b in zip(got[:6],c['expected'][:6]):self.assertLessEqual(abs(a-b),ref.POLICY['stress_absolute_floor_Pa']+ref.POLICY['stress_relative_to_scale']*c['stress_scale'])
                self.assertLessEqual(abs(got[6]-c['expected'][6]),ref.POLICY['void_absolute_floor']+ref.POLICY['void_relative_to_scale']*c['void_scale'])

    def test_exact_isotropy_and_initial_ncl_signed_tangents(self):
        for p in (.3,1e5,9247007.657539926):
            e=math.expm1(self.params['N']-self.params['lambda_star']*math.log(p/1000));z=[p]*3+[0]*3+[e]
            for v in (-.003,0,.003):
                r=self.env(z,[v/3]*3+[0]*3)
                self.assertEqual(r['j2'],0);self.assertEqual(r['F'],1)
                slope=self.params['lambda_star']if v>0 else self.params['kappa_star']
                for x in r['stress_rate'].v[:3]:self.assertAlmostEqual(x/p,v/slope,delta=3e-15)
                self.assertEqual(r['e_rate'],-(1+e)*v)

    def test_rotation_covariance_independent_cartesian(self):
        by={c['id']:c for c in ref.build_reference()['cases']}
        for c in by.values():
            if 'rotation_of'not in c['tags']:continue
            parent=by[c['tags']['rotation_of']];want=ref.to_mandel(ref.rotate(ref.from_mandel(parent['expected'][:6]),c['tags']['rotation']))
            for a,b in zip(want,c['expected'][:6]):self.assertLessEqual(abs(a-b),1e-10+2e-12*c['stress_scale'])
            self.assertAlmostEqual(parent['expected'][6],c['expected'][6],delta=1e-15)

    def test_mandel_all_shears(self):
        for slot,(i,j)in enumerate(((0,1),(1,2),(0,2)),3):
            v=[0.]*6;v[slot]=math.sqrt(2);a=ref.from_mandel(v)
            self.assertAlmostEqual(a[i][j],1);self.assertAlmostEqual(ref.dot(a,a),sum(x*x for x in v))
            self.assertEqual(ref.to_mandel(a),v)

    def test_invalid_domains_both_paths(self):
        c=ref.cases()[0]
        invalid=[(c['state'],c['increment'],dict(phi_c=0)),(c['state'],c['increment'],dict(kappa_star=.2)),(c['state'],c['increment'],dict(r=0)),(c['state'][:6]+[-.1],c['increment'],{}),([1e5,1e5,-1e5,0,0,0,.8],c['increment'],{}),([0]*6+[.8],c['increment'],{}),(c['state'],c['increment'],dict(kappa_star=.1)),(c['state'],c['increment'],dict(N=-10,lambda_star=.0001,kappa_star=.00001))]
        for z,E,p in invalid:
            with self.subTest(z=z,p=p):
                with self.assertRaises((ValueError,ArithmeticError)):self.env(z,E,p)
                with self.assertRaises((ValueError,ArithmeticError)):ref.rate(ref.from_mandel(z[:6]),ref.from_mandel(E),z[6],**(c['parameters']|p))

    def test_near_sphere_floor_rejection_not_isotropic_substitution(self):
        E=[.001,0,0,0,0,0]
        self.env([1e5]*3+[0]*3+[.8],E)
        for shear in (1e-60,1e-200):
            z=[1e5]*3+[shear,0,0,.8]
            with self.assertRaises((ValueError,ArithmeticError)):self.env(z,E)
            with self.assertRaises((ValueError,ArithmeticError)):ref.rate(ref.from_mandel(z[:6]),ref.from_mandel(E),z[6],**{n:self.params[n]for n in ref.SOURCE_PARAMETERS})
        # Explicit just-below/above support-floor cases, classified by actual binary64 j2.
        for factor,accepted in ((.5,False),(2.,True)):
            shear=300000*math.sqrt(factor*self.params['j2_floor'])
            z=[1e5]*3+[shear,0,0,.8]
            if accepted:
                r=self.env(z,E);self.assertGreaterEqual(r['j2'],self.params['j2_floor'])
            else:
                with self.assertRaises(ValueError):self.env(z,E)
        # Supported but not accuracy-certified: no determinant-oracle endorsement here.
        r=self.env([1e5]*3+[1e-40,0,0,.8],E)
        self.assertGreater(r['j2'],self.params['j2_floor']);self.assertFalse(r['j2']==0)

    def test_frozen_finite_invalids_reject_in_both_paths(self):
        for c in json.loads((HERE/'invalid-cases.json').read_text())['cases']:
            with self.subTest(c=c['id']):
                with self.assertRaises((ValueError,ArithmeticError)):self.env(c['state'],c['increment'],c['parameters'])
                with self.assertRaises((ValueError,ArithmeticError)):ref.evaluate(c)

    def test_boolean_and_nonfinite_rejections(self):
        c=ref.cases()[0]
        for value in (True,float('nan'),float('inf')):
            with self.assertRaises(ValueError):self.env(c['state'],c['increment'],dict(r=value))
            with self.assertRaises(ValueError):ref.rate(ref.from_mandel(c['state'][:6]),ref.from_mandel(c['increment']),c['state'][6],**(c['parameters']|dict(r=value)))

    def test_no_history_reset_and_no_mutation(self):
        c=ref.cases()[0];z=copy.deepcopy(c['state']);E=copy.deepcopy(c['increment']);before=copy.deepcopy((z,E));self.env(z,E)
        self.assertEqual((z,E),before);self.assertNotIn('increment_reset',self.model);self.assertEqual(len(self.model['state']),2)
        bad=z[:6]+[-1.];parent=copy.deepcopy(bad)
        with self.assertRaises(ValueError):self.env(bad,E)
        self.assertEqual(bad,parent)


if __name__=='__main__':unittest.main()
