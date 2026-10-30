"""Model loading and semantic validation. JSON is the canonical YAML subset."""
from __future__ import annotations
import json
import math
import re
from pathlib import Path
from .dsl import DIMS, TIME, I, Sym, Type, ZERO, dimensions, ValidationError, cpp, evaluate, infer, parse

MAX_STATE_COMPONENTS = 32
ROOT = Path(__file__).resolve().parents[1]
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
RESERVED = {"I", "de", "dt", "time", "time_n", "strain_rate", "loading", "evaluation_time", "check_only", "observables_only", "check_initial", "T", "params", "z", "zn", "out", "domain", "true", "false",
            "double", "auto", "if", "else", "return", "const", "class", "struct", "template",
            "int", "float", "void", "bool", "new", "delete", "switch", "case", "default",
            "for", "while", "do", "break", "continue", "throw", "try", "catch", "namespace",
            "make_sym", "axisymmetric_x", "using", "typename", "static", "virtual", "public", "private", "protected"}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    model = json.loads(Path(path).read_text(), object_pairs_hook=reject_duplicate_keys,
                       parse_constant=lambda s: (_ for _ in ()).throw(ValidationError(f"invalid number: {s}")))
    validate(model)
    return model


def field_type(field):
    if field.get('shape', 'scalar') not in ('scalar', 'sym'):
        raise ValidationError('unsupported shape')
    return Type(field.get('shape','scalar'), dimensions(field.get('unit','1')))


def physical_time(model):
    return model.get('schema_version') == '0.2'


def validate(model):
    from .structure import check
    version=model.get('schema_version')
    if version not in ('0.1','0.2'):
        raise ValidationError('unsupported schema version')
    physical=physical_time(model)
    schema='model-v0.2.schema.json' if physical else 'model.schema.json'
    check(model,json.loads((ROOT/'schemas'/schema).read_text()))
    required = {'schema_version','id','name','family','status','sources','parameters','state', 'derived','equations','domain','description'}
    if not required <= model.keys():
        raise ValidationError(f"missing fields: {sorted(required-model.keys())}")
    if not physical and model['integration'] not in ('residual','rate'):
        raise ValidationError('unsupported schema version or integration kind')
    if not re.fullmatch(r'[a-z][a-z0-9-]*',model['id']):
        raise ValidationError('invalid model ID')
    if model['status'] not in ('draft','transcribed','numerically-tested','reviewed'):
        raise ValidationError('invalid review status')
    if not model['sources'] or any(not {'url','locator','role'} <= s.keys() for s in model['sources']):
        raise ValidationError('source URL, locator and role are required')
    symbols = {'I':Type('sym'), 'time':Type(dim=TIME), 'strain_rate':Type('sym',tuple(-v for v in TIME))} if physical else {'I':Type('sym'),'de':Type('sym')}
    names = set()
    def declare(name, typ):
        if not IDENT.fullmatch(name) or name in RESERVED or name.endswith('_n') or name in names:
            raise ValidationError(f'invalid, duplicate or reserved identifier: {name}')
        names.add(name)
        symbols[name]=typ
    for name,field in model['parameters'].items():
        typ=field_type(field)
        if typ.shape != 'scalar': raise ValidationError('parameters must be scalar')
        declare(name,typ)
        if any(type(field.get(k)) not in (int,float) or not math.isfinite(field[k]) for k in ('default','min','max')):
            raise ValidationError(f'{name}: finite default, min and max required')
        if not field['min'] <= field['default'] <= field['max']:
            raise ValidationError(f'{name}: default outside bounds')
    if not physical and (not model['state'] or model['state'][0]['name'] != 'sigma' or field_type(model['state'][0]) != Type('sym',DIMS['Pa'])):
        raise ValidationError('first state must be symmetric stress sigma in Pa')
    count=0
    for field in model['state']:
        typ=field_type(field); name=field['name']
        declare(name,typ)
        if not physical: symbols[name+'_n']=typ
        initial=field['initial']
        if typ.shape=='sym':
            if not isinstance(initial,list) or len(initial)!=6: raise ValidationError(f'{name}: six Mandel components required')
        else: initial=[initial]
        if any(type(v) not in (float,int) or not math.isfinite(v) for v in initial): raise ValidationError('nonfinite initial value')
        scale=parse(field['scale'])
        param_symbols={key:field_type(value) for key,value in model['parameters'].items()}
        if infer(scale,param_symbols)!=Type(dim=typ.dim): raise ValidationError(f'{name}: scale must have matching units and reference parameters only')
        env={k:v['default'] for k,v in model['parameters'].items()}
        scale_value=evaluate(scale,env)
        if not math.isfinite(scale_value) or scale_value<=0: raise ValidationError('state scale must be finite and positive')
        count+=6 if typ.shape=='sym' else 1
        if physical and (field.get('transient') or field.get('multiplier')):
            raise ValidationError('physical-time ODE state must be persistent; incremental multipliers are unsupported')
        if field.get('multiplier') and (typ!=Type() or not field.get('transient') or model['integration']!='residual'):
            raise ValidationError('multipliers must be dimensionless transient scalars in residual models')
    if count>MAX_STATE_COMPONENTS: raise ValidationError(f'at most {MAX_STATE_COMPONENTS} state components are supported')
    for field in model['derived']:
        typ=infer(parse(field['expr']),symbols)
        if typ.shape=='bool': raise ValidationError('derived values must be numeric')
        declare(field['name'],typ)
    eqs=model['equations']
    if set(eqs)!={f['name'] for f in model['state']}: raise ValidationError('one equation per state is required')
    for f in model['state']:
        expected=field_type(f)
        if physical: expected=Type(expected.shape,tuple(a-b for a,b in zip(expected.dim,TIME)))
        if infer(parse(eqs[f['name']]),symbols)!=expected: raise ValidationError(f"{f['name']}: equation shape or dimensions mismatch")
    for condition in model['domain']:
        if infer(parse(condition),symbols)!=Type('bool'): raise ValidationError('domain checks must be comparisons')
    for condition in model.get('initial_checks',[]):
        if infer(parse(condition),symbols)!=Type('bool'): raise ValidationError('initial checks must be comparisons')
    for field in model.get('observables',[]):
        typ=field_type(field)
        if infer(parse(field['expr']),symbols)!=typ:
            raise ValidationError(f"{field['name']}: observable shape or dimensions mismatch")
        if field['name']=='stress' and typ!=Type('sym',DIMS['Pa']):
            raise ValidationError('stress observable must be a symmetric tensor in Pa')
        scale=parse(field['scale'])
        param_symbols={name:field_type(value) for name,value in model['parameters'].items()}
        scale_value=evaluate(scale,defaults(model)) if infer(scale,param_symbols)==Type(dim=typ.dim) else float('nan')
        if not math.isfinite(scale_value) or scale_value<=0:
            raise ValidationError('observable scale must be positive, parameter-only, and have matching units')
        # Output names do not enter the equation/derived namespace.
        if not IDENT.fullmatch(field['name']) or field['name'] in RESERVED or field['name'].endswith('_n') or field['name'] in names:
            raise ValidationError('invalid or duplicate observable name')
        names.add(field['name'])
    return model


def defaults(model):
    return {name: p['default'] for name,p in model['parameters'].items()}


def axisymmetric_x(values):
    if len(values)!=6 or any(not math.isfinite(v) for v in values):return False
    tolerance=64*__import__('sys').float_info.epsilon*max(map(abs,values))
    return abs(values[1]-values[2])<=tolerance and all(abs(v)<=tolerance for v in values[3:])


def evaluation_environment(model, state, previous, increment, parameters=None, *, time=None):
    if physical_time(model) and (type(time) not in (int,float) or not math.isfinite(time)):
        raise ValueError('physical-time evaluation requires finite stage time')
    if model.get('formulation',{}).get('kinematics')=='axisymmetric_x' and not axisymmetric_x(increment):
        raise ValueError('axisymmetric_x requires equal radial rates and zero shear')
    env={'I':I,'de':Sym(tuple(increment)),**defaults(model),**(parameters or {})}
    if physical_time(model): env.update(time=time, strain_rate=Sym(tuple(increment)))
    for f in model['state']:
        name=f['name']; wrap=lambda v: Sym(tuple(v)) if f.get('shape')=='sym' else v
        env[name]=wrap(state[name])
        if not physical_time(model): env[name+'_n']=wrap(previous[name])
    for f in model['derived']: env[f['name']]=evaluate(parse(f['expr']),env)
    if not all(evaluate(parse(c),env) for c in model['domain']): raise ValueError('state outside model domain')
    return env


def interpret(model, state, previous, increment, parameters=None, *, time=None):
    env=evaluation_environment(model,state,previous,increment,parameters,time=time)
    return {k:evaluate(parse(expr),env) for k,expr in model['equations'].items()}


def observe(model,state,strain_rate,parameters=None,*,time=None):
    if not physical_time(model):raise ValidationError('observables require a physical-time ODE definition')
    env=evaluation_environment(model,state,None,strain_rate,parameters,time=time)
    outputs={f['name']:evaluate(parse(f['expr']),env) for f in model.get('observables',[])}
    if model.get('formulation',{}).get('kinematics')=='axisymmetric_x' and 'stress' in outputs and not axisymmetric_x(outputs['stress'].v):
        raise ValueError('axisymmetric_x stress observable is outside its declared scope')
    return outputs


def all_models():
    return [load(p) for p in sorted((ROOT/'models').glob('*.json'))]
