"""Independent clay2013 source-rate checks; no integrated material admission."""
from decimal import Decimal, localcontext
import copy
import math
import random
import unittest

from atlas.dsl import Sym, ValidationError
from tools.inspect_clay2013_rate import load_fragment, validate_fragment, evaluate_rate
from tools.clay2013_invariant_reference import inspect as decimal_invariants
from tools.reference_clay2013_cartesian import rate as cartesian_rate, isotropic_pressure_rate

R2=math.sqrt(2.)
P=dict(phi_c=math.radians(30),lambda_star=.1,kappa_star=.02,N=1.,nu=.2)


def matrix(v):
    x,y,z,u,v,w=v.v
    return [[x,u/R2,w/R2],[u/R2,y,v/R2],[w/R2,v/R2,z]]


def mandel(a):
    return Sym((a[0][0],a[1][1],a[2][2],R2*a[0][1],R2*a[1][2],R2*a[0][2]))


def rotate(a):
    q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
    return [[math.fsum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3))
             for j in range(3)] for i in range(3)]


class ClayRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment=load_fragment()

    def reduced(self,sigma,de,e=.7,**changes):
        return evaluate_rate(self.fragment,sigma,de,e,**(P|changes))

    def close(self,a,b,rel=2e-11,floor=1e-8):
        for x,y in zip(a,b,strict=True):
            self.assertAlmostEqual(x,y,delta=max(floor,rel*max(abs(x),abs(y))))

    def test_source_identity_dimensions_and_fixed_reference_pressure(self):
        self.assertEqual(self.fragment['source']['sha256'],'21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281')
        for action in ['unit','pressure','source','order']:
            f=copy.deepcopy(self.fragment)
            if action=='unit': f['terms'][-3]['unit']='1'
            if action=='pressure':f['constants']['p_ref']['value']=1
            if action=='source':f['source']['sha256']='0'*64
            if action=='order':f['terms'][0],f['terms'][1]=f['terms'][1],f['terms'][0]
            # a and p are independent; swap a with j2 to test a true future reference.
            if action=='order':f['terms'][0],f['terms'][2]=f['terms'][2],f['terms'][0]
            with self.subTest(action=action),self.assertRaises(ValidationError):validate_fragment(f)

    def test_exact_isotropic_limits_loading_unloading_and_density(self):
        for pressure in [.1,.3,1e5,3e8]:
            for v in [-.003,0.,.003]:
                for e in [.4,.8,1.2]:
                    params=P|dict(N=math.log1p(e)+P['lambda_star']*math.log(pressure/1000))
                    sigma=Sym((pressure,)*3+(0.,)*3);de=Sym((v/3,)*3+(0.,)*3)
                    r=evaluate_rate(self.fragment,sigma,de,e,**params)
                    expected=pressure*v/(params['lambda_star'] if v>=0 else params['kappa_star'])
                    self.close(r['stress_rate'].v,(expected,)*3+(0.,)*3)
                    self.assertEqual(r['fm'],0.)
                    self.close(r['d'].v,(-1/math.sqrt(3),)*3+(0.,)*3, floor=2e-15)
                    self.assertAlmostEqual(r['e_rate'],-(1+e)*v,delta=1e-17)
                    ref=cartesian_rate(matrix(sigma),matrix(de),e,**params)
                    self.close(r['stress_rate'].v,mandel(ref['stress_rate']).v)
        # Away from the NCL, compare the independently derived density-ratio law.
        for e in [.2,.6,1.]:
            for v in [-.002,.002]:
                r=self.reduced(Sym((1e5,)*3+(0.,)*3),Sym((v/3,)*3+(0.,)*3),e)
                expected=isotropic_pressure_rate(1e5,e,v,**{k:P[k] for k in ['lambda_star','kappa_star','N']})
                self.close(r['stress_rate'].v,(expected,)*3+(0.,)*3)

    def test_cartesian_noncoaxial_rates_covariance_and_homogeneity(self):
        rng=random.Random(20131031)
        for _ in range(40):
            b=[[rng.uniform(-.4,.4) for _ in range(3)] for _ in range(3)]
            a=[[1e5*(sum(b[i][k]*b[j][k] for k in range(3))+(1 if i==j else 0)) for j in range(3)] for i in range(3)]
            sigma=mandel(a);de=Sym(tuple(rng.uniform(-.003,.003) for _ in range(6)))
            original=(sigma.v,de.v)
            r=self.reduced(sigma,de)
            ref=cartesian_rate(matrix(sigma),matrix(de),.7,**P)
            self.close(r['stress_rate'].v,mandel(ref['stress_rate']).v)
            for root,key in [('p','p'),('pe','pe'),('fm','Fm'),('fd','fd'),('fdA','fdA'),('omega','omega')]:
                self.assertAlmostEqual(r[root],ref['diagnostics'][key],delta=2e-11*max(1,abs(r[root])))
            rr=self.reduced(mandel(rotate(matrix(sigma))),mandel(rotate(matrix(de))))
            self.close(rr['stress_rate'].v,mandel(rotate(matrix(r['stress_rate']))).v)
            self.assertAlmostEqual(rr['e_rate'],r['e_rate'],delta=1e-17)
            for factor in [.01,3.]:
                scaled=self.reduced(sigma,de*factor)
                self.close(scaled['stress_rate'].v,(r['stress_rate']*factor).v)
                self.assertAlmostEqual(scaled['e_rate'],r['e_rate']*factor,delta=1e-17)
            self.assertEqual((sigma.v,de.v),original)

    def test_lode_endpoints_and_near_isotropic_continuity(self):
        de=Sym((.002,-.0005,.0003,.0004,-.0002,.0001))
        for values in [(180000.,100000.,100000.),(100000.,180000.,180000.)]:
            r=self.reduced(Sym(values+(0.,)*3),de)
            self.assertAlmostEqual(abs(r['cos3theta']),1.,delta=64*math.ulp(1.))
        base=self.reduced(Sym((1e5,)*3+(0.,)*3),de)['stress_rate']
        perturb=Sym((.4,-.1,-.3,R2*.2,-R2*.15,R2*.1))
        previous=float('inf')
        for epsilon in [1e-2,1e-4,1e-6,1e-8,1e-10,1e-12]:
            sigma=Sym((1e5,)*3+(0.,)*3)+perturb*(1e5*epsilon)
            r=self.reduced(sigma,de)
            error=max(abs(x-y) for x,y in zip(r['stress_rate'].v,base.v))
            self.assertLess(error,previous);previous=error
            self.assertGreater(r['fm'],0.)
            self.assertTrue(-1-64*math.ulp(1.)<=r['cos3theta']<=1+64*math.ulp(1.))
        self.assertLess(previous,1e-7)

    def test_stable_invariants_agree_with_high_precision_actual_float_inputs(self):
        # Evaluate Decimal at the exact supplied binary64 values, rather than
        # comparing rounded states with ideal pre-rounding perturbations.
        de=Sym((.001,0.,0.,0.,0.,0.))
        for epsilon in [1e-2,1e-6,1e-10,1e-12]:
            sigma=Sym((1e5*(1+2*epsilon),1e5*(1-epsilon),1e5*(1-epsilon),0.,0.,0.))
            r=self.reduced(sigma,de)
            with localcontext() as context:
                context.prec=180
                exact=[[Decimal.from_float(v) for v in row] for row in matrix(sigma)]
                ref=decimal_invariants(exact)
            self.assertAlmostEqual(r['fm']/float(ref['Fm_stable']),1.,delta=3e-14)
            self.assertAlmostEqual(r['cos3theta'],float(ref['lode_cosine']),delta=3e-14)

    def test_zero_rate_and_rejected_domains_leave_inputs_unchanged(self):
        sigma=Sym((1e5,1.2e5,1.4e5,2000.,-1000.,3000.));zero=Sym((0.,)*6)
        r=self.reduced(sigma,zero)
        self.assertEqual(r['stress_rate'].v,zero.v);self.assertEqual(r['e_rate'],0.)
        for changes in [dict(e=-.1),dict(lambda_star=.01),dict(nu=.5),dict(phi_c=0.),dict(phi_c=True),dict(N=1000.),dict(N=-1000.),dict(N=65.)]:
            args=dict(sigma=sigma,stretching=zero,e=.7,**P)|changes
            with self.subTest(changes=changes),self.assertRaises(ValidationError):evaluate_rate(self.fragment,**args)
        for bad in [Sym((0.,)*6),Sym((-1.,1.,1.,0.,0.,0.)),Sym((1.,1.,1.,3.,0.,0.)),Sym((float('nan'),)*6),[1.,2.]]:
            with self.subTest(stress=bad),self.assertRaises(ValidationError):self.reduced(bad,zero)
        with self.assertRaises(ValidationError):self.reduced(Sym((1.,1.,1.,1e-300,0.,0.)),zero)
        self.assertEqual(sigma.v,(1e5,1.2e5,1.4e5,2000.,-1000.,3000.))


if __name__=='__main__':unittest.main()
