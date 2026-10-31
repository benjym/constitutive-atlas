"""Independent bounded algebra witnesses, not a constitutive implementation.
Run: python3 check_packet.py [--write]; no source PDFs or production Atlas imports.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent

def run():
    rows = []
    def witness(name, locator, inputs, outputs, claim):
        rows.append(dict(id=name, locator=locator, inputs=inputs, outputs=outputs, interpretation=claim))
    # Euclidean matrix contraction independently matches Mandel2, not vector xy.
    xx, yy, xy = 3., -2., 4.
    matrix_norm = math.sqrt(xx*xx+yy*yy+2*xy*xy)
    mandel_norm = math.hypot(xx, yy, math.sqrt(2)*xy)
    assert math.isclose(matrix_norm, mandel_norm, rel_tol=1e-15)
    witness('2D-shear-norm','Eqs1-8/15 pp16-19',dict(xx=xx,yy=yy,xy=xy),dict(matrix_norm=matrix_norm,mandel_norm=mandel_norm), 'Mandel2 needs sqrt(2) shear. This does not establish an Atlas6 embedding.')
    sigma = [100., 60., 0.]
    p2 = (sigma[0]+sigma[1])/2
    p3 = sum(sigma)/3
    ev = .03
    trace2_e = (ev-2*ev/3)
    assert p2 != p3 and math.isclose(trace2_e, ev/3)
    witness('2D-vs-3D','Eqs1-8 pp16-17',dict(sigma=sigma,ev=ev),dict(p2=p2,p3_if_zero_zz=p3,trace2_displayed_e=trace2_e), 'Zero-zz 3D stress mean and trace-free2 strain are different laws.')
    # Exact CSR initial numerator divided by itself equals one.
    M, Mb, csr0, power = 1., 1.2, .5, 4.
    numerator = 1-csr0*(M/Mb)**power
    csr = min(1., numerator/numerator)
    assert csr == 1.
    witness('frozen-CSR','Eq24 p22',dict(M=M,Mb=Mb,CSR0=csr0,mSR=power),dict(initial_numerator=numerator,CSR_initial=csr), 'Freeze the denominator at preparation; recomputing it every step destroys CSR evolution.')
    # Independent l'Hopital limit of the DENSE Eq45 curve, not a branch choice.
    phi = math.radians(33)
    M = 2*math.sin(phi)
    nb, nd = .5, .1
    limit = nb/(.8*(nb+nd)*math.sqrt(1-M*M/4))
    def ado(xi):
        mb, md = M*math.exp(-nb*xi), M*math.exp(nd*xi)
        return (math.asin(mb/2)-math.asin(M/2))/(.4*(mb-md))
    samples = [ado(-10.**(-k)) for k in (3,4,5)]
    assert abs(samples[-1]-limit) < abs(samples[0]-limit) and abs(samples[-1]-limit) < 1e-4
    witness('dense-critical-limit','Eq45 p27; Table3.2 step3',dict(phi_degrees=33,nb=nb,nd=nd,xi=[-.001,-.0001,-.00001]),dict(samples=samples,analytical_dense_limit=limit,loose_default=1.24), 'Eq45 is 0/0 at exact xi=0; dense limit does not choose startup equality or loose branch.')
    p, pmin, pmin2 = 5000., 500., 5000.
    body, table = 1/(1+(pmin2/p)**2), 1/(1+(pmin/p)**2)
    assert body == .5 and abs(body-table) > .4
    witness('low-pressure-scale-conflict','Eq74 p35 vs Table2.1 p43',dict(p=p,pmin=pmin,pmin2=pmin2),dict(body=body,summary=table), 'Distinct printed scales give distinct dilation factors; no variant selected.')
    ratio, fmin = .5, .04
    body, table = fmin+(1-fmin)*ratio**2, fmin+(1-fmin)*ratio
    assert math.isclose(body,.28) and math.isclose(table,.52)
    witness('postshake-square-conflict','Eq89 p38 vs Table2.1 p45',dict(pressure_ratio=ratio,Fmin=fmin),dict(body=body,summary=table), 'Square versus linear is consequential even away from zero denominators.')
    D, depv, cz = -.2, -.002, 1.
    body = -cz*max(-depv,0)/D
    table = -cz*depv/D
    assert body > 0 and table < 0 and body == -table
    witness('fabric-sign-conflict','Eq57 p30 vs Table3.1 step14 p66',dict(D=D,devpl=depv,cz=cz,zcum=0.,zmax=1.),dict(body_multiplier=body,table_multiplier=table), 'Coefficients of (zmax*n+z) have opposite signs on this negative-D loading. Not a complete admissible material state.')
    pzp, pmin = 100., 1.
    def pressure_factor(p):
        numerator = -max(-(pzp-p),0.)
        return numerator/(numerator+pmin)
    assert pressure_factor(99.) == 0 and pressure_factor(100.5) == -1.
    try:
        pressure_factor(101.)
        raise AssertionError('literal pole not detected')
    except ZeroDivisionError:
        pass
    witness('pressure-factor-pole','Eq64 p32',dict(pzp=pzp,pmin=pmin),dict(f_at_99=pressure_factor(99.),f_at_100_5=pressure_factor(100.5),pole_at_p=101.), 'Literal positive-pressure expression is not a bounded interpolation; sign adapter unresolved.')
    dapp, dtrue, dprev = 0., 0., 0.
    assert dprev <= 0 and not dprev < 0
    witness('initial-reversal-domain','Eq20 p21/Eq38 p25; Table3.2 step5',dict(dapp=dapp,dtrue=dtrue,dprev=dprev),dict(Eq38_enters_division=True,division_defined=False,strict_negative_branch=False), 'Coincident initial anchors do not define the selected zero-over-zero limit.')
    assert 101300/200 == 506.5
    assert abs(min(10.,5+25*(.15-.35))) < 1e-14
    witness('default-parameter-boundaries','p35; pp60-61; Table4.2 pp77-78',dict(pA=101300.,DR_initial=.15),dict(pA_over_200=101300/200,nominal_floor_Pa=500.,CDR=min(10.,5+25*(.15-.35))), 'A nominal floor is distinct from exact atmosphere scaling; printed CDR rule lacks a positive lower bound.')
    # Deliberately synthetic lagged constitutive coefficient: not PM4Sand solver.
    # Stored D=0 initially, D<-cumulative load only at caller commit.
    def lagged(parts):
        total, stress, D = 0., 0., 0.
        for dx in parts:
            stress += (1-D)*dx
            total += dx
            D = total
        return stress
    one, two = lagged([1.]), lagged([.5,.5])
    assert one == 1. and two == .75
    witness('caller-lag-partition','Sec3.2 p59; Table3.1 steps6/12',dict(initial_D=0.,total_load=1.),dict(one_caller=one,two_callers=two), 'Synthetic example shows why changing caller refresh frequency changes a lagged law; not a source-model numerical prediction.')
    return dict(schema_version='0.1',kind='bounded-independent-algebra-witnesses',model='PM4Sand2D3.3',groups=len(rows),all_passed=True,scope='Scalar/tensor algebra only; no production DSL, host, compiled model or author implementation evaluated.',checks=rows)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    result=run()
    data=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.write:
        (HERE/'check-results.json').write_text(data)
    else:
        assert (HERE/'check-results.json').read_text()==data, 'retained witness results differ'
    print(f"{result['groups']} bounded algebra groups passed; retained results match")
