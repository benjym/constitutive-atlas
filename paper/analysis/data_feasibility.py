"""Minimum field checks are not scientific admission or specimen deduplication."""
import math


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def classify(record):
    rows = record['rows']
    channels = sorted(set().union(*(set(row) for row in rows)))
    counts = {key: sum(key in row for row in rows) for key in channels}
    initial = record.get('initial', {})
    stress = initial.get('effective_stress')
    stress_present = (isinstance(stress, list) and len(stress) == 6 and
                      all(finite_number(v) for v in stress) and sum(stress[:3]) > 0)
    e = initial.get('void_ratio')
    void_present = finite_number(e) and e > 0
    gaps = []
    if record['kind'] == 'experiment':
        required = {'axial_strain', 'q'}
        if record['protocol'] == 'drained-triaxial':
            required.add('volumetric_strain')
        elif record['protocol'] == 'undrained-triaxial':
            required.add('p')
        else:
            gaps.append('protocol_not_in_current_triaxial_field_check')
        missing = sorted(key for key in required if counts.get(key, 0) != len(rows))
        if missing:
            gaps.append('required_channels_missing_or_incomplete')
        if not stress_present:
            gaps.append('initial_effective_stress_unresolved')
        if not void_present:
            gaps.append('initial_void_ratio_unresolved')
        minimum_present = not gaps
        disposition = 'minimum_triaxial_fields_present' if minimum_present else 'triaxial_metadata_gaps'
    else:
        missing = []
        minimum_present = False
        disposition = ('summary_not_a_loading_history' if record['kind'] == 'test-summary'
                       else 'source_series_requires_scoped_adapter_and_metadata_review')
        gaps.append(disposition)
    return dict(disposition=disposition, minimum_triaxial_fields_present=minimum_present,
                native_drained_field_candidate=minimum_present and record['protocol'] == 'drained-triaxial',
                missing_or_incomplete_required_channels=missing, channels=channels,
                channel_row_counts=counts, initial_effective_stress_present=stress_present,
                initial_void_ratio_present=void_present, gaps=gaps,
                scientific_admission='not_assessed', independent_specimen_identity='not_established')
