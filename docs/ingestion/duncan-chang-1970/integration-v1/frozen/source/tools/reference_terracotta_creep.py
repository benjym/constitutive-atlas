"""Separate scalar Figure-1 reference for prepared constant-total-stress creep.

Only stdlib; no Atlas DSL/material integration or author functions are called.
RK4 refinement is cross-checked with explicit midpoint. This is independent
mathematical implementation, not independent scientific authorship or data.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

PARAMETERS = dict(Kmod=13e9,Gmod=5e9,Mcrit=.73,omega=.6,pOne=543e6,
                  Lambda=10,alpha=6e5,gamma=6e5,eta=150,Gamma=.001)
SOURCE = 'https://doi.org/10.1016/j.jmps.2024.105789'


def elastic(state, p):
    v,s,T,phi=state[:4]
    return (phi**6*(p['Kmod']*v*v+3*p['Gmod']*s*s)/2,
            3*p['Gmod']*phi**6*v*s)


def total_stress(state, rates, p):
    pe,qe=elastic(state,p);T=state[2];Dv,Ds=rates
    return (pe+(2*p['alpha']*T*Dv+T*T)/p['Gamma'],
            qe+2*p['gamma']*T*Ds/p['Gamma'])


def creep_rates(state, targets, p):
    """Exact algebraic elimination at Tm>0; singular origin is rejected."""
    if not state[2]>0:raise ValueError('stress-control elimination requires Tm > 0')
    pe,qe=elastic(state,p);T=state[2];pressure,q=targets
    return ((pressure-pe-T*T/p['Gamma'])*p['Gamma']/(2*p['alpha']*T),
            (q-qe)*p['Gamma']/(2*p['gamma']*T))


def rhs(state, rates, p):
    v,s,T,phi=state[:4];Dv,Ds=rates
    pe,qe=elastic(state,p)
    a=math.sqrt(p['eta']/p['alpha'])
    b=-a*qe/(p['Mcrit']**2*pe)
    c=math.sqrt(p['eta']/p['gamma'])/(p['Mcrit']*p['omega'])+a/p['Mcrit']**2
    if (not all(math.isfinite(x) for x in (*state,*rates,pe,qe,a,b,c))
            or not (v>0 and 0<phi<=1 and T>=0 and pe>0)
            or a*c<b*b or p['Kmod']*v*v<3*p['Gmod']*s*s):
        raise ValueError('reference stage outside current Figure1 draft domain')
    pc=p['pOne']*phi**p['Lambda']
    return [Dv-T/pc*(a*pe+b*qe),Ds-T/pc*(b*pe+c*qe),
            p['alpha']*Dv*Dv+p['gamma']*Ds*Ds-p['eta']*T*T,
            phi*Dv,Dv,Ds]


def advance(state, duration, steps, rates, p, method='rk4'):
    if type(steps) is not int or steps<=0 or not duration>0:
        raise ValueError('positive duration and integer steps required')
    if method not in ('rk4','midpoint'):raise ValueError('unknown reference method')
    y=list(state);h=duration/steps
    derivative=lambda z:rhs(z,rates(z),p)
    for _ in range(steps):
        k1=derivative(y)
        k2=derivative([a+h*b/2 for a,b in zip(y,k1)])
        if method=='midpoint':y=[a+h*b for a,b in zip(y,k2)]
        else:
            k3=derivative([a+h*b/2 for a,b in zip(y,k2)])
            k4=derivative([a+h*b for a,b in zip(y,k3)])
            y=[a+h*(b+2*c+2*d+e)/6 for a,b,c,d,e in zip(y,k1,k2,k3,k4)]
    derivative(y)  # Check the final stage too; no projection/repair.
    return y


def point(time,state,targets,p):
    rates=creep_rates(state,targets,p)
    Dv,Ds=rates;ev,es=state[4:]
    return {'time':time,'state':state[:4],
            'strain':[ev/3+es,ev/3-es/2,ev/3-es/2,0,0,0],
            'rate':[Dv/3+Ds,Dv/3-Ds/2,Dv/3-Ds/2,0,0,0],
            'elastic_pressure':elastic(state,p)[0], 'elastic_q':elastic(state,p)[1],
            'pressure':total_stress(state,rates,p)[0],
            'signed_q':total_stress(state,rates,p)[1]}


def generate():
    p=PARAMETERS.copy();phi=.423
    initial=[math.sqrt(2*100000/(p['Kmod']*phi**6)),0,0,phi,0,0]
    cases=[]
    for name,rate in [('compression',(0,2e-5)),('extension',(0,-2e-5)),('isotropic',(6e-5,0))]:
        prepared=[advance(initial,10,n,lambda z:rate,p) for n in (1000,2000,4000)]
        parent=prepared[-1];targets=total_stress(parent,rate,p)
        production=p['alpha']*rate[0]**2+p['gamma']*rate[1]**2
        exact_T=math.sqrt(production/p['eta'])*math.tanh(math.sqrt(production*p['eta'])*10)
        exact_phi=phi*math.exp(rate[0]*10)
        if abs(parent[2]-exact_T)>1e-13 or abs(parent[3]-exact_phi)>1e-13:
            raise AssertionError('preparation temperature/density analytical disagreement')
        if max(abs(a-b) for a,b in zip(creep_rates(parent,targets,p),rate))>1e-15:
            raise AssertionError('hold-entry rates do not recover preparation rates')
        rate_fn=lambda z:creep_rates(z,targets,p)
        histories=[]
        for n in (128,256,512):
            state=list(parent);points=[point(0,state,targets,p)]
            for i in range(1,11):
                state=advance(state,2,n,rate_fn,p)
                points.append(point(2*i,state,targets,p))
            histories.append(points)
        state=list(parent);midpoints=[point(0,state,targets,p)]
        for i in range(1,11):
            state=advance(state,2,2048,rate_fn,p,'midpoint')
            midpoints.append(point(2*i,state,targets,p))
        difference=lambda a,b,key:[max(abs(x[key][j]-y[key][j]) for x,y in zip(a,b))
                                   for j in range(len(a[0][key]))]
        errors={'preparation_state_last_pair':[abs(a-b) for a,b in zip(prepared[-2],parent)],
                'rk4_state_last_pair':difference(histories[-2],histories[-1],'state'),
                'rk4_strain_last_pair':difference(histories[-2],histories[-1],'strain'),
                'rk4_rate_last_pair':difference(histories[-2],histories[-1],'rate'),
                'rk4_state_first_pair':difference(histories[0],histories[1],'state'),
                'rk4_strain_first_pair':difference(histories[0],histories[1],'strain'),
                'rk4_rate_first_pair':difference(histories[0],histories[1],'rate'),
                'midpoint_state_difference':difference(midpoints,histories[-1],'state'),
                'midpoint_strain_difference':difference(midpoints,histories[-1],'strain'),
                'midpoint_rate_difference':difference(midpoints,histories[-1],'rate')}
        if max(errors['preparation_state_last_pair'])>1e-11 or max(errors['rk4_state_last_pair'])>1e-10 or max(errors['rk4_strain_last_pair'])>1e-10:
            raise AssertionError('reference refinement did not converge')
        if max(errors['midpoint_state_difference'])>1e-8 or max(errors['midpoint_strain_difference'])>1e-8:
            raise AssertionError('independent integration methods disagree')
        if max(errors['rk4_rate_last_pair'])>1e-10 or max(errors['midpoint_rate_difference'])>1e-8:
            raise AssertionError('reference rate disagreement')
        cases.append({'id':name,'preparation':{'duration':10,'rates_Dv_Ds':list(rate),
                      'initial_extended_state':initial,'rk4_steps':[1000,2000,4000],
                      'prepared_extended_state':parent},
                      'targets':{'pressure':targets[0],'signed_q':targets[1]},
                      'creep':{'duration':20,'sample_interval':2,'rk4_steps_per_sample':[128,256,512],
                               'midpoint_steps_per_sample':2048},'reference_errors':errors,
                      'time_origin':'hold elapsed time; preparation occupied preceding10s',
                      'rk4_refinement':[{'steps_per_sample':n,'points':pts} for n,pts in zip((128,256,512),histories)],
                      'points':histories[-1]})
    return {'version':'terracotta-scalar-creep-reference-0.1','source_url':SOURCE,
            'source_locator':'Figure1; Eqs23–24,29–32,36–38,42–43,48,51',
            'variant':'Figure1, unhalved temperature evolution; rounded author-code SI parameters',
            'parameters':p,'cases':cases,
            'scope':'Fixed-axis axisymmetric continuous law, frozen independently prepared initial state, constant total p/q; no author mixed-control routine, experimental data or full3D claim.',
            'limitations':['Separate mathematical implementation by AI, not independent scientific review.',
                           'Algebraic rate elimination requires positive Tm; no zero-Tm stress-control extension.',
                           'Reference refinement bounds are numerical study thresholds, not rigorous global error bounds.']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--model-definition',type=Path,required=True);args=parser.parse_args()
    data=generate();data['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    model=json.loads(args.model_definition.read_bytes())
    data['model_id']=model['id']
    data['model_sha256']=hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print(f'Generated {len(data["cases"])} prepared creep references')


if __name__=='__main__':main()
