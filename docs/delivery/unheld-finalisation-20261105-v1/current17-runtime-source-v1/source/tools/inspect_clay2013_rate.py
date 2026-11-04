"""Diagnostic zero-spin clay2013 source-rate algebra, not a material integrator."""
from __future__ import annotations

import json
import math
from pathlib import Path

from atlas.dsl import FUNCTIONS, I, Sym, Type, ValidationError, dimensions, infer, parse
from atlas.history import _evaluate  # shared pure finite-intermediate/lazy-branch evaluator
from atlas.model import ROOT

FRAGMENT_PATH = ROOT/'catalogue/source-audits/clay-hypoplasticity-2013-rate.json'
SOURCE_SHA256 = '21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281'
_INPUTS = {'sigma','stretching','e','phi_c','lambda_star','kappa_star','N','nu'}


def _scalar(x):
    try:
        if type(x) not in (int,float) or not math.isfinite(x) or float(x)!=x:
            raise ValidationError('finite binary64 real value required')
        return float(x)
    except (OverflowError, ValueError) as exc:
        raise ValidationError('finite binary64 real value required') from exc


def _sym(x):
    values = x.v if isinstance(x, Sym) else x
    if not isinstance(values,(list,tuple)) or len(values)!=6:
        raise ValidationError('six finite Mandel components required')
    return Sym(tuple(_scalar(v) for v in values))


def validate_fragment(fragment):
    if fragment.get('fragment_version')!='clay-source-rate-0.1' or fragment.get('model_id')!='hypoplastic-clay-2013':
        raise ValidationError('wrong clay source-rate fragment identity')
    if fragment['source']['sha256']!=SOURCE_SHA256 or fragment['source']['doi']!='10.1007/s11440-012-0199-y':
        raise ValidationError('wrong clay source identity')
    if set(fragment['inputs'])!=_INPUTS:
        raise ValidationError('exact explicit clay input set required')
    if fragment['constants']!={'p_ref':{'shape':'scalar','unit':'Pa','value':1000},
                               'lode_roundoff_allowance':{'shape':'scalar','unit':'1','value':64*math.ulp(1.)}}:
        raise ValidationError('fixed source reference pressure/roundoff policy changed')
    symbols={'I':Type('sym')}
    for name,spec in fragment['inputs'].items():
        expected=Type('sym' if name in ('sigma','stretching') else 'scalar',
                                                  dimensions('Pa' if name=='sigma' else '1'))
        actual=Type(spec['shape'],dimensions(spec['unit']))
        if actual!=expected:
            raise ValidationError('incorrect clay input type: '+name)
        symbols[name]=actual
    for name,spec in fragment['constants'].items():
        _scalar(spec['value']);symbols[name]=Type(spec['shape'],dimensions(spec['unit']))
    for term in fragment['terms']:
        name=term['name']
        if name in symbols or name in FUNCTIONS or not name.isidentifier():
            raise ValidationError('duplicate or reserved clay term')
        if infer(parse(term['expression']),symbols)!=Type(term['shape'],dimensions(term['unit'])):
            raise ValidationError('clay source-rate type mismatch: '+name)
        symbols[name]=Type(term['shape'],dimensions(term['unit']))
        if not term['locator'].strip():
            raise ValidationError('clay source locator required')
        for check in term.get('checks',[]):
            if infer(parse(check),symbols)!=Type('bool'):
                raise ValidationError('clay term check must be Boolean')
    if fragment['outputs']!=['stress_rate','e_rate'] or symbols.get('stress_rate')!=Type('sym',dimensions('Pa')) or symbols.get('e_rate')!=Type():
        raise ValidationError('clay rate outputs required')
    return fragment


def load_fragment(path=FRAGMENT_PATH):
    return validate_fragment(json.loads(Path(path).read_text()))


def _positive_definite(sigma):
    scale=max(map(abs,sigma.v))
    if not scale:
        raise ValidationError('strictly positive-definite compression stress required')
    x,y,z,u,v,w=(q/scale for q in sigma.v)
    r=math.sqrt(2.)
    matrix=[[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]
    L=[[0.]*3 for _ in range(3)]
    try:
        for i in range(3):
            for j in range(i+1):
                residual=matrix[i][j]-math.fsum(L[i][k]*L[j][k] for k in range(j))
                if i==j:
                    if residual<=0:
                        raise ValidationError('strictly positive-definite compression stress required')
                    L[i][j]=math.sqrt(residual)
                else:
                    L[i][j]=residual/L[j][j]
    except (ArithmeticError,ValueError) as exc:
        raise ValidationError('undefined compression-stress domain') from exc


def evaluate_rate(fragment, sigma, stretching, e, *, phi_c, lambda_star, kappa_star, N, nu):
    """Return all typed terms in compression-positive Mandel coordinates.

    Parameters are explicit and source pressure is fixed to1000Pa. Diagnostic
    scope checks evaluability, not ASBS/physical admissibility. No update occurs.
    """
    sigma,stretching=_sym(sigma),_sym(stretching)
    params={k:_scalar(v) for k,v in dict(e=e,phi_c=phi_c,lambda_star=lambda_star,
                                      kappa_star=kappa_star,N=N,nu=nu).items()}
    if not (params['e']>=0 and params['lambda_star']>params['kappa_star']>0 and
            -1<params['nu']<.5 and 0<params['phi_c']<math.pi/2):
        raise ValidationError('outside explicit clay diagnostic parameter domain')
    _positive_definite(sigma)
    env=dict(I=I,sigma=sigma,stretching=stretching,**params)
    env.update({name:spec['value'] for name,spec in fragment['constants'].items()})
    exact_isotropic=sigma.v[0]==sigma.v[1]==sigma.v[2] and all(v==0 for v in sigma.v[3:])
    try:
        for term in fragment['terms']:
            env[term['name']]=_evaluate(parse(term['expression']),env)
            if term['name']=='j2' and env['j2']==0 and not exact_isotropic:
                raise ValidationError('nonisotropic deviator norm underflow; no isotropic substitution')
            for check in term.get('checks',[]):
                if _evaluate(parse(check),env) is not True:
                    raise ValidationError('clay domain check failed at '+term['name'])
    except (ArithmeticError,ValueError,TypeError) as exc:
        raise ValidationError('undefined clay rate; no regularization selected: '+str(exc)) from exc
    return {term['name']:env[term['name']] for term in fragment['terms']}
