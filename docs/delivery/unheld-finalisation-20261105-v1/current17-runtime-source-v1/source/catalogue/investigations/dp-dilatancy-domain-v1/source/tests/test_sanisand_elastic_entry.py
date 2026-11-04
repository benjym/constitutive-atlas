"""Exact elastic path and first-yield research checks; no native execution."""
import math
import unittest

from atlas.dsl import I, Sym, ValidationError, dev, dot, trace
from tools.sanisand_elastic_entry import elastic_point, first_yield


def rk4(sigma, e, strain, steps):
    # Independently integrate the original instantaneous elasticity, without the
    # transformed-pressure formula used in the exact reference.
    def rate(y):
        p=sum(y[:3])/3
        G=125*1e5*(2.97-y[6])**2/(1+y[6])*math.sqrt(p/1e5)
        K=2*1.05/(3*.9)*G
        volume=sum(strain.v[:3])
        return [2*G*(v-(volume/3 if i<3 else 0))+(K*volume if i<3 else 0)
                for i,v in enumerate(strain.v)]+[-(1+y[6])*volume]
    y=[*sigma.v,e]
    for _ in range(steps):
        h=1/steps
        a=rate(y);b=rate([v+h*w/2 for v,w in zip(y,a)])
        c=rate([v+h*w/2 for v,w in zip(y,b)])
        d=rate([v+h*w for v,w in zip(y,c)])
        y=[v+h*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(y,a,b,c,d)]
    return Sym(tuple(y[:6])),y[6]


def rotate(t):
    # Oblique Cartesian Q A Q^T independently of the elasticity implementation.
    c,s=math.cos(.37),math.sin(.37)
    Q=((c,-s,0),(s,c,0),(0,0,1));r=math.sqrt(2)
    a,b,d,u,v,w=t.v
    A=((a,u/r,w/r),(u/r,b,v/r),(w/r,v/r,d))
    B=[[sum(Q[i][k]*A[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return Sym((B[0][0],B[1][1],B[2][2],r*B[0][1],r*B[1][2],r*B[0][2]))


class ElasticEntryTests(unittest.TestCase):
    def near(self,a,b,atol=1e-8,rtol=2e-11):
        av=a.v if isinstance(a,Sym) else (a,)
        bv=b.v if isinstance(b,Sym) else (b,)
        for x,y in zip(av,bv):self.assertLessEqual(abs(x-y),atol+rtol*abs(y))

    def test_zero_volume_and_small_volume_limit(self):
        sigma=I*1e5;strain=Sym((2e-4,-1e-4,-1e-4,3e-4,-2e-4,1e-4))
        G=125*1e5*(2.97-.7)**2/1.7
        exact=elastic_point(sigma,.7,strain)
        self.near(exact[0],sigma+strain*(2*G));self.assertEqual(exact[1],.7)
        for volume in [1e-12,-1e-12,1e-18,-1e-18]:
            got=elastic_point(sigma,.7,strain+I*(volume/3))
            self.near(got[0],exact[0],atol=1e-3)
        # Near the excluded zero-stiffness density, do not lose f(e) by
        # subtracting large nearly equal terms in the closed-form average.
        near_boundary=2.97-1e-10
        shear=Sym((0.,0.,0.,1.,0.,0.))
        got=elastic_point(sigma,near_boundary,shear)
        expected=2*125*1e5*(2.97-near_boundary)**2/(1+near_boundary)
        self.near(got[0].v[3],expected,atol=0,rtol=1e-14)

    def test_matches_independent_rate_integration_and_refinement(self):
        sigma=Sym((1.1e5,.9e5,1e5,200.,-500.,100.))
        for strain in [Sym((.006,.003,.001,.002,-.001,.003)),
                       Sym((-.002,-.001,-.001,.002,.001,-.001)),
                       Sym((.003,-.002,-.001,.003,-.002,.001))]:
            exact=elastic_point(sigma,.7,strain)
            errors=[]
            for steps in [8,16,32,64]:
                got=rk4(sigma,.7,strain,steps)
                errors.append(max(abs(a-b) for a,b in zip(got[0].v,exact[0].v)))
            if errors[0]>1e-6:
                self.assertLess(errors[1],errors[0]/10)
                self.assertLess(errors[2],errors[1]/10)
            self.near(got[0],exact[0],atol=.003,rtol=1e-8)
            self.near(got[1],exact[1])

    def test_partition_covariance_and_units(self):
        sigma=Sym((1.1e5,.9e5,1e5,200.,-500.,100.))
        strain=Sym((.003,.002,-.001,.002,-.001,.001))
        exact=elastic_point(sigma,.7,strain)
        a=elastic_point(sigma,.7,strain,.37)
        b=elastic_point(a[0],a[1],strain*(1-.37))
        self.near(b[0],exact[0]);self.near(b[1],exact[1])
        rotated=elastic_point(rotate(sigma),.7,rotate(strain))
        self.near(rotated[0],rotate(exact[0]));self.near(rotated[1],exact[1])
        for scale in [1e-3,1e3]:
            other=elastic_point(sigma*scale,.7,strain,p_at=1e5*scale)
            self.near(other[0]/scale,exact[0]);self.near(other[1],exact[1])

    def test_constant_volume_first_yield_analytic(self):
        sigma=I*1e5;alpha=Sym((0.,)*6)
        strain=Sym((.0001,-.00005,-.00005,.0002,-.0001,.00005))
        G=125*1e5*(2.97-.7)**2/1.7
        expected=math.sqrt(2/3)*.01*1e5/(2*G*math.sqrt(dot(strain,strain)))
        event=first_yield(sigma,.7,alpha,strain)
        self.assertLessEqual(event['lower']['fraction'],expected)
        self.assertGreaterEqual(event['upper']['fraction'],expected)
        self.assertLessEqual(event['upper']['fraction']-event['lower']['fraction'],1e-12)
        self.assertLess(event['lower']['residual'],0)
        self.assertGreaterEqual(event['upper']['residual'],0)
        self.assertIsNone(first_yield(sigma,.7,alpha,strain*(expected*.5)))

    def test_mixed_yield_partition_rotation_and_unloading(self):
        sigma=I*1e5;alpha=Sym((0.,)*6)
        strain=Sym((.001,.0003,-.0001,.0004,-.0002,.0001))
        event=first_yield(sigma,.7,alpha,strain)
        lo,hi=event['lower']['fraction'],event['upper']['fraction']
        self.assertLess(lo,hi);self.assertGreater(lo,0)
        rotated=first_yield(rotate(sigma),.7,rotate(alpha),rotate(strain))
        self.near(rotated['upper']['fraction'],hi,atol=2e-12)
        before=elastic_point(sigma,.7,strain,lo/2)
        rest=first_yield(before[0],before[1],alpha,strain*(1-lo/2))
        self.near(lo/2+(1-lo/2)*rest['upper']['fraction'],hi,atol=2e-12)
        # Start near one cone side and unload through the opposite side.
        radius=math.sqrt(2/3)*.01
        on=Sym((1e5,1e5,1e5,1e5*radius,0.,0.))
        inward=Sym((0.,0.,0.,-1e-4,0.,0.))
        crossing=first_yield(on,.7,alpha,inward)
        self.assertGreater(crossing['lower']['fraction'],0)
        self.assertIsNone(first_yield(on,.7,alpha,inward*.01))
        outward=first_yield(on,.7,alpha,-inward)
        self.assertLessEqual(outward['upper']['fraction'],1e-12)
        self.assertIsNone(first_yield(on,.7,alpha,Sym((0.,)*6)))

    def test_rejects_domains_and_failed_search_without_mutation(self):
        sigma=I*1e5;strain=Sym((.001,0.,0.,0.,0.,0.));alpha=Sym((0.,)*6)
        saved=(sigma,e:=.7,strain,alpha)
        for kwargs in [dict(e=-1),dict(fraction=2),dict(G0=0),dict(nu=.5),dict(p_at=0)]:
            arguments=dict(sigma=sigma,e=e,strain=strain);arguments.update(kwargs)
            with self.assertRaises(ValidationError):elastic_point(**arguments)
        with self.assertRaises(ValidationError):elastic_point(sigma,.7,I*(-1.))
        with self.assertRaises(ValidationError):elastic_point(sigma,.7,I*1.)
        with self.assertRaises(ValidationError):first_yield(sigma,.7,alpha,strain,max_iterations=1)
        with self.assertRaises(ValidationError):first_yield(sigma,.7,I,strain)
        with self.assertRaises(ValidationError):first_yield(sigma,.7,alpha,strain,fraction_tolerance=0)
        exterior=Sym((1e5,1e5,1e5,2e3,0.,0.))
        with self.assertRaises(ValidationError):first_yield(exterior,.7,alpha,strain)
        self.assertEqual(saved,(sigma,e,strain,alpha))


if __name__=='__main__':unittest.main()
