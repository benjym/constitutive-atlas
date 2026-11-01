"""Independent Cartesian spring/dashpot reference, standard library only.

No Atlas imports or generated constitutive expressions. Inputs/outputs use Mandel
transport, but calculations below use 3x3 Cartesian tensors and Lame's first
parameter. This is an equation oracle, never a production material kernel.
"""
import math


def cart(a):
    r=math.sqrt(2.)
    return [[a[0],a[3]/r,a[5]/r], [a[3]/r,a[1],a[4]/r], [a[5]/r,a[4]/r,a[2]]]


def mandel(a):
    r=math.sqrt(2.)
    return [a[0][0],a[1][1],a[2][2],r*a[0][1],r*a[1][2],r*a[0][2]]


def source_stress(eps,rate,K,G,tau):
    e,d=cart(eps),cart(rate)
    tr_e=sum(e[i][i] for i in range(3));tr_d=sum(d[i][i] for i in range(3))
    lam=K-2*G/3;eta=G*tau
    return mandel([[2*G*e[i][j]+2*eta*d[i][j]+(lam*tr_e-2*eta*tr_d/3)*(i==j)
                    for j in range(3)] for i in range(3)])


def constant_rate(eps0,rate,t):
    return [e+t*d for e,d in zip(eps0,rate)]


def deviatoric_stress_ramp(e0,s0,A,t,G,tau):
    """For each deviatoric component: stress(t)=s0+A*t.

    Integrating-factor solution of the series-free scalar parallel-element law
    tau*de/dt + e = stress/(2G). Derivative is derived analytically, not by
    observing the production stress expression.
    """
    q=math.exp(-t/tau);m=-math.expm1(-t/tau)
    e=[x*q+s*m/(2*G)+a*(t-tau*m)/(2*G) for x,s,a in zip(e0,s0,A)]
    d=[-x*q/tau+s*q/(2*G*tau)+a*m/(2*G) for x,s,a in zip(e0,s0,A)]
    return e,d
