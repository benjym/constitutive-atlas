"""Synthetic dependency witnesses, NOT a PM4Sand3D constitutive implementation."""
import copy
import json
import math


def witnesses():
    # Coordinates along one unit Frobenius deviatoric tensor B; n=B.
    parent = {'true': 0.4, 'previous': -0.2, 'fabric': 1., 'fabric_reversal': 0.,
              'D_lag': 0.2, 'Kp_lag': 10., 'generation': 8}
    endpoint = 0.1
    decision = endpoint - parent['true'] < 0
    good = {**parent, 'previous': parent['true'], 'true': endpoint}
    bad = copy.deepcopy(parent)
    bad['true'] = endpoint
    bad['previous'] = bad['true']
    twice = {**good, 'previous': good['true'], 'true': endpoint}
    # Eq27 and Eq47 differ only at equality in this abstract anchor tuple.
    a, previous, true, apparent = 0.4, 0.4, 0.1, -0.2
    q_previous = a - previous
    ratio = (a - apparent) / (a - true)
    stages = [copy.deepcopy(parent), {**parent, 'fabric': 2.}, good]
    failed_result = parent  # outer envelope required behavior, not source algorithm.
    return {
        'scope': 'synthetic scalar projections and dependency/transaction witnesses only',
        'basis_mandel': [math.sqrt(2/3), -1/math.sqrt(6), -1/math.sqrt(6), 0., 0., 0.],
        'anchor_copy': {'parent': parent, 'endpoint_alpha': endpoint,
            'step12_reversal': decision, 'simultaneous': good,
            'current_then_previous': bad, 'duplicate_copy': twice,
            'recomputed_guard_after_reset': endpoint-good['true'] < 0},
        'lag_scope': {'subzones': 2, 'incoming_shared': [parent['D_lag'], parent['Kp_lag']],
            'correct_reads': [[0.2, 10.], [0.2, 10.]],
            'wrong_early_publication_reads': [[0.2, 10.], [-0.1, 20.]],
            'candidate_for_next_caller': [-0.1, 20.]},
        'fabric_copy': {'before_step15': 1., 'after_step15': 2.,
            'copy_old_result': 1., 'copy_updated_result': 2.,
            'source_selected': None},
        'equality_branch': {'alpha': a, 'previous': previous, 'true': true, 'apparent': apparent,
            'q_previous': q_previous, 'eq27_strict_branch': q_previous < 0,
            'eq47_nonstrict_branch': q_previous <= 0,
            'eq47_ratio_branch_value': ratio, 'alternative_else_value': 1.,
            'full_material_path_admissibility': 'not established'},
        'initialized_ratio': {'all_anchors_equal_alpha': True, 'numerator': 0.,
            'denominator': 0., 'finite_source_branch_identified': False},
        'transaction': {'stages_attempted': stages, 'failure_after_anchor_phase': True,
            'returned_parent_identical': failed_result is parent,
            'parent_unchanged': parent == stages[0], 'published_events': [],
            'incomplete_zone_must_publish': False}
    }


if __name__ == '__main__':
    print(json.dumps(witnesses(), indent=2, allow_nan=False))
