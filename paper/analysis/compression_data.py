"""Scoped OE transcription; never invent a full initial effective stress."""
import math
from pathlib import PurePosixPath
import re

from .reservations import assert_development_ids


def normalize_oedometer(content, name, archive_hash, member_hash):
    match = re.fullmatch(r'OE([0-9]+)\.dat', PurePosixPath(name).name, re.IGNORECASE)
    if not match:
        raise ValueError('unsupported OE member name')
    identifier = 'KFS-OE'+match[1]
    assert_development_ids([identifier])
    lines = content.decode('utf-8-sig').splitlines()
    if (len(lines) < 3 or lines[0].split() != ['sigma1', 'eps1', 'Void', 'ratio'] or
            lines[1].split() != ['[kPa]', '[%]', '[-]']):
        raise ValueError('unrecognized OE headers or units')
    rows = []
    for number, line in enumerate(lines[2:], 3):
        if not line.strip():
            continue
        try:
            values = [float(x) for x in line.split()]
        except ValueError as exc:
            raise ValueError(f'non-numeric OE line {number}') from exc
        if len(values) != 3 or not all(math.isfinite(v) for v in values) or values[2] <= 0:
            raise ValueError(f'expected three finite OE values and positive void ratio at line {number}')
        rows.append(dict(axial_stress=values[0]*1000, axial_strain=values[1]/100,
                         void_ratio=values[2], source_line=number))
    if not rows:
        raise ValueError('empty OE response')
    return dict(schema_version='0.1', kind='experiment', id=identifier, material='Karlsruhe fine sand',
                protocol='oedometer', conventions=dict(stress='compression-positive', strain='compression-positive',
                    stress_unit='Pa', strain_unit='1'),
                provenance=dict(source_url='https://www.torsten-wichtmann.de/KFSDB-OE.htm',
                    archive_sha256=archive_hash, member=name, member_sha256=member_hash,
                    original_headers=lines[:2], transformations=['Axial stress: kPa to Pa.',
                        'Axial strain: percent to dimensionless; void ratio retained.',
                        'Source line numbers and acquisition order retained, including repeated observations.'],
                    redistribution='not-reviewed; local research copy only'),
                initial=dict(void_ratio=rows[0]['void_ratio'], axial_stress=rows[0]['axial_stress'],
                             axial_strain=rows[0]['axial_strain']),
                warnings=['Dry oedometer source; effective-stress interpretation and model applicability need review.',
                          'Radial stress, full initial stress, elapsed time and loading rate are not supplied by these columns.',
                          'Void ratio and axial strain are kinematically linked; do not count as independent curve information.',
                          'No zero-stress initialization or positive-stress truncation rule is imposed by normalization.'], rows=rows)


def audit_oedometer(record):
    rows = record['rows']
    stresses = [r['axial_stress'] for r in rows]
    strains = [r['axial_strain'] for r in rows]
    e0 = rows[0]['void_ratio']
    x0 = rows[0]['axial_strain']
    # The selected source starts at zero engineering strain. Do not silently
    # apply a reference-volume conversion to a different source convention.
    if x0 != 0:
        raise ValueError('kinematic check requires the source zero-strain reference')
    residuals = [abs((1+r['void_ratio'])-(1+e0)*(1-r['axial_strain'])) for r in rows]
    # Source e has five decimals; eps1 has three decimals in percent. This
    # bound describes printing precision, not measurement uncertainty.
    bounds = [5e-6+abs(1-r['axial_strain'])*5e-6+(1+e0)*5e-6+25e-12 for r in rows]
    ds = [b-a for a, b in zip(stresses, stresses[1:])]
    signs = [1 if d > 0 else -1 for d in ds if d != 0]
    return dict(id=record['id'], rows=len(rows), full_initial_stress_available=False,
                minimum_axial_stress_Pa=min(stresses), maximum_axial_stress_Pa=max(stresses),
                zero_axial_stress_rows=sum(s == 0 for s in stresses),
                stress_direction_changes=sum(a != b for a, b in zip(signs, signs[1:])),
                repeated_stress_steps=sum(d == 0 for d in ds),
                decreasing_axial_strain_steps=sum(b < a for a, b in zip(strains, strains[1:])),
                maximum_kinematic_residual=max(residuals),
                maximum_print_rounding_ratio=max(r/b for r, b in zip(residuals, bounds)),
                kinematic_relation='1+e = (1+e_initial)*(1-engineering_axial_strain), assuming fixed lateral dimensions and solid volume',
                rounding_is_measurement_uncertainty=False, calibration_admission='not_established')
