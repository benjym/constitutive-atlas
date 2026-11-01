"""Exact source-constraint diagnostics, not a constitutive update or solver test."""
from fractions import Fraction as F
import json
from pathlib import Path


def check():
    # Ch6 pp95/98: at fixed p and packing, interior stress probes produce no strain.
    # ln(2) > 1/2 follows by integrating 1/x > 1/2 over [1,2].
    M, p, pc, v, kappa = F(6, 5), F(50000), F(100000), F(2), F(1, 25)
    threshold_lower = M * p / 2
    qs = [F(-10000), F(0), F(10000)]
    assert pc == 2*p and all(abs(q) < threshold_lower for q in qs)
    compliance = [[kappa/(v*p), F(0)], [F(0), F(0)]]
    assert compliance[0][0] > 0 and compliance[0][1] == compliance[1][0] == compliance[1][1] == 0
    # Same strain/volume/packing increment, distinct interior final stresses.
    # Does not imply distinct stresses are mandatory for a strain-driven API.
    states = [dict(p_Pa=int(p), q_Pa=int(q), v=str(v), pc_Pa=int(pc),
                   volumetric_increment=0, distortion_increment=0) for q in qs]
    # Ch6 p101 normal cone: f+/- = +/-q + M p ln(p/pc).
    # At the vertex the normals in (p,q) coordinates are (M,+/-1).
    corner = []
    for lp, lm in [(F(1,1000),F(0)), (F(0),F(1,1000)), (F(1,2000),F(1,2000))]:
        ev, es = M*(lp+lm), lp-lm
        assert lp >= 0 and lm >= 0 and ev >= M*abs(es)
        corner.append(dict(lambda_plus=str(lp),lambda_minus=str(lm),
                           plastic_volume=str(ev),plastic_distortion=str(es),
                           stress_work_Pa=str(pc*ev),
                           smooth_absolute_shear_loss_Pa=str(M*pc*abs(es))))
    assert corner[-1]['plastic_distortion'] == '0'
    assert corner[-1]['stress_work_Pa'] != corner[-1]['smooth_absolute_shear_loss_Pa']
    # Any finite G introduces shear compliance absent in original Ch6 Eq6.7.
    G = F(10000000)
    added_shear_strain = (qs[-1]-qs[1])/(3*G)
    assert added_shear_strain != 0
    return dict(passed=True, compiled_calls=0, acceptance='exact rational identities and analytic ln2 lower bound',
                interior_states=states, yield_threshold_strict_lower_bound_Pa=str(threshold_lower),
                elastic_compliance=[[str(x) for x in row] for row in compliance],
                compliance_rank=1, corner_vectors=corner,
                finite_G_augmented_shear_increment=str(added_shear_strain),
                limitations='No finite update, full3D closure, source-edition authentication or generic-engine impossibility claim.')


if __name__ == '__main__':
    Path(__file__).with_name('constraint-witness.json').write_text(json.dumps(check(),indent=2)+'\n')
