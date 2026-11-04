"""Python-only typed evaluation of an on-cone SANISAND source fragment.

No native compilation, constitutive integration or model admission occurs here.
"""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.dsl import I, Sym, Type, ValidationError, dimensions, evaluate, infer, parse


def load_fragment(root=ROOT):
    fragment=json.loads((root/'catalogue/source-audits/sanisand-2004-original-equations.json').read_text())
    receipt=json.loads((root/fragment['source']['receipt']).read_text())
    source=next(r for r in receipt['records'] if r['id']=='sanisand-2004')
    if any(fragment['source'][k]!=source[k] for k in ['sha256','doi']):
        raise ValidationError('fragment source identity differs from receipt')
    symbols={'I':Type('sym')}
    symbols.update({n:Type(v['shape'],dimensions(v['unit'])) for n,v in fragment['inputs'].items()})
    for term in fragment['terms']:
        expected=Type(term['shape'],dimensions(term['unit']))
        if term['name'] in symbols or infer(parse(term['expression']),symbols)!=expected:
            raise ValidationError('duplicate or incorrectly typed term: '+term['name'])
        symbols[term['name']]=expected
    return fragment


def evaluate_fragment(fragment, **supplied):
    inputs=fragment['inputs']
    if set(supplied)-set(inputs): raise ValidationError('unknown fragment inputs')
    env={'I':I}
    for name,spec in inputs.items():
        value=supplied.get(name,spec.get('default'))
        if spec['shape']=='sym':
            if not isinstance(value,Sym) or len(value.v)!=6:
                raise ValidationError(name+' requires six Mandel components')
            values=value.v
        else: values=(value,)
        if any(type(x) not in (int,float) or not math.isfinite(x) for x in values):
            raise ValidationError('finite numeric inputs required: '+name)
        env[name]=value
    p=sum(env['sigma'].v[:3])/3
    if not (p>0 and env['p_at']>0 and -1<env['nu']<.5 and env['e']>0
            and 0<env['c']<=1 and env['m']>0 and env['G0']>0 and env['h0']>0
            and 1-env['ch']*env['e']>0 and env['A0']>=0 and env['cz']>=0
            and env['zmax']>=0):
        raise ValidationError('outside declared audit parameter domain')
    tolerance=fragment['audit_domain']['deviatoric_trace_tolerance']
    for name in ['alpha','alpha_in','z']:
        tensor=env[name].v
        if abs(sum(tensor[:3]))>tolerance*max(1.,max(abs(x) for x in tensor)):
            raise ValidationError('deviatoric history required: '+name)
    delta=[env['sigma'].v[i]/p-(1 if i<3 else 0)-env['alpha'].v[i] for i in range(6)]
    distance=math.sqrt(sum(x*x for x in delta));radius=math.sqrt(2/3)*env['m']
    if abs(distance-radius)>fragment['audit_domain']['on_cone_relative_tolerance']*radius:
        raise ValidationError('fragment is defined only on the yield cone')
    try:
        for term in fragment['terms']:
            name=term['name']
            value=env[name]=evaluate(parse(term['expression']),env)
            if name=='hardening_distance' and value<=0:
                raise ValueError('finite positive reversal distance required')
            if name=='loading_denominator' and value==0:
                raise ValueError('singular loading denominator')
            values=value.v if isinstance(value,Sym) else (value,)
            if not all(math.isfinite(x) for x in values): raise ValueError('nonfinite result')
    except (ValueError,ZeroDivisionError,OverflowError) as exc:
        raise ValidationError('source fragment needs an unresolved singular/domain policy') from exc
    return {t['name']:env[t['name']] for t in fragment['terms']}
