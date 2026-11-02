"""Stress identity metadata; this does not validate or enable an execution profile."""
from .dsl import ValidationError


def stress_binding(model):
    """Return a detached stress descriptor from an otherwise validated model.

    v0.1 has the documented effective Cauchy sigma contract. v0.2 timed
    observables have no declared measure/scope: retain that uncertainty rather
    than infer effective/total from a tensor name. v0.3 must declare its binding.
    A returned total binding does not authorize incremental total execution.
    """
    version = model.get('schema_version')
    if version == '0.1':
        return dict(source='state', name='sigma', measure='cauchy', scope='effective')
    if version == '0.2':
        if any(field.get('name') == 'stress' for field in model.get('observables', [])):
            return dict(source='observable', name='stress', measure='unspecified', scope='unspecified')
        return dict(source='none')
    if version != '0.3':
        raise ValidationError('unsupported stress binding model version')
    formulation = model.get('formulation')
    binding = formulation.get('stress') if isinstance(formulation, dict) else None
    if binding == {'source': 'none'}:
        return dict(source='none')
    if (not isinstance(binding, dict) or set(binding) != {'source', 'name', 'measure', 'scope'}
            or binding['source'] not in ('state', 'observable')
            or not isinstance(binding['name'], str) or not binding['name']
            or binding['measure'] != 'cauchy' or binding['scope'] not in ('effective', 'total')):
        raise ValidationError('explicit Cauchy stress binding and scope required')
    return dict(binding)


def stress_scope(model):
    """Return none/effective/total/unspecified without guessing missing scope."""
    binding = stress_binding(model)
    return 'none' if binding['source'] == 'none' else binding['scope']
