"""Typed physical-time external fields; generated equations remain model agnostic."""
from dataclasses import dataclass,asdict
from copy import deepcopy
import hashlib,json,math
from .dsl import I,Sym,Type,TIME,dimensions,evaluate,parse,ValidationError,FUNCTIONS
from .model import IDENT,RESERVED,field_type,axisymmetric_x
from .path import PATH_RESERVED,checked_mapping,components,unpack,check_parameters
PROFILE='controlled-time-ode-v1'
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def size(f):return 6 if f['shape']=='sym' else 1
def identity(model):return hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def control_fields(model):return [dict(name=n,**f) for n,f in sorted(model['formulation']['controls'].items())]
def validate_inputs(model):
    controls=model['formulation']['controls'];inputs=model['formulation']['inputs']['equation']
    if len(model['parameters'])>256:raise ValidationError('at most 256 controlled-time parameters')
    if sum(size(f) for f in controls.values())>32:raise ValidationError('at most 32 control components')
    if sum(size(f) for f in inputs.values())>65:raise ValidationError('at most 65 equation input components')
    if sum(size(f) for f in model.get('observables',[]))>144:raise ValidationError('at most 144 observable components')
    forbidden=RESERVED|PATH_RESERVED|{'start_time','duration'}
    mechanical={'quantity':'strain','shape':'sym','unit':'1','constraint':'finite','measure':'infinitesimal_strain','configuration':'current'}
    if controls.get('strain')!=mechanical:raise ValidationError('strain control requires fixed-frame symmetric infinitesimal Mandel strain')
    for n,f in controls.items():
        if not IDENT.fullmatch(n) or n in forbidden or n.endswith('_n'):raise ValidationError('invalid controlled-time control name')
        if n!='strain' and (f['shape']!='scalar' or 'measure' in f or 'configuration' in f):raise ValidationError('nonmechanical controls must be scalar fields')
        unit=dimensions(f['unit'])
        if f['quantity'] in ('temperature','suction') and unit!=dimensions('K' if f['quantity']=='temperature' else 'Pa'):raise ValidationError('physical field quantity requires SI temperature/pressure units')
        if n!='strain' and f['quantity'] in ('strain','strain_rate','time','duration','path_coordinate','path_progress'):raise ValidationError('mechanical and clock quantities cannot be scalar external fields')
    pairs=set()
    for n,f in inputs.items():
        if n=='time':continue
        if not IDENT.fullmatch(n) or n.endswith('_n') or (n in forbidden and n!='strain_rate'):raise ValidationError('invalid controlled-time input name')
        b=f['binding'];key=b['control'];order=b['derivative_order']
        if type(order) is not int or order not in (0,1) or key not in controls:raise ValidationError('invalid control binding')
        if (key,order) in pairs:raise ValidationError('duplicate control derivative binding')
        pairs.add((key,order));c=controls[key]
        expected=tuple(a-order*b for a,b in zip(dimensions(c['unit']),TIME))
        if f['shape']!=c['shape'] or dimensions(f['unit'])!=expected or f['quantity']!=c['quantity']+('_rate' if order else ''):raise ValidationError('control input shape, quantity or derivative units mismatch')
        if key=='strain':
            if f.get('measure')!=('infinitesimal_strain_rate' if order else 'infinitesimal_strain') or f.get('configuration')!='current':raise ValidationError('mechanical input measure/configuration mismatch')
        elif 'measure' in f or 'configuration' in f:raise ValidationError('scalar fields cannot declare mechanical measures')
    if inputs['strain_rate']['binding']!={'control':'strain','derivative_order':1}:raise ValidationError('strain_rate must bind the mechanical derivative')

def controls_checked(model,values,label,*,rates=False):
    fields=control_fields(model);flat=components(values,fields)
    if not rates:
        for f in fields:
            vals=values[f['name']] if size(f)==6 else [values[f['name']]]
            if f['constraint']=='positive_finite' and any(v<=0 for v in vals):raise ValueError(label+': positive value required')
            if f['constraint']=='nonnegative_finite' and any(v<0 for v in vals):raise ValueError(label+': nonnegative value required')
    return flat

def inputs_at(model,time,values,rates):
    if not finite(time):raise ValueError('finite physical time required')
    controls_checked(model,values,'controls');controls_checked(model,rates,'control rates',rates=True)
    env={'time':time}
    for n,f in model['formulation']['inputs']['equation'].items():
        if n=='time':continue
        b=f['binding'];v=(rates if b['derivative_order'] else values)[b['control']]
        env[n]=Sym(tuple(v)) if f['shape']=='sym' else v
    if model['formulation']['kinematics']=='axisymmetric_x' and not axisymmetric_x(env['strain_rate'].v):raise ValueError('axisymmetric strain-rate required')
    return env

def evaluate_stage(model,state,parameters,time,values,rates,*,initial=False):
    check_parameters(model,parameters);components(state,model['state'])
    env={'I':I,**parameters,**inputs_at(model,time,values,rates)}
    for f in model['state']:
        v=state[f['name']];env[f['name']]=Sym(tuple(v)) if size(f)==6 else v
    for f in model['derived']:env[f['name']]=evaluate(parse(f['expr']),env)
    if not all(evaluate(parse(c),env) for c in model['domain']):raise ValueError('outside controlled-time domain')
    if initial and not all(evaluate(parse(c),env) for c in model.get('initial_checks',[])):raise ValueError('inadmissible initial state')
    rr={n:evaluate(parse(e),env) for n,e in model['equations'].items()}
    rr={n:list(v.v) if isinstance(v,Sym) else v for n,v in rr.items()};components(rr,model['state'])
    oo={f['name']:evaluate(parse(f['expr']),env) for f in model.get('observables',[])}
    if model['formulation']['kinematics']=='axisymmetric_x' and 'stress' in oo and not axisymmetric_x(oo['stress'].v):raise ValueError('axisymmetric stress required')
    oo={n:list(v.v) if isinstance(v,Sym) else v for n,v in oo.items()}
    scales=[]
    for f in model['state']:
        v=evaluate(parse(f['scale']),parameters)
        if not finite(v) or v<=0:raise ValueError('positive finite state scale required')
        scales.extend([v]*size(f))
    return rr,oo,scales

@dataclass(frozen=True)
class Context:
    state:dict
    time:float
    controls:dict
    control_rates:dict
    parameters:dict
    model_sha256:str
    profile:str=PROFILE
@dataclass(frozen=True)
class Settings:
    absolute_scale_fraction:float=1e-11
    relative_tolerance:float=1e-8
    minimum_step_seconds:float=1e-12
    maximum_step_seconds:float=1.
    maximum_depth:int=40
    maximum_trials:int=100000
    def check(self):
        a,r,mi,ma,d,t=asdict(self).values()
        if any(not finite(v) or v<=0 for v in (a,r,mi,ma)) or mi>ma or type(d) is not int or not 1<=d<=60 or type(t) is not int or not 1<=t<=1000000:raise ValueError('invalid controlled-time execution settings')
@dataclass(frozen=True)
class Result:
    context:Context
    observables:dict
    left_observables:dict
    right_observables:dict
    diagnostics:dict

def initialize(model,state,time,controls,control_rates,parameters):
    from .model import validate,controlled_time
    validate(model)
    if not controlled_time(model):raise ValueError('controlled-time profile required')
    evaluate_stage(model,state,parameters,time,controls,control_rates,initial=True)
    return Context(deepcopy(state),time,deepcopy(controls),deepcopy(control_rates),deepcopy(parameters),identity(model))

def stage_controls(model,start,end,duration,fraction):
    if not finite(duration) or duration<=0 or not finite(fraction) or not 0<=fraction<=1:raise ValueError('positive duration and finite stage fraction in [0,1] required')
    fields=control_fields(model);a=controls_checked(model,start,'start');b=controls_checked(model,end,'end')
    vals=[];rates=[]
    for x,z in zip(a,b):
        delta=z-x;rate=delta/duration;value=x if fraction==0 else z if fraction==1 else x+fraction*delta
        if not all(finite(v) for v in (delta,rate,value)):raise ValueError('nonfinite interpolated control or rate')
        vals.append(value);rates.append(rate)
    return unpack(vals,fields),unpack(rates,fields)

def advance(model,parent,duration,controls_start,controls_end,settings=Settings()):
    settings.check()
    if parent.profile!=PROFILE or parent.model_sha256!=identity(model):raise ValueError('context identity/profile mismatch')
    from .model import validate
    validate(model)
    evaluate_stage(model,parent.state,parent.parameters,parent.time,parent.controls,parent.control_rates)
    if controls_start!=parent.controls:raise ValueError('start controls differ from committed values')
    endpoint=parent.time+duration if finite(duration) else float('nan')
    if not finite(duration) or duration<=0 or not finite(endpoint) or not endpoint>parent.time:raise ValueError('positive representable physical duration required')
    _,left,scales=evaluate_stage(model,parent.state,parent.parameters,parent.time,parent.controls,parent.control_rates)
    fields=model['state'];y0=components(parent.state,fields);trials=accepted=rejected=0;last_error=0.
    def rhs(y,offset):
        values,rates=stage_controls(model,controls_start,controls_end,duration,offset/duration)
        rr,oo,_=evaluate_stage(model,unpack(y,fields),parent.parameters,parent.time+offset,values,rates)
        return components(rr,fields),oo
    _,right=rhs(y0,0)
    def midpoint(y,t,h):
        a,_=rhs(y,t);b,_=rhs([x+h*.5*v for x,v in zip(y,a)],t+h*.5)
        out=[x+h*v for x,v in zip(y,b)];rhs(out,t+h);return out
    def integrate(y,t,h,depth):
        nonlocal trials,accepted,rejected,last_error
        trials+=1
        if trials>settings.maximum_trials or not t+h>t or not parent.time+t+h>parent.time+t or not t+h*.5>t or not parent.time+t+h*.5>parent.time+t:raise ValueError('trial budget or physical clock resolution exhausted')
        error=float('inf');candidate=None
        if h<=settings.maximum_step_seconds:
            try:
                full=midpoint(y,t,h);half=midpoint(y,t,h*.5);candidate=midpoint(half,t+h*.5,h*.5)
                weights=[3*(settings.absolute_scale_fraction*s+settings.relative_tolerance*max(abs(x),abs(z))) for x,z,s in zip(y,candidate,scales)]
                diffs=[abs(x-z) for x,z in zip(full,candidate)]
                if all(finite(w) and w>0 for w in weights) and all(finite(d) for d in diffs):error=max(d/w for d,w in zip(diffs,weights))
            except (ValueError,ArithmeticError):pass
        if error<=1:accepted+=2;last_error=error;return candidate
        rejected+=1
        if depth>=settings.maximum_depth or h*.5<settings.minimum_step_seconds:raise ValueError('time refinement/domain failure')
        return integrate(integrate(y,t,h*.5,depth+1),t+h*.5,h*.5,depth+1)
    result=integrate(y0,0,duration,0);_,obs=rhs(result,duration)
    values,rates=stage_controls(model,controls_start,controls_end,duration,1)
    context=Context(unpack(result,fields),endpoint,values,rates,deepcopy(parent.parameters),parent.model_sha256)
    return Result(context,obs,left,right,dict(trials=trials,accepted_half_steps=accepted,rejected_trials=rejected,final_error=last_error))

def context_from_dict(model,data):
    required={'state','time','controls','control_rates','parameters','model_sha256','profile'}
    if not isinstance(data,dict) or set(data)!=required:raise ValueError('complete controlled-time restart context required')
    if data['profile']!=PROFILE or data['model_sha256']!=identity(model):raise ValueError('restart profile/model identity mismatch')
    # Restart validates evolving domain, not initialization-only preparation checks.
    from .model import validate
    validate(model);evaluate_stage(model,data['state'],data['parameters'],data['time'],data['controls'],data['control_rates'])
    return Context(**deepcopy(data))

def validate_request(model,request):
    from .model import ROOT
    from .structure import check
    check(request,json.loads((ROOT/'schemas/run-controlled-time-v1.schema.json').read_text()))
    if request['model']!=model['id'] or request['profile']!=PROFILE:raise ValueError('request model/profile mismatch')
    parent=context_from_dict(model,request['context']);settings=Settings(**request['settings']);settings.check()
    total=0;ids=set();time=parent.time;current=parent.controls
    for segment in request['segments']:
        if segment['id'] in ids:raise ValueError('duplicate segment id')
        ids.add(segment['id']);duration=segment['duration'];endtime=time+duration
        if not finite(endtime) or endtime<=time:raise ValueError('unrepresentable segment endpoint')
        controls_checked(model,segment['controls_end'],'end controls');stage_controls(model,current,segment['controls_end'],duration,1)
        previous=time
        for i in range(1,segment['samples']+1):
            t=endtime if i==segment['samples'] else time+duration*i/segment['samples']
            if not t>previous:raise ValueError('unrepresentable output sample interval')
            previous=t
        total+=segment['samples'];time=endtime;current=segment['controls_end']
    if total>10000:raise ValueError('at most 10000 output intervals')
    return deepcopy(request)

def run(model,request,advance_function=advance):
    spec=validate_request(model,request);current=context_from_dict(model,spec['context']);settings=Settings(**spec['settings']);points=[]
    for segment in spec['segments']:
        start=current;duration=segment['duration']
        for i in range(1,segment['samples']+1):
            fraction=i/segment['samples'];end,_=stage_controls(model,start.controls,segment['controls_end'],duration,fraction)
            time=start.time+duration if i==segment['samples'] else start.time+duration*fraction
            result=advance_function(model,current,time-current.time,current.controls,end,settings)
            if i==1:points.append(dict(segment=segment['id'],side='left',context=asdict(current),observables=result.left_observables));points.append(dict(segment=segment['id'],side='right',context={**asdict(current),'control_rates':deepcopy(result.context.control_rates)},observables=result.right_observables))
            points.append(dict(segment=segment['id'],side='end',context=asdict(result.context),observables=result.observables,diagnostics=result.diagnostics));current=result.context
    return dict(profile=PROFILE,model=model['id'],model_sha256=identity(model),request=spec,context=asdict(current),points=points)
