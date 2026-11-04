"""Research-only PM4Sand3D flow evaluation via the existing DSL and surface audit."""
import hashlib
import json
import math
from pathlib import Path
from atlas.dsl import I, Sym, Type, ValidationError, dimensions, evaluate, infer, parse
from atlas.model import ROOT
from tools.inspect_pm4sand_surfaces import evaluate_fragment as evaluate_surface, load_fragment as load_surface

FRAGMENT_PATH = Path(__file__).resolve().parents[1] / 'catalogue/source-audits/pm4sand3d-1.0-flow.json'


def validate_flow_fragment(fragment):
    surface = load_surface()  # Independently verifies the existing pinned manual identity/types.
    if fragment['source'] != surface['source'] or fragment['model_id'] != surface['model_id']:
        raise ValidationError('flow source identity differs from the pinned surface source')
    dependencies = fragment['dependencies']
    if len(dependencies) != 1 or dependencies[0]['path'] != 'catalogue/source-audits/pm4sand3d-1.0-surfaces.json':
        raise ValidationError('unexpected surface dependency')
    actual = hashlib.sha256((ROOT / dependencies[0]['path']).read_bytes()).hexdigest()
    if actual != dependencies[0]['sha256'] or fragment['terms'][:len(surface['terms'])] != surface['terms']:
        raise ValidationError('surface dependency hash or copied terms differ')
    D_input = fragment['inputs'].get('D')
    if not isinstance(D_input,dict):
        raise ValidationError('missing scalar flow input D')
    for key in ('c_min','c_max','trace_relative_tolerance','requirements'):
        if fragment['audit_domain'].get(key) != surface['audit_domain'][key]:
            raise ValidationError('flow audit domain differs from pinned surface scope')
    if len(fragment['terms']) != 11:
        raise ValidationError('flow fragment must contain eleven typed terms')
    expected_inputs = surface['inputs'] | {'D': D_input}
    if fragment['inputs'] != expected_inputs or fragment['inputs']['D']['shape'] != 'scalar' or fragment['inputs']['D']['unit'] != '1':
        raise ValidationError('incorrect flow inputs')
    symbols = {'I': Type('sym')}
    symbols.update({name: Type(spec['shape'], dimensions(spec['unit'])) for name,spec in fragment['inputs'].items()})
    for term in fragment['terms']:
        expected = Type(term['shape'], dimensions(term['unit']))
        if term['name'] in symbols or infer(parse(term['expression']), symbols) != expected:
            raise ValidationError('duplicate or incorrectly typed flow term: '+term['name'])
        symbols[term['name']] = expected
    return fragment


def load_flow_fragment(path=FRAGMENT_PATH):
    return validate_flow_fragment(json.loads(Path(path).read_text()))


def evaluate_flow(fragment, *, r, alpha, c, m, D):
    if type(D) not in (int,float) or not math.isfinite(D):
        raise ValidationError('D requires a finite real scalar')
    # Reuse the exact domain/undefined-direction policy of the surface fragment.
    surface = {key:fragment[key] for key in ('inputs','audit_domain','terms')}
    surface['terms'] = fragment['terms'][:7]
    outputs = evaluate_surface(surface, r=r, alpha=alpha, c=c, m=m)
    env = dict(I=I, r=r, alpha=alpha, c=c, m=m, D=D, **outputs)
    try:
        for term in fragment['terms'][7:]:
            value = env[term['name']] = evaluate(parse(term['expression']),env)
            values = value.v if isinstance(value,Sym) else (value,)
            if not all(math.isfinite(x) for x in values):
                raise ValueError('nonfinite flow result')
    except (ValueError,ZeroDivisionError,OverflowError) as exc:
        raise ValidationError('undefined flow evaluation; no regularization selected') from exc
    return {term['name']:env[term['name']] for term in fragment['terms']}
