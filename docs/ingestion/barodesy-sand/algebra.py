"""Independent bounded diagonal/scalar checks; no full tensor model or integrator."""
import argparse
import json
import math
from pathlib import Path

PARAMETERS = dict(c1=-1.0246, c2=1., c3=-2.3, c4=465., c5=28., ec0=.87, emin=.35)


def csl(sigma, p=PARAMETERS):
    if not math.isfinite(sigma) or sigma < 0:
        raise ValueError('nonnegative finite stress norm required')
    b = (p['ec0']-p['emin'])/(p['ec0']+1)*math.exp(
        -(1+p['emin'])/p['c5']*math.log1p(p['c5']*sigma/p['c4']))
    ec = (p['emin']+b)/(1-b)
    derivative = -(1+ec)*(ec-p['emin'])/(p['c4']+p['c5']*sigma)
    return ec, derivative


def diagonal_rate(t, e, d, p=PARAMETERS):
    """Source tension-positive diagonal subset only, excludes undefined norms."""
    sigma, speed = math.hypot(*t), math.hypot(*d)
    if sigma == 0 or speed == 0 or e <= p['emin']:
        raise ValueError('interior only; no boundary continuation')
    u = [x/speed for x in d]
    delta = math.fsum(u)
    a = p['c1']*math.exp(p['c2']*delta)
    r = [-math.exp(a*x) for x in u]
    rn = math.hypot(*r)
    ec = csl(sigma, p)[0]
    h = -(p['c4']+p['c5']*sigma)/(e-p['emin'])
    return [h*((delta+p['c3']*ec)*x/rn-p['c3']*e*y/sigma)*speed
            for x, y in zip(r, t)], (1+e)*math.fsum(d)


def stress_origin_witness():
    # At fixed nonzero D and same stress norm tending to0, only T0 differs.
    # Difference tends h0*g*d*(T0_a-T0_b); all R terms cancel.
    p, e = PARAMETERS, .75
    h0 = -p['c4']/(e-p['emin'])
    g = -p['c3']*e
    directions = [(-1/math.sqrt(3),)*3, (-2/math.sqrt(6), -1/math.sqrt(6), -1/math.sqrt(6))]
    difference = [h0*g*(x-y) for x,y in zip(*directions)]
    return dict(directions=directions, limiting_rate_difference=difference,
                difference_norm=math.hypot(*difference))


def build_fixtures():
    stresses = [0., 1., 100., 1000., 1e12]
    t, e, d = [-120., -80., -60.], .75, [-.002, .0003, .0004]
    rate, void_rate = diagonal_rate(t,e,d)
    x = .4
    return {'version':'barodesy-sand-2015-algebra-v1',
            'parameters':PARAMETERS,
            'parameter_provenance':'2019 manuscript Table1 illustrative kPa values; not asserted exact2015 calibration',
            'definitions':{'csl':'2015 Eqs26,27; derivative reciprocal Eq25',
                           'diagonal_rate':'2015 Eqs9,20,23,26,27,29–31, source tension-positive convention',
                           'matrix_witness':'expm([[0,x,0],[x,0,0],[0,0,0]])=[[cosh(x),sinh(x),0],[sinh(x),cosh(x),0],[0,0,1]]',
                           'origin_witness':'difference of two fixed-norm stress-direction limits, fixed unit loading speed'},
            'csl':[dict(sigma_kPa=s,ec=csl(s)[0],dec_dsigma_per_kPa=csl(s)[1]) for s in stresses],
            'diagonal_input':dict(stress_kPa=t,e=e,stretch=d),
            'diagonal_output':dict(stress_rate=rate,void_rate=void_rate),
            'matrix_exponential_witness':dict(x=x,matrix=[[math.cosh(x),math.sinh(x),0.],[math.sinh(x),math.cosh(x),0.],[0.,0.,1.]],
                                              componentwise_entry00=1.,componentwise_entry01=math.exp(x)),
            'stress_origin_witness':stress_origin_witness(),
            'limitations':['not a generic tensor exponential','no finite-path integration','no canonical zero-stress or zero-loading branch','no derivative/experimental/native/Wasm admission']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=build_fixtures()
    if args.check and json.loads(args.check.read_text()) != json.loads(json.dumps(result)):
        raise SystemExit('fixture mismatch')
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if args.check:
        print('bounded algebra fixture replay: PASS')

if __name__=='__main__':
    main()
