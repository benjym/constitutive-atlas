"""Bounded ISA ingestion algebra/receipt checks; not a constitutive evaluator."""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checks(repo=None):
    receipt = json.loads((HERE / 'source-receipt.json').read_text())
    result = {'version': 'isa-ingestion-algebra-0.1', 'constitutive_evaluator': False,
              'compiled_calls': 0, 'source_conflicts_resolved': False, 'checks': []}
    def check(name, ok, details):
        if not ok:
            raise AssertionError(name)
        result['checks'].append({'name': name, 'passed': True, 'details': details})
    for record in receipt['private_sources']:
        p = Path(record['private_path'])
        if p.exists():
            check('private-source:' + record['id'], sha(p) == record['sha256'], record['sha256'])
        else:
            result.setdefault('unavailable_private_sources', []).append(record['id'])
    if repo is not None:
        for record in receipt['repository_dependencies']:
            p = Path(repo) / record['path']
            check('repository-dependency:' + record['path'], p.is_file() and sha(p) == record['sha256'], record['sha256'])
    # Visually transcribed scalar shapes; this diagnoses a discrepancy, selects no repair.
    t, c = .4, .3
    printed = math.sqrt(t*t/8 + (2-t*t)/(2+2*math.sqrt(2)*t*c)) - 1/(2*math.sqrt(2)*t)
    vw = math.sqrt(t*t/8 + (2-t*t)/(2+math.sqrt(2)*t*c)) - t/(2*math.sqrt(2))
    check('shape-formula-disagreement', abs(printed-vw) > .1,
          {'tan_psi': t, 'cos_3theta': c, 'ISA_printed_Eq39': printed, 'VW96_Eq42': vw,
           'same_lode_scalar_for_comparison_only': True, 'ISA_hydro_reciprocal_undefined': True,
           'denominator_constant_is_2_not_a_squared': True})
    # Independent limiting calculation: sqrt term stays O(1), printed reciprocal diverges.
    vals = [math.sqrt(t*t/8 + (2-t*t)/2)-1/(2*math.sqrt(2)*t) for t in [1e-3,1e-6]]
    check('printed-hydro-approach-singular', vals[1] < 900*vals[0], {'tan_psi':[1e-3,1e-6],'printed_values':vals})
    R = 1.4e-4
    chord = []
    for f in [0., .25, .5, .75, 1.]:
        h, cent = R*(1-f), R/2
        fh = abs(h-cent)-R/2
        chord.append({'s_over_R':f,'FH_over_R':fh/R,'N_defined':h != cent})
        check('elastic-chord:' + str(f), abs(fh) < 1e-18 if f in (0.,1.) else fh < 0,
              chord[-1])
    check('elastic-midpoint-direction-undefined', chord[2]['N_defined'] is False, 'h=c on reversal chord')
    # Fixed unit N diagnostic: Z(u)=N+(Z0-N)exp(-u), u=integral k ds.
    # Not the evolving-N ISA trajectory. Norm<=1 follows convex combination.
    N, Z0 = [1.,0.,0.,0.,0.,0.], [-.3,.2,0.,0.,0.,0.]
    for u in [0., .125, 2., 100.]:
        z = [ni+(zi-ni)*math.exp(-u) for ni,zi in zip(N,Z0)]
        check('fixed-direction-Z-ball:' + str(u), math.hypot(*z) <= 1,
              {'u':u,'norm_Z':math.hypot(*z),'f_z':max(-sum(ni*zi for ni,zi in zip(N,z)),0.)})
    # Source sign inversion of ALL symmetric components leaves contractions invariant.
    h, c6, D, Z = [2.,1.,-.2,.3,.4,-.7], [.2,0.,.1,-.1,.1,.2], [.2,-.3,.4,.1,.5,-.6], [.1,.2,.3,.4,.1,.2]
    diff = [x-y for x,y in zip(h,c6)]
    N = [x/math.hypot(*diff) for x in diff]
    Nd = sum(x*y for x,y in zip(N,D))
    fz = max(-sum(x*y for x,y in zip(Z,N)),0.)
    Ns, Ds, Zs = [-x for x in N], [-x for x in D], [-x for x in Z]
    check('compression-sign-contractions', Nd == sum(x*y for x,y in zip(Ns,Ds)) and fz == max(-sum(x*y for x,y in zip(Zs,Ns)),0.),
          {'N_dot_D':Nd,'f_z':fz})
    # Actual Cartesian -> Mandel contraction, including all shear pairs.
    A = [[2.,.3,-.4],[.3,-1.,.7],[-.4,.7,.5]]
    B = [[-.2,.9,.1],[.9,.6,-.8],[.1,-.8,1.1]]
    def mandel(a):
        return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
    check('mandel-component-identities', mandel(A) == [2.,-1.,.5,math.sqrt(2)*.3,math.sqrt(2)*.7,math.sqrt(2)*(-.4)], {'basis':'xx yy zz sqrt2xy sqrt2yz sqrt2xz'})
    cart = sum(A[i][j]*B[i][j] for i in range(3) for j in range(3))
    md = sum(x*y for x,y in zip(mandel(A),mandel(B)))
    check('cartesian-mandel-contraction', math.isclose(cart,md,rel_tol=0.,abs_tol=2e-15), {'cartesian':cart,'mandel':md})
    # Full-history cardinality; statuses must not accidentally claim executable support.
    contract = json.loads((HERE/'fragment-contract.json').read_text())
    check('state-layout-and-contract-status', sum(x['components'] for x in contract['state_layout']) == 26 and contract['basis'] == ['11','22','33','sqrt(2)*12','sqrt(2)*23','sqrt(2)*13'] and contract['executable'] is False and contract['admission_changed'] is False,
          {'components':26,'nonexecutable':True})
    result['passed'] = True
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(checks(args.repo),indent=2,allow_nan=False)+'\n')
