#!/usr/bin/env python3
"""Independent Decimal bisection of uneliminated OCC finite equations.

The oracle uses packing/yield/flow equations, never the proposed x_s/x_c
elimination as its solve. The candidate is separately evaluated for comparison.
No compiled artifact or production model is imported.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import hashlib
import json
import math

getcontext().prec = 90
HERE = Path(__file__).resolve().parent
CONTRACT = HERE.parent / 'CONTRACT.md'
M, K, LA, GA = map(D, ('1.2', '.04', '.2', '2.5'))
TOL = D('1e-65')


def bisect(f, lo, hi):
    assert f(lo) <= 0 <= f(hi)
    for _ in range(300):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def oracle(vn, xn, E, r, qn):
    v = vn / (1 + E)
    def packing(x):
        return 1 + (GA - (v + K*x)) / (LA-K)
    # Locate hydrostatic intersection from the source packing and q=0 yield.
    hydro = bisect(lambda x: x - packing(x), D('-10000'), D('10000'))
    def balance(x):
        return K/v*(x-xn) + r*M*(1+x-packing(x)) - E
    if balance(hydro) <= 0:
        x, q = hydro, D(0)
        L = (E-K/v*(x-xn))/M
        branch = 'corner'
    elif r:
        lo = hydro - 1
        while balance(lo) > 0:
            lo = hydro - 2*(hydro-lo)
        x = bisect(balance, lo, hydro)
        q = -M*x.exp()*(x-packing(x))
        L, branch = r, 'smooth'
    else:
        # Exact source recovery, independent of proposed pressure formula.
        x = xn + (vn-v)/K
        capacity = -M*x.exp()*(x-packing(x))
        q = min(qn, capacity)
        L, branch = D(0), 'interior-projection'
    c = packing(x)
    A = M*(1+x-c)
    residuals = [v-vn+v*E, E-K/v*(x-xn)-L*A,
                 v+K*x-vn-K*xn+v*L*A]
    F = q + M*x.exp()*(x-c)
    if L:
        residuals.append(F)
    assert F <= TOL
    assert L >= -TOL
    if branch == 'corner':
        assert L + TOL >= r
    assert max(map(abs, residuals)) < TOL
    return v, x, q, L, branch, max(map(abs, residuals))


def eliminated(vn, xn, E, r, qn):
    v = vn/(1+E)
    alpha, beta = K/v, M*r/(LA-K)
    xs = (E+alpha*xn+beta*(GA-v))/(alpha+beta*LA)
    xc = (GA+LA-K-v)/LA
    x = min(xs, xc)
    Q = M*x.exp()*LA/(LA-K)*(xc-x)
    if xs > xc or (r and xs == xc):
        return v, x, D(0), (E-alpha*(xc-xn))/M
    return v, x, Q if r else min(qn,Q), r


def main():
    results = []
    for xn in map(D, ('-2','0','4','8')):
        for gap in map(D, ('.05','1','2','3')):
            vn = GA+LA-K-LA*xn-(LA-K)*gap
            qn = M*xn.exp()*gap*D('.6')
            assert vn > 0
            for E in map(D, ('-.1','-.001','0','.001','.1')):
                for r in map(D, ('0','1e-40','.0001','.01','.5')):
                    reference = oracle(vn,xn,E,r,qn)
                    candidate = eliminated(vn,xn,E,r,qn)
                    err = max(abs(a-b) for a,b in zip(reference[:4],candidate))
                    assert err < TOL, (xn,gap,E,r,err)
                    results.append(dict(xn=str(xn), gap=str(gap), E=str(E), r=str(r),
                                        branch=reference[4], error=str(err),
                                        residual=str(reference[5])))
    # The continuous critical state is an exact mechanism of these endpoints.
    xn = D(4)
    vn = GA-LA*xn
    qn = M*xn.exp()
    critical = oracle(vn,xn,D(0),D('.2'),qn)
    assert abs(critical[1]-xn)<TOL and abs(critical[2]-qn)<TOL
    # Explicit dry-side undrained relaxation and packing softening.
    xn = D(4)
    gap = D('1.1')
    vn = GA+LA-K-LA*xn-(LA-K)*gap
    qn = M*xn.exp()*gap
    dry = oracle(vn,xn,D(0),D('.01'),qn)
    oldc = xn+gap
    newc = 1+(GA-dry[0]-K*dry[1])/(LA-K)
    assert dry[1]>xn and newc<oldc and dry[2]<qn
    # Binary64 witness is analytical: finite stress jump with norm underflow.
    tiny = 1e-200
    naive_norm = math.sqrt(tiny*tiny)
    assert tiny != 0 and naive_norm == 0
    pressure = 50000.0
    pc = 100000.0
    jump_limit = float(M)*pressure*math.log(pc/pressure)
    output = dict(status='pass', precision=90, tolerance=str(TOL),
                  contract_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                  cases=results, count=len(results),
                  critical=dict(x=str(critical[1]),q=str(critical[2])),
                  dry_side=dict(x=str(dry[1]),q=str(dry[2]),c=str(newc)),
                  retained_initial_check_failure='An initial extra assertion q_new<q_n at gap=2 failed; that assertion is not source-mandated. Dry-side packing softening need not imply decreasing q under undrained loading. Revised explicit declining-q case uses gap=1.1, with no change to oracle or tolerances.',
                  tiny_witness=dict(nonzero_mandel_shear=tiny, naive_norm=naive_norm,
                                    positive_q_limit_Pa=jump_limit,
                                    interpretation='identity is a finite wrong stress, not negligible error'))
    (HERE/'constraint-results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='cases'},indent=2))


if __name__ == '__main__':
    main()
