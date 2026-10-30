"""Model loading and semantic validation. JSON is the canonical YAML subset."""
from __future__ import annotations
import json
import math
import re
from pathlib import Path
from .dsl import DIMS, I, Sym, Type, ZERO, ValidationError, cpp, evaluate, infer, parse

ROOT = Path(__file__).resolve().parents[1]
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
RESERVED = {"I", "de", "dt", "T", "params", "z", "zn", "out", "domain", "true", "false",
            "double", "auto", "if", "else", "return", "const", "class", "struct", "template",
            "int", "float", "void", "bool", "new", "delete", "switch", "case", "default",
            "for", "while", "do", "break", "continue", "throw", "try", "catch", "namespace",
            "using", "typename", "static", "virtual", "public", "private", "protected"}


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
    if field.get('shape', 'scalar') not in ('scalar', 'sym') or field.get('unit', '1') not in DIMS:
        raise ValidationError('unsupported shape or unit')
    return Type(field.get('shape','scalar'), DIMS[field.get('unit','1')])


def validate(model):
    from .structure import check
    check(model,json.loads((ROOT/'schemas/model.schema.json').read_text()))
    required = {'schema_version','id','name','family','status','sources','parameters','state', 'derived','equations','domain','integration','description'}
    if not required <= model.keys():
        raise ValidationError(f"missing fields: {sorted(required-model.keys())}")
    if model['schema_version'] != '0.1' or model['integration'] not in ('residual','rate'):
        raise ValidationError('unsupported schema version or integration kind')
    if not re.fullmatch(r'[a-z][a-z0-9-]*',model['id']):
        raise ValidationError('invalid model ID')
    if model['status'] not in ('draft','transcribed','numerically-tested','reviewed'):
        raise ValidationError('invalid review status')
    if not model['sources'] or any(not {'url','locator','role'} <= s.keys() for s in model['sources']):
        raise ValidationError('source URL, locator and role are required')
    symbols = {'I':Type('sym'),'de':Type('sym')}
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
    if not model['state'] or model['state'][0]['name'] != 'sigma' or field_type(model['state'][0]) != Type('sym',DIMS['Pa']):
        raise ValidationError('first state must be symmetric stress sigma in Pa')
    count=0
    for field in model['state']:
        typ=field_type(field); name=field['name']
        declare(name,typ); symbols[name+'_n']=typ
        initial=field['initial']
        if typ.shape=='sym':
            if not isinstance(initial,list) or len(initial)!=6: raise ValidationError(f'{name}: six Mandel components required')
        else: initial=[initial]
        if any(type(v) not in (float,int) or not math.isfinite(v) for v in initial): raise ValidationError('nonfinite initial value')
        scale=parse(field['scale'])
        if infer(scale,symbols)!=Type(dim=typ.dim): raise ValidationError(f'{name}: scale must have matching units')
        if any(n.id not in model['parameters'] for n in __import__('ast').walk(scale) if isinstance(n,__import__('ast').Name)):
            raise ValidationError('state scales may reference parameters only')
        env={k:v['default'] for k,v in model['parameters'].items()}
        if not evaluate(scale,env)>0: raise ValidationError('state scale must be positive')
        count+=6 if typ.shape=='sym' else 1
        if field.get('multiplier') and (typ!=Type() or not field.get('transient') or model['integration']!='residual'):
            raise ValidationError('multipliers must be dimensionless transient scalars in residual models')
    if count>24: raise ValidationError('v0.1 supports at most 24 state components')
    for field in model['derived']:
        typ=infer(parse(field['expr']),symbols)
        if typ.shape=='bool': raise ValidationError('derived values must be numeric')
        declare(field['name'],typ)
    eqs=model['equations']
    if set(eqs)!={f['name'] for f in model['state']}: raise ValidationError('one equation per state is required')
    for f in model['state']:
        if infer(parse(eqs[f['name']]),symbols)!=field_type(f): raise ValidationError(f"{f['name']}: equation shape or dimensions mismatch")
    for condition in model['domain']:
        if infer(parse(condition),symbols)!=Type('bool'): raise ValidationError('domain checks must be comparisons')
    for condition in model.get('initial_checks',[]):
        if infer(parse(condition),symbols)!=Type('bool'): raise ValidationError('initial checks must be comparisons')
    return model


def defaults(model):
    return {name: p['default'] for name,p in model['parameters'].items()}


def interpret(model, state, previous, increment, parameters=None):
    env={'I':I,'de':Sym(tuple(increment)),**defaults(model),**(parameters or {})}
    for f in model['state']:
        name=f['name']; wrap=lambda v: Sym(tuple(v)) if f.get('shape')=='sym' else v
        env[name]=wrap(state[name]); env[name+'_n']=wrap(previous[name])
    for f in model['derived']: env[f['name']]=evaluate(parse(f['expr']),env)
    if not all(evaluate(parse(c),env) for c in model['domain']): raise ValueError('state outside model domain')
    return {k:evaluate(parse(expr),env) for k,expr in model['equations'].items()}


def all_models():
    return [load(p) for p in sorted((ROOT/'models').glob('*.json'))]
