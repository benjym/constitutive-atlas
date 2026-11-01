"""Independent source-equation check; does not import any Atlas implementation.

Acceptance frozen in this script before first execution: central finite difference
of yield+mixed control, relative/absolute normalized error <= 2e-6, delta=1e-7.
The perturbed image pressure follows the original Eq12 tangent. This is a local
algebra check only, not qualification of finite paths or any runtime.
"""
import json
import math

TOL = 2e-6
DELTA = 1e-7


def ratio(eta, M, N):
    return math.exp(eta / M - 1) if N == 0 else ((1-N*eta/M)/(1-N))**((N-1)/N)


def root(pi, C, K, M, N):
    # Solve original yield inversion and external stress constraint, independently
    # of the reduced eta differential equation.
    lo, hi = -0.5, 2.0
    for _ in range(100):
        eta = (lo+hi)/2
        image = C/(1-K*eta)*ratio(eta, M, N)
        if image < pi:
            lo = eta
        else:
            hi = eta
    return (lo+hi)/2


checks = []
for N in (0, .2, .39):
    for K in (0, .2, 1/3):
        for eta in (.2, .8, 1.5):
            for changed in (False, True):
                M, h, p, psi_i = 1.25, 40., 100000., -.05
                r = ratio(eta, M, N)
                pi = p*r
                C = p*(1-K*eta)
                Cs = .02*C if changed else 0.
                Ks = .1 if changed else 0.
                rL = math.exp(-3.5*psi_i/M) if N == 0 else (1+3.5*psi_i*N/M)**((N-1)/N)
                pi_s = h*(p*rL-pi)
                minus = root(pi-DELTA*pi_s, C-DELTA*Cs, K-DELTA*Ks, M, N)
                plus = root(pi+DELTA*pi_s, C+DELTA*Cs, K+DELTA*Ks, M, N)
                numerical = (plus-minus)/(2*DELTA)
                Y = 1. if N == 0 else (1/r)**(N/(1-N))
                B = 1-K*eta
                reduced = M*Y*B/(B+K*M*Y)*(h*(rL/r-1)-Cs/C-Ks*eta/B)
                error = abs(numerical-reduced)/max(1., abs(reduced))
                assert error <= TOL, (N, K, eta, changed, error)
                checks.append(error)
print(json.dumps({"scope": "independent local source yield/control tangent only", "checks": len(checks), "delta": DELTA, "tolerance": TOL, "maximum_normalized_error": max(checks), "passed": True}, indent=2))
