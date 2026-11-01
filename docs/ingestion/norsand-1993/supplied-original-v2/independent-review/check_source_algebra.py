"""Independent source-only algebra; no atlas/compiled implementation imported.

Prospective tolerances: inverse/flow algebra 3e-12; central finite-difference
normality 3e-7 absolute. These establish identities, not trajectory accuracy.
"""
import hashlib
import json
import math
from pathlib import Path


def yield_eta(r, M, N):  # r = p / image pressure, Eq7
    if N == 0:
        return M * (1 - math.log(r))
    return M / N * (1 + (N - 1) * r ** (N / (1 - N)))


def image_ratio(eta, M, N):  # Eq10
    if N == 0:
        return math.exp(eta / M - 1)
    return ((1 - N * eta / M) / (1 - N)) ** ((N - 1) / N)


def limit_ratio(psi_i, M, N):  # Eq11; current psi_i held as argument
    if N == 0:
        return math.exp(-3.5 * psi_i / M)
    return (1 + 3.5 * psi_i * N / M) ** ((N - 1) / N)


def main():
    inverse = []
    normality = []
    limit = []
    for N in (0, 0.1, 0.2, 0.39):
        M = 1.25
        for r in (0.6, 1.0, 1.4, 2.0):
            eta = yield_eta(r, M, N)
            inverse.append(abs(image_ratio(eta, M, N) - 1 / r))
            # With image pressure = 1, q(p) = p*eta(p). Normality
            # requires D=-dq/dp; central difference is constructed from
            # the yield curve, independently of the explicit flow rule.
            delta = 1e-5 * r
            slope = ((r + delta) * yield_eta(r + delta, M, N)
                     - (r - delta) * yield_eta(r - delta, M, N)) / (2 * delta)
            normality.append(abs(-slope - (M - eta) / (1 - N)))
        for psi_i in (-0.2, 0, 0.1):
            eta_lim = yield_eta(1 / limit_ratio(psi_i, M, N), M, N)
            limit.append(abs((M - eta_lim) / (1 - N) - 3.5 * psi_i))
    assert max(inverse + limit) < 3e-12
    assert max(normality) < 3e-7
    # Normally consolidated q=0 initialization, N=.2, Fig8 p98.
    nc_ratio = image_ratio(0, 1.25, .2)
    assert abs(nc_ratio - .4096) < 3e-12
    # Work conjugacy using notation p102, not a tensor extension.
    s1, s3, e1, e3 = 180., 90., .02, -.003
    p, q = (s1 + 2*s3)/3, s1-s3
    ep, eq = e1+2*e3, 2*(e1-e3)/3
    assert abs(p*ep + q*eq - (s1*e1+2*s3*e3)) < 3e-12
    source = Path('.local/private-sources/norsand-1993/supplied-original-v2/NorSandGeot1993.pdf')
    result = {
        'reviewer': '/root/norsand_original_review',
        'scope': 'original-source algebra only; not E5 approval',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': {'inverse': len(inverse), 'normality': len(normality), 'limiting_flow': len(limit)},
        'max_inverse_error': max(inverse),
        'max_normality_error': max(normality),
        'max_limiting_flow_error': max(limit),
        'normally_consolidated_pi_over_p_N_0_2': nc_ratio,
        'work_conjugacy': 'pass',
        'result': 'pass',
        'excluded': ['production comparison', 'trajectory integration', 'parameter admission', 'compiled execution'],
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
