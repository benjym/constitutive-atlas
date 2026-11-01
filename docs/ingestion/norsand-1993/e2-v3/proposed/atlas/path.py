"""Generic declared dimensionless path ODEs. No constitutive model branches."""
from dataclasses import dataclass
from copy import deepcopy
import math
from .dsl import I, Sym, Type, ValidationError, dimensions, evaluate, parse
from .model import IDENT, RESERVED, axisymmetric_x, field_type, validate


def finite(x):
    return type(x) in (float, int) and math.isfinite(x)


def validate_inputs(model):
    inputs=model['formulation']['inputs']['equation']; controls={}; pairs=set()
    reserved=RESERVED|{'path_coordinate','start_coordinate','progress'}
    if len(inputs)>33: raise ValidationError('at most 32 control channels')
    for name,f in inputs.items():
        if name=='path_coordinate': continue
        if not IDENT.fullmatch(name) or name in reserved or name.endswith('_n'):
            raise ValidationError('invalid path input name')
        b=f['binding']; key=b['control']; pair=(key,b['derivative_order'])
        if not IDENT.fullmatch(key) or key in reserved or key.endswith('_n'):
            raise ValidationError('invalid control binding')
        if pair in pairs: raise ValidationError('duplicate control/order binding')
        pairs.add(pair); dim=dimensions(f['unit'])
        if key in controls and dim!=controls[key]: raise ValidationError('control units disagree')
        controls[key]=dim
    # External control keys are a separate namespace; equation symbols are not.


def control_names(model):
    return sorted({f['binding']['control'] for n,f in model['formulation']['inputs']['equation'].items() if n!='path_coordinate'})


def checked_mapping(values, names, label):
    if not isinstance(values,dict) or set(values)!=set(names) or any(not finite(v) for v in values.values()):
        raise ValueError('invalid '+label+' layout or finite values')


def components(state, fields):
    if not isinstance(state,dict) or set(state)!={f['name'] for f in fields}: raise ValueError('state layout mismatch')
    out=[]
    for f in fields:
        x=state[f['name']]
        if f['shape']=='sym':
            if not isinstance(x,(list,tuple)) or len(x)!=6: raise ValueError('six Mandel state components required')
            out.extend(x)
        else: out.append(x)
    if any(not finite(x) for x in out): raise ValueError('nonfinite state')
    return out


def unpack(values, fields):
    state={}; i=0
    for f in fields:
        n=6 if f['shape']=='sym' else 1
        state[f['name']]=values[i:i+n] if n==6 else values[i]; i+=n
    if i!=len(values): raise ValueError('state component count')
    return state


def check_parameters(model, params):
    checked_mapping(params,model['parameters'],'parameter')
    for n,f in model['parameters'].items():
        if not f['min']<=params[n]<=f['max']: raise ValueError('parameter outside declared bounds: '+n)


def stage_inputs(model, coordinate, start, end, fraction, progress):
    if not finite(coordinate) or not finite(fraction) or not 0<=fraction<=1: raise ValueError('invalid stage coordinate')
    inputs={'path_coordinate':coordinate}
    for n,f in model['formulation']['inputs']['equation'].items():
        if n=='path_coordinate': continue
        b=f['binding']; a=start[b['control']]; z=end[b['control']]
        # Endpoints are exact; overflow in a finite endpoint difference rejects.
        delta=z-a
        value=(delta/progress if progress else 0.) if b['derivative_order'] else (a if fraction==0 else z if fraction==1 else a+fraction*delta)
        if not finite(delta) or not finite(value): raise ValueError('nonfinite interpolated control')
        inputs[n]=value
    return inputs


def evaluate_stage(model,state,params,inputs,*,initial=False):
    check_parameters(model,params); components(state,model['state'])
    checked_mapping(inputs,model['formulation']['inputs']['equation'],'stage input')
    env={'I':I,**params,**inputs}
    for f in model['state']:
        x=state[f['name']];env[f['name']]=Sym(tuple(x)) if f['shape']=='sym' else x
    for f in model['derived']: env[f['name']]=evaluate(parse(f['expr']),env)
    if not all(evaluate(parse(c),env) for c in model['domain']): raise ValueError('outside path model domain')
    if initial and not all(evaluate(parse(c),env) for c in model.get('initial_checks',[])): raise ValueError('inadmissible initial state')
    rates={n:evaluate(parse(expr),env) for n,expr in model['equations'].items()}
    rates={n:list(v.v) if isinstance(v,Sym) else v for n,v in rates.items()}
    components(rates,model['state'])
    obs={f['name']:evaluate(parse(f['expr']),env) for f in model.get('observables',[])}
    if model['formulation']['kinematics']=='axisymmetric_x' and 'stress' in obs and not axisymmetric_x(obs['stress'].v):
        raise ValueError('stress outside axisymmetric scope')
    return rates,{n:list(v.v) if isinstance(v,Sym) else v for n,v in obs.items()}


@dataclass(frozen=True)
class Settings:
    absolute: float=1e-10
    relative: float=1e-8
    min_step: float=1e-12
    max_step: float=.001
    max_depth: int=40
    max_trials: int=100000

    def check(self):
        for n in ('absolute','relative','min_step','max_step'):
            if not finite(getattr(self,n)) or getattr(self,n)<=0: raise ValueError('invalid path setting '+n)
        if self.min_step>self.max_step: raise ValueError('minimum exceeds maximum step')
        for n in ('max_depth','max_trials'):
            if type(getattr(self,n)) is not int or not 1<=getattr(self,n)<=1000000: raise ValueError('invalid path budget')
        if self.max_depth>60: raise ValueError('maximum depth exceeds 60')


@dataclass(frozen=True)
class Context:
    state: dict
    coordinate: float
    controls: dict
    parameters: dict


def initialize(model,state,coordinate,controls,parameters):
    validate(model)
    if not finite(coordinate): raise ValueError('nonfinite path coordinate')
    checked_mapping(controls,control_names(model),'control'); check_parameters(model,parameters)
    evaluate_stage(model,state,parameters,stage_inputs(model,coordinate,controls,controls,0,0),initial=True)
    return Context(deepcopy(state),coordinate,deepcopy(controls),deepcopy(parameters))


def advance(model,parent,progress,controls_start,controls_end,settings=Settings()):
    """Returns a new context; any failure raises without mutating any caller object."""
    settings.check()
    initialize(model,parent.state,parent.coordinate,parent.controls,parent.parameters)
    names=control_names(model)
    checked_mapping(controls_start,names,'start control');checked_mapping(controls_end,names,'end control')
    if controls_start!=parent.controls: raise ValueError('start controls differ from committed context')
    if not finite(progress) or progress<0: raise ValueError('path progress must be nonnegative and finite')
    end_coordinate=parent.coordinate+progress
    if not finite(end_coordinate) or progress>0 and not end_coordinate>parent.coordinate: raise ValueError('unrepresentable path endpoint')
    if progress==0 and controls_end!=controls_start: raise ValueError('zero progress requires unchanged controls')
    inputs=lambda offset: stage_inputs(model,parent.coordinate+offset,controls_start,controls_end,offset/progress if progress else 0,progress)
    fields=model['state']; params=parent.parameters
    scales=[]
    for f in fields:
        x=evaluate(parse(f['scale']),params)
        if not finite(x) or x<=0: raise ValueError('invalid state scale')
        scales.extend([x]*(6 if f['shape']=='sym' else 1))
    y0=components(parent.state,fields)
    def rhs(y,t):
        r,_=evaluate_stage(model,unpack(y,fields),params,inputs(t))
        return components(r,fields)
    rhs(y0,0)
    if progress==0: return deepcopy(parent)
    trials=0
    def midpoint(y,t,h):
        a=rhs(y,t); mid=[x+h*.5*v for x,v in zip(y,a)]
        b=rhs(mid,t+h*.5); out=[x+h*v for x,v in zip(y,b)]
        rhs(out,t+h)
        return out
    def integrate(y,t,h,depth):
        nonlocal trials
        trials+=1
        if trials>settings.max_trials: raise ValueError('path trial budget exhausted')
        if not t+h>t or not parent.coordinate+t+h>parent.coordinate+t: raise ValueError('unrepresentable internal path step')
        error=float('inf'); candidate=None
        if h<=settings.max_step:
            try:
                full=midpoint(y,t,h);half=midpoint(y,t,h*.5);candidate=midpoint(half,t+h*.5,h*.5)
                error=max(abs(a-b)/(3*(settings.absolute*s+settings.relative*max(abs(x),abs(b)))) for a,b,x,s in zip(full,candidate,y,scales))
            except (ValueError,ArithmeticError): pass
        if error<=1: return candidate
        if depth>=settings.max_depth or h*.5<settings.min_step: raise ValueError('path refinement limit/domain failure')
        left=integrate(y,t,h*.5,depth+1)
        return integrate(left,t+h*.5,h*.5,depth+1)
    result=integrate(y0,0,progress,0)
    evaluate_stage(model,unpack(result,fields),params,inputs(progress))
    return Context(unpack(result,fields),end_coordinate,deepcopy(controls_end),deepcopy(params))
