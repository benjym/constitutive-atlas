"""Scope-aware recorded request codec; native execution is not activated here."""
import json
from pathlib import Path
from .dsl import ValidationError
from .recorded import recorded_wire, validate_recorded_run
from .stress import stress_binding
from .structure import check

VERSION='experimental-recorded-run-0.2'
SCHEMA=Path(__file__).resolve().parents[1]/'schemas/recorded-run-v0.2.schema.json'


def _legacy_mechanics(spec):
    # New outer identity, identical nested path/settings semantics. Never mutate.
    return {**{k:v for k,v in spec.items() if k!='stress_scope'},
            'version':'experimental-recorded-run-0.1'}


def validate_scoped_recorded_run(spec):
    """Check the closed 0.2 request and unchanged ordered path/settings contract."""
    try:
        check(spec,json.loads(SCHEMA.read_text()))
    except OverflowError as exc:
        raise ValidationError('numeric input exceeds finite floating-point range') from exc
    validate_recorded_run(_legacy_mechanics(spec))
    return spec


def validate_scoped_recorded_model(spec,model):
    """Check metadata compatibility, not full model validity or scientific scope.

    Execution must separately validate the complete model and engine capability.
    Total incremental validation remains disabled in the production engine.
    """
    validate_scoped_recorded_run(spec)
    binding=stress_binding(model)
    first=next(iter(model.get('state',[])),{})
    role=first.get('semantics',{}).get('role','increment_unknown' if first.get('transient') or first.get('multiplier') else 'persistent')
    if (model.get('id')!=spec['model'] or model.get('schema_version') not in ('0.1','0.3')
            or (model.get('schema_version')=='0.3' and model.get('formulation',{}).get('time_dependence')!='strain_path')
            or binding!=dict(source='state',name='sigma',measure='cauchy',scope=spec['stress_scope'])
            or first.get('name')!='sigma' or first.get('shape')!='sym' or first.get('unit')!='Pa' or role!='persistent'):
        raise ValidationError('recorded stress scope/model binding mismatch')
    return spec


def scoped_recorded_wire(spec,model):
    """Require matching declared scope before emitting unchanged numeric wires."""
    validate_scoped_recorded_model(spec,model)
    return recorded_wire(_legacy_mechanics(spec))
