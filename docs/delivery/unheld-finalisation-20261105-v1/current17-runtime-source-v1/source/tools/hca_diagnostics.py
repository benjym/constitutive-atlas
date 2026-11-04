"""Bounded HCA-2005 arithmetic diagnostics; no constitutive model or pi update."""
import math
import sys

SOURCE = {
    'doi': 'https://doi.org/10.1016/j.compgeo.2005.03.002',
    'url': 'https://www.torsten-wichtmann.de/paper/journal/2005-CG-a-high-cycle-model.pdf',
    'sha256': 'ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce',
    'amplitude_locator': 'author-manuscript PDF p.10, Eqs.(21)-(23)',
    'history_locator': 'author-manuscript PDF p.12, Eq.(37); p.7, Eqs.(13)-(14)',
}


def _finite(x):
    try:
        return type(x) in (int, float) and math.isfinite(x)
    except OverflowError:
        return False


def _vector(value):
    if not isinstance(value, (list, tuple)) or len(value) != 6 or not all(_finite(x) for x in value):
        raise ValueError('six finite symmetric Mandel components required')
    return tuple(float(x) for x in value)


def convert_mandel(value, *, source, target):
    """Both bases are orthonormal; only xz/yz ordering changes, no sqrt(2) scaling."""
    bases = ('atlas_mandel', 'source_mandel')
    if source not in bases or target not in bases:
        raise ValueError('unknown Mandel basis')
    v = _vector(value)
    return v if source == target else v[:4] + (v[5], v[4])


def _dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def sampled_amplitude(samples, *, basis='atlas_mandel', rank_relative_tolerance=1e-12):
    """Farthest-pair recursive projection of the supplied finite point set.

    Original order and repetitions are retained. Indices refer to caller order.
    Numerical rank tolerance and exact-tie selection are project policies.
    """
    if not isinstance(samples, (list, tuple)) or not 2 <= len(samples) <= 128:
        raise ValueError('provide 2..128 ordered samples')
    if not _finite(rank_relative_tolerance) or not 0 < rank_relative_tolerance <= 1e-3:
        raise ValueError('rank relative tolerance must be in (0,1e-3]')
    points = [convert_mandel(p, source=basis, target='atlas_mandel') for p in samples]
    centered = [tuple(x-y for x, y in zip(p, points[0])) for p in points]
    if not all(_finite(x) for p in centered for x in p):
        raise ValueError('sample differences exceed finite arithmetic range')
    scale = max(abs(x) for p in centered for x in p)
    residual = [tuple(x/scale for x in p) for p in centered] if scale else centered
    directions = []; radii = []; stages = []; first_diameter = None
    discarded_radius = 0.
    for stage in range(6):
        pairs = [(math.dist(residual[i], residual[j]), i, j)
                 for i in range(len(points)) for j in range(i+1, len(points))]
        diameter = max(d for d, _, _ in pairs)
        ties = [[i, j] for d, i, j in pairs if d == diameter]
        if first_diameter is None:
            first_diameter = diameter
        if diameter == 0 or diameter <= rank_relative_tolerance*first_diameter:
            discarded_radius = diameter/2*scale
            break
        i, j = ties[0]
        direction = tuple((x-y)/diameter for x, y in zip(residual[j], residual[i]))
        # Twice reorthogonalize to protect the sampled-rank interpretation.
        for _ in range(2):
            for previous in directions:
                projection = _dot(direction, previous)
                direction = tuple(x-projection*y for x, y in zip(direction, previous))
        length = math.hypot(*direction)
        if not length:
            raise ValueError('numerical direction breakdown')
        direction = tuple(x/length for x in direction)
        pivot = max(range(6), key=lambda k: abs(direction[k]))
        if direction[pivot] < 0:
            direction = tuple(-x for x in direction)
        radius = diameter/2*scale
        if not _finite(radius) or radius == 0:
            raise ValueError('amplitude exceeds finite arithmetic range')
        radii.append(radius); directions.append(direction)
        stages.append({'stage': stage, 'source_index': 6-stage,
                       'selected_pair': [i, j], 'exact_tied_pairs': ties,
                       'diameter_scaled': diameter})
        residual = [tuple(x-_dot(p, direction)*y for x, y in zip(p, direction)) for p in residual]
    matrix = [[math.fsum(r*d[i]*d[j] for r, d in zip(radii, directions))
               for j in range(6)] for i in range(6)]
    amplitude = math.hypot(*radii)
    if not _finite(amplitude) or not all(_finite(x) for row in matrix for x in row):
        raise ValueError('amplitude exceeds finite arithmetic range')
    return {'basis': 'atlas_mandel', 'sample_count': len(points), 'sampled_rank': len(radii),
            'rank_relative_tolerance': rank_relative_tolerance,
            'radii': radii, 'directions': [list(d) for d in directions],
            'amplitude_operator': matrix, 'epsilon_ampl': amplitude,
            'normalized_operator': [[x/amplitude for x in row] for row in matrix] if amplitude else None,
            'stages': stages, 'discarded_radius_bound': discarded_radius,
            'source': dict(SOURCE)}


def g_a_increment(g_A, a, C_N1, C_N2, delta_N):
    """Eq.(37) only: fixed-amplitude scalar history, not total accumulation.

    Zero amplitude/interval/C_N2 gives zero increment. g_A is not inferred from N.
    delta_N=0 is an identity diagnostic; production accumulation blocks may require >0.
    """
    values = (g_A, a, C_N1, C_N2, delta_N)
    if not all(_finite(v) for v in values) or min(g_A, a, C_N2, delta_N) < 0 or C_N1 <= 0:
        raise ValueError('finite nonnegative history/amplitude/C_N2/count; C_N1 positive required')
    if a == 0 or C_N2 == 0 or delta_N == 0:
        return {'delta_g_A': 0., 'g_A_out': g_A}
    g_A, a, C_N1, C_N2, delta_N = map(float, values)
    b = a*C_N1
    # Subnormal product rounding can have O(1) relative error; retain logs there.
    represented_b = math.isfinite(b) and b >= sys.float_info.min
    log_b = math.log(b) if represented_b else math.fsum((math.log(a),math.log(C_N1)))
    if represented_b:
        ratio = g_A/b
    elif g_A == 0:
        ratio = 0.
    else:
        log_ratio = math.log(g_A)-log_b
        try:
            ratio = math.exp(log_ratio)
        except OverflowError:
            ratio = math.inf
    log_c = math.log(C_N2); log_n = math.log(delta_N)
    log_z = math.fsum((log_c, log_n, -ratio))
    try:
        if log_z < -37:
            # log1p(z)/z differs from 1 by at most z/2 < 4.3e-17.
            # Keep b combined with z: z itself may underflow while b*z does not.
            increment = math.exp(math.fsum((log_b,log_c,log_n,-ratio)))
        else:
            softplus = log_z + math.log1p(math.exp(-log_z)) if log_z > 0 else math.log1p(math.exp(log_z))
            increment = b*softplus if represented_b else math.exp(math.fsum((log_b,math.log(softplus))))
    except OverflowError as exc:
        raise ValueError('history result exceeds finite arithmetic range') from exc
    result = g_A + increment
    if not _finite(increment) or not _finite(result):
        raise ValueError('history result exceeds finite arithmetic range')
    if increment == 0:
        raise ValueError('positive history increment underflows arithmetic range')
    if result == g_A:
        raise ValueError('positive history increment lost when added to parent')
    return {'delta_g_A': increment, 'g_A_out': result}


def generate_evidence(source_path, output_directory):
    """Retain deterministic diagnostics and artifact/source hash bindings."""
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    observed = hashlib.sha256(Path(source_path).read_bytes()).hexdigest()
    if observed != SOURCE['sha256']:
        raise ValueError('original manuscript hash mismatch')
    fixtures = {}
    for n in (10, 30, 90):
        points = [[2*math.cos(2*math.pi*k/n),math.sin(2*math.pi*k/n),0.,0.,0.,0.] for k in range(n)]
        result = sampled_amplitude(points)
        fixtures[str(n)] = {'sample_count': n, 'sampled_rank': result['sampled_rank'],
                            'radii': result['radii'], 'epsilon_ampl': result['epsilon_ampl'],
                            'continuous_harmonic_norm_oracle': math.sqrt(5),
                            'absolute_norm_error': abs(result['epsilon_ampl']-math.sqrt(5))}
    whole = g_a_increment(.03,.1,.8,.2,17.)['g_A_out']
    split = .03
    for delta in (1.,3.,.5,12.5): split = g_a_increment(split,.1,.8,.2,delta)['g_A_out']
    evidence = {'version': 'hca-diagnostics-0.1', 'source': dict(SOURCE),
                'source_hash_verified': True, 'scope': 'sampled amplitude and fixed-amplitude scalar history only',
                'policies': {'sample_limit':128, 'rank_relative_tolerance':1e-12,
                             'tie_policy':'exact maximum distance; first caller index pair',
                             'source_optional_ten_percent_truncation':False},
                'harmonic_sampling':fixtures,
                'history_composition':{'g_A_in':.03,'a':.1,'C_N1':.8,'C_N2':.2,
                                       'delta_N':17.,'partitions':[1.,3.,.5,12.5],
                                       'whole':whole,'split':split,'absolute_difference':abs(whole-split)}}
    import decimal
    extremes = []
    cases = [(0.,1e300,1.,1e-300,1e-100),(0.,1e300,1.,1e-300,1e-300),
             (0.,1e200,1e200,1e-300,1e-100),(0.,5e-324,.1,1e300,1.),
             (0.,5e-324,.6,1e300,1.)]
    for values in cases:
        with decimal.localcontext() as context:
            context.prec = 1200
            g,a,c1,c2,n = map(decimal.Decimal.from_float, values)
            b = a*c1
            reference = float(b*(1+c2*n*(-g/b).exp()).ln())
        actual = g_a_increment(*values)
        extremes.append({'inputs':list(values),'delta_g_A':actual['delta_g_A'],
                         'decimal_1200_reference':reference,
                         'absolute_error':abs(actual['delta_g_A']-reference)})
    evidence['extreme_scalar_cases'] = extremes
    names = ['tools/hca_diagnostics.py','tests/test_hca_diagnostics.py',
             'tests/test_hca_covariance.py','docs/HCA_DIAGNOSTICS.md']
    evidence['inputs_sha256'] = {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}
    output = Path(output_directory); output.mkdir(parents=True, exist_ok=True)
    (output/'evidence.json').write_text(json.dumps(evidence,indent=2,sort_keys=True,allow_nan=False)+'\n')
    bindings = {name:evidence['inputs_sha256'][name] for name in names}
    evidence_name = 'catalogue/investigations/hca-diagnostics-v1/evidence.json'
    bindings[evidence_name] = hashlib.sha256((output/'evidence.json').read_bytes()).hexdigest()
    (output/'manifest.json').write_text(json.dumps(bindings,indent=2,sort_keys=True)+'\n')
    return evidence


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,help='local original manuscript PDF; never copied to output')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'catalogue/investigations/hca-diagnostics-v1')
    args = parser.parse_args()
    generate_evidence(args.source,args.output)
