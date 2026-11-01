"""Research fragment runner: restricted existing DSL, supplied linear host action."""
import json, math
from pathlib import Path
from atlas.dsl import Sym, I, Type, dimensions, parse, infer, ValidationError
from atlas.history import _evaluate
ROOT=Path(__file__).resolve().parents[1]

def load_fragment():
    return json.loads((ROOT/'catalogue/source-audits/gis-2024-supplied-host-rates.json').read_text())

def validate_fragment(fragment):
    if fragment.get('id')!='gis-2024-supplied-host-rates' or fragment.get('candidate_id')!='hypoplastic-generalized-igs-2024':
        raise ValidationError('wrong GIS source fragment identity')
    if fragment['source']['sha256']!='39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3' or fragment['source']['doi']!='10.1016/j.compgeo.2024.106480':
        raise ValidationError('wrong GIS source identity')
    if fragment['outputs']!=['h_rhs','Omega_rhs','sigma_rhs']:
        raise ValidationError('GIS directional rate outputs required')
    expected_names={'de','h','Omega','m','C','S','f','R','m_R','m_T','beta_R','chi_R','gamma_chi','chi_0','chi_max','C_Omega','gamma_Omega'}
    if set(fragment['inputs'])!=expected_names:
        raise ValidationError('exact GIS source input names required')
    action=fragment['host_action']
    if action['name']!='E' or action['unit']!='Pa' or action['input']!='effective_de' or action['output']!={'name':'E_effective_de','shape':'sym','unit':'Pa'}:
        raise ValidationError('incorrect supplied GIS host action contract')
    symbols={'I':Type('sym')}
    for name,spec in fragment['inputs'].items():
        actual=Type(spec['shape'],dimensions(spec['unit']))
        if actual!=Type('sym' if name in ('de','h','m','f') else 'scalar'):
            raise ValidationError('incorrect GIS input type: '+name)
        symbols[name]=actual
    symbols['E_effective_de']=Type('sym',dimensions('Pa'))
    for term in fragment['terms']:
        typ=infer(parse(term['expression']),symbols)
        if typ != Type(term['shape'],dimensions(term['unit'])):
            raise ValidationError('term dimension/shape mismatch: '+term['name'])
        if term['name'] in symbols:raise ValidationError('duplicate term')
        symbols[term['name']]=typ
    return fragment

def real(value):
    try: valid=type(value) in (int,float) and math.isfinite(value) and float(value)==value
    except (OverflowError,ValueError):valid=False
    if not valid:raise ValidationError('expected finite real, excluding bool')
    return float(value)

def vector(value):
    if not isinstance(value,Sym) or len(value.v)!=6:raise ValidationError('expected six-component Sym')
    return Sym(tuple(real(v) for v in value.v))

def finite(value):
    for x in value.v if isinstance(value,Sym) else (value,):
        real(x)
    return value

def rates(fragment,*,E,**values):
    validate_fragment(fragment)
    if set(values)!=set(fragment['inputs']):raise ValidationError('exact input names required')
    env={'I':I}
    for name,spec in fragment['inputs'].items():
        env[name]=vector(values[name]) if spec['shape']=='sym' else real(values[name])
    if type(E) not in (list,tuple) or len(E)!=6 or any(type(row) not in (list,tuple) or len(row)!=6 for row in E):
        raise ValidationError('E must be finite 6x6 Mandel linear-action matrix')
    matrix=[[real(v) for v in row] for row in E]
    positive=['R','beta_R','chi_R','gamma_chi','chi_0','gamma_Omega']
    if any(env[n]<=0 for n in positive) or env['chi_max']<env['chi_0'] or env['C_Omega']<0 or not 1<=env['m_T']<=env['m_R'] or not 0<=env['Omega']<=1 or env['C']<0 or env['S']<0:
        raise ValidationError('outside bounded fragment audit domain')
    hn=math.hypot(*env['h'].v);mn=math.hypot(*env['m'].v)
    if hn>env['R']+16*math.ulp(env['R']) or abs(mn-1)>1e-12:raise ValidationError('h outside radius or nonnormalized m')
    zero=all(v==0 for v in env['de'].v)
    if zero and any(v!=0 for v in env['f'].v):raise ValidationError('zero direction requires zero homogeneous f')
    try:
        for term in fragment['terms']:
            name=term['name']
            if zero and name=='q':
                env.update(q=None,k=None,suppression=None,h_rhs=Sym((0.,)*6),Omega_rhs=0.,effective_de=Sym((0.,)*6),sigma_rhs=Sym((0.,)*6))
                break
            if name=='sigma_rhs':
                v=env['effective_de'].v
                env['E_effective_de']=finite(Sym(tuple(sum(matrix[i][j]*v[j] for j in range(6)) for i in range(6))))
            env[name]=finite(_evaluate(parse(term['expression']),env))
            if name=='q' and not -1-64*math.ulp(1.)<=env[name]<=1+64*math.ulp(1.):
                raise ValueError('unresolved loading cosine outside roundoff margin')
            if name=='k' and env[name]<=0:
                raise ValueError('unresolved positive stiffness multiplier')
            if name in ('hn','dn') and env[name]==0 and any(v!=0 for v in env['h' if name=='hn' else 'de'].v):
                raise ValueError('nonzero direction norm underflow')
    except (ArithmeticError,ValueError,TypeError) as exc:
        raise ValidationError('fragment arithmetic/domain failure: '+str(exc)) from exc
    return {name:env[name] for name in [t['name'] for t in fragment['terms']]}
