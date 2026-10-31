"""Independent arithmetic/index witnesses for source questions; no author runtime."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

SOURCE_SHA = '43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9'


def run():
    findings = []
    Eo, Eu, p, nu = F(1000), F(3000), F(100), F(1, 5)
    plus = 3/(p*(1/Eo+3*(1-2*nu)/Eu))
    minus = 3/(p*(1/Eo-3*(1-2*nu)/Eu))
    assert plus == F(75, 4) and minus == 75 and plus != minus
    singular_Eu = F(1800)
    assert 1/Eo-3*(1-2*nu)/singular_Eu == 0
    assert 1/Eo+3*(1-2*nu)/singular_Eu != 0
    findings.append(dict(id='cap-denominator-conflict', equality='fails_as_printed',
                         plus=str(plus), minus=str(minus), minus_singular_Eur=str(singular_Eu)))
    # Index facts, not author-code execution or a claim about minimum model state.
    N = 33
    basic = 3*N+3
    writes = {'B_cs':3*N+12, 'project_path_length':3*N+13}
    assert basic == 102 and all(i > basic for i in writes.values())
    findings.append(dict(id='advertised-basic-bound', containment='fails_for_printed_unguarded_writes',
                         advertised=basic, writes=writes))
    bubble_addresses = {(16+4*k+j)*N+i for k in range(4) for j in range(4) for i in range(1, N+1)}
    assert len(bubble_addresses) == 16*N
    assert min(bubble_addresses) == 16*N+1 and max(bubble_addresses) == 32*N
    creates_from = [n for n in range(1, 5) if n <= 3]
    assert [n+1 for n in creates_from] == [2, 3, 4]
    findings.append(dict(id='four-contour-index-witness', address_count=len(bubble_addresses),
                         min_index=min(bubble_addresses), max_index=max(bubble_addresses),
                         possible_created_counts=[n+1 for n in creates_from], full_state_safety_proven=False))
    # Both active source branches overwrite normals using their own original stress.
    stress = (F(-50), F(-100), F(-50), F(3), F(0), F(0))
    OCR, POP, K0 = F(2), F(25), F(1, 2)
    ocr_normals = tuple(OCR*x for x in stress[:3])
    v = stress[1]-abs(POP)
    pop_normals = (K0*v, v, K0*v)
    assert ocr_normals == (F(-100), F(-200), F(-100))
    assert pop_normals == (F(-125, 2), F(-125), F(-125, 2))
    assert pop_normals != tuple(x*OCR for x in pop_normals)
    assert sum((F(10), F(-10), F(0), F(0), F(0), F(0))) == 0
    findings.append(dict(id='preparation-branch-witness', OCR_only=[str(x) for x in ocr_normals],
                         OCR_then_POP=[str(x) for x in pop_normals], nonzero_zero_trace_sentinel_collision=True,
                         accepted_Atlas_recipe=False))
    # Raw hyperbola witness inherited algebraically, not a selected stored-state policy.
    t0, u, h, gamma, maximum = F(1, 10), F(4, 5), F(1, 50), F(1, 10), F(3, 5)
    raw = t0+(u-t0)*gamma/(h+gamma)
    evaluated = min(raw, maximum)
    assert raw == F(41, 60) and evaluated == maximum and raw > evaluated
    findings.append(dict(id='raw-state-versus-clipped-evaluation', raw=str(raw), evaluated=str(evaluated),
                         immediate_stored_state_clamp_inferred=False))
    assert F(60)/1000 == F(3, 50)
    assert F(30)/180 == F(1, 6)  # coefficient of pi in radians
    findings.append(dict(id='source-input-scale', UI_Amat='60', equation_Amat=str(F(60)/1000),
                         UI_degrees='30', radians_as_pi_multiple=str(F(30)/180)))
    # Inspect denominators independently: do not execute or repair the source expression.
    unsafe = []
    floor = F(1, 10**15)
    for name, vol, shear in [('deviatoric_only', F(0), F(1, 1000)),
                              ('volumetric_only', F(1, 1000), F(0))]:
        active = abs(vol) > floor or shear > floor
        zeros = [label for label, x in [('volumetric', vol), ('shear', shear)] if x == 0]
        assert active and len(zeros) == 1
        unsafe.append(dict(case=name, outer_guard=True, zero_denominators=zeros))
    findings.append(dict(id='mixed-activity-division-guard', sufficiency='fails_for_two_algebraic_witnesses',
                         witnesses=unsafe, repaired_tolerance_or_policy=False))
    return dict(id='multilaminate-host-contract-v1', source_sha256=SOURCE_SHA,
                arithmetic='standard-library exact rational and integer index analysis',
                witness_checks_pass=True, findings=findings,
                source_conflicts_resolved=False, constitutive_validation=False,
                author_code_executed=False, scientific_admission=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path)
    args = parser.parse_args()
    if args.pdf:
        assert hashlib.sha256(args.pdf.read_bytes()).hexdigest() == SOURCE_SHA
    print(json.dumps(run(), indent=2, sort_keys=True)+'\n', end='')
