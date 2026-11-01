"""Data-only initialization feasibility; does not initialize or run a model."""
import math

from .reservations import assert_development_ids


def first_loading_diagnostics(record, minimum_stresses):
    """Use observed starts, no interpolation and no reads of reserved responses.

    The first strictly decreasing stress ends first loading. Repeated controls
    remain in order. The logarithmic coordinate below is a geometric diagnostic,
    not authorization to extend an infinitesimal constitutive law to finite strain.
    """
    assert_development_ids([record['id']])
    if record.get('protocol') != 'oedometer':
        raise ValueError('compression protocol requires oedometer observations')
    rows = record['rows']
    if len(rows) < 2:
        raise ValueError('at least two observations are required')
    for row in rows:
        if (not all(math.isfinite(row[k]) for k in ('axial_stress', 'axial_strain', 'void_ratio'))
                or not 0 <= row['axial_strain'] < 1 or row['void_ratio'] <= 0
                or row['axial_stress'] < 0):
            raise ValueError('invalid compression observation or reference-volume strain')
    end = next((i-1 for i in range(1, len(rows))
                if rows[i]['axial_stress'] < rows[i-1]['axial_stress']), len(rows)-1)
    branch = rows[:end+1]
    if any(b['axial_strain'] < a['axial_strain'] for a, b in zip(branch, branch[1:])):
        raise ValueError('first loading contains decreasing strain; needs separate review')
    scenarios = []
    for threshold in minimum_stresses:
        if not math.isfinite(threshold) or threshold <= 0:
            raise ValueError('start threshold must be finite and positive')
        start_index = next((i for i, row in enumerate(branch) if row['axial_stress'] >= threshold), None)
        scenario = dict(requested_minimum_axial_stress_Pa=threshold,
                        initial_lateral_stress='unresolved', initial_history='unresolved')
        if start_index is None or start_index == end:
            scenario.update(status='no_nonzero_first_loading_interval')
            scenarios.append(scenario)
            continue
        start, final = rows[start_index], rows[end]
        delta = final['axial_strain']-start['axial_strain']
        logarithmic = math.log1p(-start['axial_strain'])-math.log1p(-final['axial_strain'])
        # Exact integral of de=-(1+e)dD with D interpreted as the recorded
        # engineering-strain increment. No stress law or fitted constant enters.
        engineering_e = (1+start['void_ratio'])*math.exp(-delta)-1
        # Constant-solid-volume geometry for the measured height ratio.
        geometric_e = (1+start['void_ratio'])*(1-final['axial_strain'])/(1-start['axial_strain'])-1
        scenario.update(status='data_interval_available_not_model_admission',
                        start_index=start_index, end_index=end,
                        start_source_line=start['source_line'], end_source_line=final['source_line'],
                        observations=end-start_index+1, start_axial_stress_Pa=start['axial_stress'],
                        start_void_ratio=start['void_ratio'], end_observed_void_ratio=final['void_ratio'],
                        engineering_strain_increment=delta,
                        logarithmic_height_strain_increment=logarithmic,
                        engineering_driven_continuity_end_void_ratio=engineering_e,
                        engineering_driven_end_void_ratio_residual=engineering_e-final['void_ratio'],
                        geometry_end_void_ratio=geometric_e,
                        geometry_end_void_ratio_residual=geometric_e-final['void_ratio'])
        scenarios.append(scenario)
    return dict(id=record['id'], first_loading_end_index=end,
                first_loading_end_source_line=rows[end]['source_line'],
                first_loading_end_reason='first_stress_decrease' if end < len(rows)-1 else 'record_end',
                later_observations_excluded_from_this_diagnostic=len(rows)-end-1,
                full_cycle_has_zero_stress=any(row['axial_stress'] == 0 for row in rows[end+1:]),
                scenarios=scenarios)
