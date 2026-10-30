"""Draft structural/semantic contract for ordered incremental recorded paths.

Validation does not integrate a model or check initial-target consistency.
Finite coefficient rows act on orthonormal Mandel components xx,yy,zz,xy,yz,xz.
Targets are absolute projections; strain targets are dimensionless, stress Pa.
The coordinate orders loading and is not physical time. Input is never sorted,
rescaled, deduplicated, or otherwise mutated. C++ must repeat validation.
"""
import json
from pathlib import Path
from atlas.dsl import ValidationError
from atlas.structure import check

VERSION = 'experimental-recorded-path-0.1'
RANK_PIVOT_TOLERANCE = 1e-14
SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schemas/recorded-path.schema.json'


def _full_rank(rows):
    # Row-max scaling prevents overflow/underflow for valid finite coefficients.
    # This scaling is private to rank diagnosis, never the recorded definition.
    a = [[v/max(abs(x) for x in row) for v in row] for row in rows]
    for k in range(6):
        pivot = max(range(k,6),key=lambda i:abs(a[i][k]))
        if abs(a[pivot][k]) < RANK_PIVOT_TOLERANCE:
            return False
        a[k],a[pivot] = a[pivot],a[k]
        for i in range(k+1,6):
            factor = a[i][k]/a[k][k]
            for j in range(k+1,6):
                a[i][j] -= factor*a[k][j]
            a[i][k] = 0.
    return True


def validate_recorded_path(spec):
    """Validate and return the original specification without changing it.

    Pure-strain coefficient matrices must have numerical rank six under a
    row-scaled partial-pivot test. Mixed controls cannot be ranked using their
    coefficients alone: the constitutive stiffness enters the control Jacobian.
    """
    try:
        check(spec,json.loads(SCHEMA_PATH.read_text()))
    except OverflowError as exc:
        raise ValidationError('numeric input exceeds finite floating-point range') from exc
    if not spec['coordinate']['name'].strip():
        raise ValidationError('coordinate name must contain non-whitespace text')
    for i,row in enumerate(spec['controls']):
        if not any(v != 0 for v in row['coefficients']):
            raise ValidationError(f'controls[{i}]: coefficient row must be nonzero')
    if all(row['kind']=='strain' for row in spec['controls']):
        if not _full_rank([row['coefficients'] for row in spec['controls']]):
            raise ValidationError('all-strain coefficient matrix is numerically rank deficient')
    previous = spec['knots'][0]['coordinate']
    for i,knot in enumerate(spec['knots'][1:],1):
        if not knot['coordinate'] > previous:
            raise ValidationError(f'knots[{i}]: coordinates must be strictly increasing in input order')
        previous = knot['coordinate']
    return spec
