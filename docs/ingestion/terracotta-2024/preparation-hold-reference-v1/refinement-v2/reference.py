"""Independent Figure1 full-path scalar reference. Python standard library only.

No Atlas modules, author-code execution, existing reference imports or compiled API.
The six integration quantities are four material states and two accumulated strains.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parent
PARAMETERS={'K':13e9,'G':5e9,'M':.73,'omega':.6,'p1':543e6,'Lambda':10.,
            'alpha':6e5,'gamma':6e5,'eta':150.,'Gamma':.001}
SOURCE_PINS=[
 {'role':'equation image','url':'https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/images/theModel.png','sha256':'e019012545c5fb0bb80c8f95bad68d35f458c9094ea471d8f42616a170dcc071','locator':'whole visually inspected equation image; journal images unverified'},
 {'role':'rounded code parameter preset, read only','url':'https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_main.py','sha256':'62c45ae3ba7d556956e4e29d940371a5f1a39b8feeb0d1a0c59db80fbe44a888','locator':'lines12–25, initial stress100kPa, phi.423,T0'},
 {'role':'code conflict identity, not executed','url':'https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_functions.py','sha256':'6f1d7bbc9e805cfa38230b1277a1b55a02f27ab4581e973f5a61c495262a0711','locator':'TmRate139–146 unhalved versus mixed residual301 halved'}]

def binary(value):
    x=float(value)
    return {'value':x,'hex':x.hex(),'ieee754_big_endian':struct.pack('>d',x).hex()}

def stresses(y,rate,p=PARAMETERS):
    v,s,T,f=y[:4];dv,ds=rate
    E=f**6
    pe=E*(p['K']*v*v+3*p['G']*s*s)/2
    qe=3*p['G']*E*v*s
    return pe,qe,pe+(2*p['alpha']*T*dv+T*T)/p['Gamma'],qe+2*p['gamma']*T*ds/p['Gamma']

def hold_rate(y,targets,p=PARAMETERS):
    if not y[2]>0: raise ValueError('positive temperature required; zero-temperature hold inversion is singular')
    pe,qe,_,_=stresses(y,(0.,0.),p)
    return ((p['Gamma']*(targets[0]-pe)-y[2]*y[2])/(2*p['alpha']*y[2]),
            p['Gamma']*(targets[1]-qe)/(2*p['gamma']*y[2]))

def derivative(y,rate,p=PARAMETERS):
    v,s,T,f=y[:4];dv,ds=rate
    pe,qe,_,_=stresses(y,rate,p)
    if not(v>0 and 0<f<=1 and T>=0 and pe>0): raise ValueError('nonpositive or unphysical material state')
    a=math.sqrt(p['eta']/p['alpha'])
    b=-a*qe/(p['M']**2*pe)
    c=math.sqrt(p['eta']/p['gamma'])/(p['M']*p['omega'])+a/p['M']**2
    if a*c-b*b<0 or p['K']*v*v<3*p['G']*s*s: raise ValueError('outside current nonstrict Figure1 domain')
    if not p['M']**2<=3*p['G']/p['K']<=p['M']**2*(1+math.sqrt(p['alpha']/p['gamma'])*p['M']/p['omega']):raise ValueError('global stress order fails')
    z=(T/(p['p1']*f**p['Lambda']))
    out=[dv-z*(a*pe+b*qe),ds-z*(b*pe+c*qe),p['alpha']*dv*dv+p['gamma']*ds*ds-p['eta']*T*T,f*dv,dv,ds]
    if not all(math.isfinite(x) for x in (*y,*rate,*out)):raise ValueError('nonfinite source calculation')
    return out

def tensor(v,s): return [v/3+s,v/3-s/2,v/3-s/2,0.,0.,0.]

def integrate(y,start,end,resolution,rate_at,method):
    n=round((end-start)*resolution);h=(end-start)/n
    current=list(y)
    def rhs(t,x):return derivative(x,rate_at(t,x))
    def shift(x,k,f):return [a+f*b for a,b in zip(x,k)]
    for i in range(n):
        t=start+i*h
        k1=rhs(t,current)
        k2=rhs(t+h/2,shift(current,k1,h/2))
        if method=='midpoint':current=shift(current,k2,h)
        elif method=='rk4':
            k3=rhs(t+h/2,shift(current,k2,h/2))
            k4=rhs(t+h,shift(current,k3,h))
            current=[v+h*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(current,k1,k2,k3,k4)]
        else:raise ValueError('unknown method')
    rhs(end,current)
    return current

def point(t,phase,side,y,rate):
    pe,qe,P,Q=stresses(y,rate)
    return {'time':t,'phase':phase,'side':side,'state':list(y[:4]),'strain':tensor(*y[4:]),'rate':tensor(*rate),'elastic_pressure':pe,'elastic_q':qe,'pressure':P,'signed_q':Q}

def full_path(initial,rate,resolution,method,policy):
    y=list(initial);points=[];last=0.
    for t in policy['phase_grids']['preparation']:
        if t>last:y=integrate(y,last,float(t),resolution,lambda tm,z:rate,method)
        points.append(point(float(t),'preparation','left' if t==10 else 'sample',y,rate));last=float(t)
    _,_,P,Q=stresses(y,rate);targets=(P,Q)
    # No reset, reinitialization or replacement by a converged preparation state.
    for t in policy['phase_grids']['hold']:
        if t>last:y=integrate(y,last,float(t),resolution,lambda tm,z:hold_rate(z,targets),method)
        points.append(point(float(t),'hold','right' if t==10 else 'sample',y,hold_rate(y,targets)));last=float(t)
    return {'steps_per_second':resolution,'transition_targets':{'pressure':P,'signed_q':Q},'points':points}

def generate():
    policy_bytes=(ROOT/'policy.json').read_bytes();policy=json.loads(policy_bytes)
    phi=.423;p=PARAMETERS
    initial=[math.sqrt(2*100000/(p['K']*phi**6)),0.,0.,phi,0.,0.]
    cases=[]
    for name,rates in [('compression',(0.,2e-5)),('extension',(0.,-2e-5)),('isotropic',(6e-5,0.))]:
        runs=[full_path(initial,rates,n,'rk4',policy) for n in policy['rk4_steps_per_second']]
        midpoint=full_path(initial,rates,policy['midpoint_steps_per_second'],'midpoint',policy)
        fine=runs[-1]
        cases.append({'id':name,'initial_state':initial[:4],'initial_strain':tensor(0.,0.),'initial_rate':tensor(*rates),'prep_rates_Dv_Ds':list(rates),'transition_targets':fine['transition_targets'],'points':fine['points'],'rk4_refinements':runs,'midpoint':midpoint})
    return {'identity':'terracotta-preparation-hold-reference-v2','schema_target':'0.3','profile':'physical_time/ode/axisymmetric_x/fixed_spatial/none/mandel/compression_positive/total stress observable','parameters':p,'source_pins':SOURCE_PINS,'journal_doi':'https://doi.org/10.1016/j.jmps.2024.105789','policy_sha256':hashlib.sha256(policy_bytes).hexdigest(),'reference_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_binary64':{'parameters':{k:binary(v) for k,v in p.items()},'initial_extended_state':[binary(x) for x in initial],'preparation_duration':binary(10.),'hold_duration':binary(20.),'rates':{case['id']:[binary(x) for x in case['prep_rates_Dv_Ds']] for case in cases}},'cases':cases,'limitations':['Author image/code preset only; journal-image reconciliation remains open.','Independent scalar numerical implementation by AI, not independent scientific review or experiment.','No author mixed-control execution or original outer-partition reproduction.','Positive-temperature stress inversion only; initial T0 is permitted only during prescribed-rate preparation.','No general3D/finite-rotation/AppendixB or source-domain expansion.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'references.json');args=parser.parse_args()
    if args.output.exists():raise SystemExit('refusing to overwrite retained observations')
    data=generate();args.output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('Generated three full paths, three RK4 levels and midpoint;22 points per path.')
