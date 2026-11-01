"""Python-only investigation of derived finite SANISAND hardening products."""
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.dsl import I, Sym, Type, ValidationError, dimensions, evaluate, infer, parse
from tools.inspect_sanisand_original import load_fragment as load_original


def load_fragment(root=ROOT):
    original=load_original(root)
    fragment=json.loads((root/'catalogue/source-audits/sanisand-2004-hardening-limit.json').read_text())
    if fragment['source']!=original['source'] or fragment['inputs']!=original['inputs']:
        raise ValidationError('limit fragment must retain original source and input identity')
    symbols={'I':Type('sym'),**{n:Type(s['shape'],dimensions(s['unit'])) for n,s in fragment['inputs'].items()}}
    for term in fragment['terms']:
        if term['name'] in symbols or infer(parse(term['expression']),symbols)!=Type(term['shape'],dimensions(term['unit'])):
            raise ValidationError('duplicate or incorrectly typed limit term: '+term['name'])
        symbols[term['name']]=Type(term['shape'],dimensions(term['unit']))
    # Keep all unchanged source expressions exactly equal to the pinned draft.
    old={t['name']:t for t in original['terms']}
    changed={'plastic_multiplier','plastic_strain_increment','stress_increment',
             'backstress_increment','fabric_increment','void_ratio_increment'}
    for t in fragment['terms']:
        if t['name'] in old and t['name'] not in changed and t!=old[t['name']]:
            raise ValidationError('limit fragment changes unrelated source terms')
    return fragment


def evaluate_fragment(fragment, **supplied):
    """Same on-cone scope as the original helper, allowing the derived zero limit."""
    if set(supplied)-set(fragment['inputs']): raise ValidationError('unknown limit inputs')
    env={'I':I}
    for name,spec in fragment['inputs'].items():
        value=supplied.get(name,spec.get('default'))
        if spec['shape']=='sym':
            if not isinstance(value,Sym) or len(value.v)!=6:raise ValidationError('six Mandel components required')
            values=value.v
        else:values=(value,)
        if any(type(x) not in (int,float) or not math.isfinite(x) for x in values):raise ValidationError('finite inputs required')
        env[name]=value
    p=sum(env['sigma'].v[:3])/3
    if not (p>0 and env['p_at']>0 and env['e']>0 and -1<env['nu']<.5 and
            0<env['c']<=1 and env['m']>0 and env['G0']>0 and env['h0']>0 and
            1-env['ch']*env['e']>0 and env['A0']>=0 and env['cz']>=0 and env['zmax']>=0):
        raise ValidationError('outside limit audit parameter domain')
    for name in ['alpha','alpha_in','z']:
        v=env[name].v
        if abs(sum(v[:3]))>fragment['audit_domain']['deviatoric_trace_tolerance']*max(1.,max(abs(x) for x in v)):
            raise ValidationError('deviatoric history required')
    delta=[env['sigma'].v[i]/p-(1 if i<3 else 0)-env['alpha'].v[i] for i in range(6)]
    distance=math.sqrt(sum(x*x for x in delta));radius=math.sqrt(2/3)*env['m']
    if abs(distance-radius)>fragment['audit_domain']['on_cone_relative_tolerance']*radius:
        raise ValidationError('limit investigation requires state on the yield cone')
    try:
        for t in fragment['terms']:
            value=env[t['name']]=evaluate(parse(t['expression']),env)
            if t['name']=='hardening_distance' and value<0:raise ValueError('negative reversal distance')
            if t['name']=='hardening_numerator' and env['hardening_distance']==0 and value<=0:
                raise ValueError('zero-distance limit requires positive hardening numerator')
            if t['name']=='scaled_loading_denominator' and value==0:raise ValueError('singular scaled denominator')
            if any(not math.isfinite(x) for x in (value.v if isinstance(value,Sym) else (value,))):raise ValueError('nonfinite result')
    except (ValueError,ZeroDivisionError,OverflowError) as exc:
        raise ValidationError('state needs an unresolved hardening limit') from exc
    return {t['name']:env[t['name']] for t in fragment['terms']}
