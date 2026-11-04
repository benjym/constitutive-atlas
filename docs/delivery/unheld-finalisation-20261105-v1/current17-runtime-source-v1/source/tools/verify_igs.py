"""IGS history/rate checks and independent Cartesian RK4 histories.

The project-authored VW96 Cartesian reference supplies the host response.
Odd/even host-rate decomposition recovers L:D and N without DSL evaluation.
This is numerical evidence, not independent scientific review.
"""
import argparse
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tools'))
from atlas.evidence import sha256
from verify_hypoplasticity import reference_rate as host_rate, matrix, mandel, inner, multiply, csv

MODEL = 'hypoplastic-sand-igs97'
# Fixed before initial execution; h needs its own dimensionless error scale.
TOLERANCES = {
    'rate': (1e-4, 1e-11, 1e-12, 1e-9),
    'path': (1., 1e-8, 1e-9, 2e-5),
    'reference': (.001, 1e-11, 1e-12, 1e-10),
}


def compare(actual, expected, tolerance):
    if len(actual) != len(expected) or not all(math.isfinite(x) for x in actual+expected):
        return False, None
    stress, void, history, relative = tolerance
    ratios = [abs(a-b)/((stress if i<6 else void if i==6 else history)+relative*abs(b))
              for i,(a,b) in enumerate(zip(actual,expected))]
    ratio = max(ratios, default=0)
    return ratio <= 1, ratio


def reference_rate(state, strain, parameters):
    """Contract the IGS operator in ordinary 3x3 Cartesian coordinates."""
    R, mR, mT, beta_r, chi = parameters[9:]
    D, H = matrix(strain), matrix(state[7:])
    hn = math.sqrt(inner(H,H))
    eta = [[x/hn if hn else 0. for x in row] for row in H]
    rho = min(hn/R, 1.)  # Explicit atlas numerical cap, not a source identity.
    projection = inner(eta,D)
    forward = host_rate(state[:7],strain,parameters[:9])
    backward = host_rate(state[:7],[-x for x in strain],parameters[:9])
    LD = [(a-b)/2 for a,b in zip(forward[:6],backward[:6])]
    normD = math.sqrt(inner(D,D))
    N = [(a+b)/(2*normD) if normD else 0. for a,b in zip(forward[:6],backward[:6])]
    unit = mandel(eta)
    positive = host_rate(state[:7],unit,parameters[:9])
    negative = host_rate(state[:7],[-x for x in unit],parameters[:9])
    Leta = [(a-b)/2 for a,b in zip(positive[:6],negative[:6])]
    weight = rho**chi
    multiplier = weight*mT+(1-weight)*mR
    correction = [weight*((1-mT)*a+b)*projection if projection>0
                  else weight*(mR-mT)*a*projection for a,b in zip(Leta,N)]
    stress = [multiplier*a+b for a,b in zip(LD,correction)]
    Hdot = [[D[i][j]-(rho**beta_r*eta[i][j]*projection if projection>0 else 0.)
             for j in range(3)] for i in range(3)]
    return stress+[forward[6]]+mandel(Hdot)


def collinear_axis(initial, strain, parameters):
    active = {i for v in [initial[7:],strain] for i,x in enumerate(v) if x!=0}
    if len(active)==1 and parameters[12]==.5:
        axis = next(iter(active))
        if abs(initial[7+axis])<=parameters[9]: return axis
    return None


def rk4(initial, strain, parameters, steps):
    """RK4, with exact history supplied at stages for collinear beta=1/2.

    Eliminating that scalar history ODE avoids its non-smooth zero crossing;
    stress and void ratio remain integrated and independently grid refined.
    Noncollinear histories and other exponents use full-state RK4.
    """
    z = initial.copy(); dt = 1/steps
    axis = collinear_axis(initial,strain,parameters)
    def set_history(state, t):
        if axis is not None:
            state[7:] = [0.]*6
            state[7+axis] = collinear_memory_half_exponent(initial[7+axis],t*strain[axis],parameters[9])
        return state
    def shifted(z,k,f,t):
        return set_history([a+dt*f*b for a,b in zip(z,k)],t)
    for step in range(steps):
        t = step/steps
        a = reference_rate(z,strain,parameters)
        b = reference_rate(shifted(z,a,.5,t+.5*dt),strain,parameters)
        c = reference_rate(shifted(z,b,.5,t+.5*dt),strain,parameters)
        d = reference_rate(shifted(z,c,1,t+dt),strain,parameters)
        z = set_history([x+dt*(w+2*y+2*t+u)/6 for x,w,y,t,u in zip(z,a,b,c,d)],(step+1)/steps)
    return z


def rotate(v,Q):
    transpose = [list(row) for row in zip(*Q)]
    return mandel(multiply(multiply(Q,matrix(v)),transpose))


def collinear_memory_half_exponent(history, increment, radius):
    """Exact scalar history for beta_r=1/2, including reversal through zero.

    Unloading is linear. For aligned loading, u=sqrt(abs(h)/R) obeys
    -u-log(1-u) = -u0-log(1-u0) + abs(remaining_strain)/(2R).
    A monotone scalar bisection inverts this integrated equation.
    """
    direction = 1 if increment>=0 else -1
    length = abs(increment);q = direction*history
    if q<0:
        if length<=-q: return history+increment
        length += q;q = 0.
    if q>=radius: return direction*radius
    u0 = math.sqrt(q/radius)
    target = length/(2*radius)-u0-math.log1p(-u0)
    lo,hi = u0,math.nextafter(1.,0.)
    for _ in range(80):
        u = (lo+hi)/2
        if -u-math.log1p(-u)<target: lo=u
        else: hi=u
    return direction*radius*((lo+hi)/2)**2


def execute(solver):
    description = json.loads(subprocess.check_output([str(solver),'--describe'],text=True))
    definition = json.loads((ROOT/'models'/f'{MODEL}.json').read_text())
    if definition != next(m for m in description['models'] if m['id']==MODEL):
        raise ValueError('Rebuild solver: embedded model differs')
    defaults = [p['default'] for p in definition['parameters'].values()]
    cases = []
    def invoke(mode,state,strain,parameters):
        args = ['--model',MODEL,'--mode',mode,'--parameters',csv(parameters),'--initial',csv(state),'--strain',csv(strain)]
        if mode=='evaluate': args += ['--current',csv(state)]
        p = subprocess.run([str(solver),*args],capture_output=True,text=True,timeout=30)
        return args,p.returncode,json.loads(p.stdout)
    directions = ([0]*6,[.001,0,0,0,0,0],[-.001,0,0,0,0,0],
                  [0,.001,0,0,0,0],[0,0,0,.001,0,0],[0,0,0,0,-.001,0],
                  [.001,-.0003,.0002,.0004,-.0002,.0001],[-.001,.0003,-.0002,-.0004,.0002,-.0001])
    variants = [defaults, defaults[:9]+[5e-5,10.,3.,1.,2.],defaults[:9]+[2e-4,2.,2.,2.,.5]]
    for k,params in enumerate(variants):
        R = params[9]
        memories = ([0]*6,[R,0,0,0,0,0],[-R,0,0,0,0,0],
                    [.4*R,0,0,0,0,0],[0,0,0,R,0,0],[.3*R,-.2*R,.1*R,.4*R,-.1*R,.2*R])
        for j,stress in enumerate(([1e5]*3+[0,0,0],[150000,90000,60000,8000,-5000,3000])):
            for h,memory in enumerate(memories):
                state = list(stress)+[.7]+list(memory)
                for d,strain in enumerate(directions):
                    expected = reference_rate(state,strain,params)
                    args,code,result = invoke('evaluate',state,strain,params)
                    ok,ratio = compare(result.get('values',[]),expected,TOLERANCES['rate'])
                    cases.append(dict(id=f'rate-params{k}-stress{j}-h{h}-D{d}',kind='cartesian-igs-rate',arguments=args,expected=expected,actual=result.get('values'),max_tolerance_ratio=ratio,passed=ok and code==0 and result.get('ok') is True))
    base = [150000,90000,60000,8000,-5000,3000,.7,3e-5,-2e-5,1e-5,4e-5,-1e-5,2e-5]
    strain = list(directions[6])
    args0,code0,result0 = invoke('evaluate',base,strain,defaults)
    for axis,angle in enumerate((.37,-.63,1.12)):
        c,s = math.cos(angle),math.sin(angle)
        Q = ([[1,0,0],[0,c,-s],[0,s,c]] if axis==0 else [[c,0,s],[0,1,0],[-s,0,c]] if axis==1 else [[c,-s,0],[s,c,0],[0,0,1]])
        state = rotate(base[:6],Q)+[base[6]]+rotate(base[7:],Q)
        deformation = rotate(strain,Q)
        args,code,result = invoke('evaluate',state,deformation,defaults)
        expected = rotate(result0['values'][:6],Q)+[result0['values'][6]]+rotate(result0['values'][7:],Q)
        ok,ratio = compare(result.get('values',[]),expected,TOLERANCES['rate'])
        cases.append(dict(id=f'oblique-history-covariance-{axis}',kind='fixed-frame-covariance',arguments=args,base_arguments=args0,rotation=Q,expected=expected,actual=result.get('values'),max_tolerance_ratio=ratio,passed=ok and code==0 and code0==0 and result.get('ok') is True))
    R = defaults[9]
    axis = [R,0,0,0,0,0];shear = [0,0,0,R,0,0]
    zero = [0]*6;initial = [1e5]*3+[0,0,0,.7]
    histories = {
        'initial-elastic-range': (zero,[[x*.1 for x in axis]]),
        'mobilisation': (zero,[[x*5 for x in axis]]),
        'saturated-loading': (axis,[axis]),
        'saturated-reversal-through-zero': (axis,[[-2*x for x in axis]]),
        'orthogonal-turn': (axis,[shear]),
        'small-cycles': (zero,[[x*f for x in shear] for f in (.2,-.4,.4,-.4,.2)]),
        'large-reversal': (zero,[[x*f for x in axis] for f in (5,-10,5)]),
        'mixed-turns': (base[7:],[[.3*R,-.2*R,.1*R,.5*R,-.1*R,.2*R],[-.2*R,.1*R,-.3*R,0,.4*R,-.1*R]]),
    }
    for name,(memory,history) in histories.items():
        start = initial+list(memory);actual = start.copy();reference = start.copy();segments = []
        active = {i for v in [memory]+history for i,x in enumerate(v) if x!=0}
        scalar_axis = next(iter(active)) if len(active)==1 else None
        scalar_memory = memory[scalar_axis] if scalar_axis is not None else None
        for deformation in history:
            levels = [];previous = None;converged = False;reference_ratio = None
            for steps in (128,256,512,1024,2048,4096):
                fine = rk4(reference,deformation,defaults,steps)
                if previous is not None:
                    converged,reference_ratio = compare(previous,fine,TOLERANCES['reference'])
                levels.append(dict(steps=steps,state=fine,comparison_to_previous=reference_ratio,converged=converged))
                if converged: break
                previous = fine
            args,code,result = invoke('integrate',actual,deformation,defaults)
            ok,ratio = compare(result.get('state',[]),fine,TOLERANCES['path'])
            final = result.get('state',[])
            radius = math.sqrt(sum(x*x for x in final[7:]))/R if len(final)==13 else None
            segments.append(dict(reference_scheme='RK4 with analytical collinear stage history' if collinear_axis(reference,deformation,defaults) is not None else 'full-state RK4',arguments=args,expected=fine,actual=final,reference_levels=levels,reference_converged=converged,reference_tolerance_ratio=reference_ratio,max_tolerance_ratio=ratio,history_radius_fraction=radius,diagnostics=result.get('diagnostics'),passed=ok and converged and code==0 and result.get('ok') is True and radius<1.01))
            if scalar_axis is not None:
                scalar_memory = collinear_memory_half_exponent(scalar_memory,deformation[scalar_axis],R)
                analytical = [0.]*13;analytical[7+scalar_axis] = scalar_memory
                native_memory = [0.]*7+final[7:]
                reference_memory = [0.]*7+fine[7:]
                analytical_ok,analytical_ratio = compare(native_memory,analytical,TOLERANCES['path'])
                _,rk4_analytical_ratio = compare(reference_memory,analytical,TOLERANCES['reference'])
                segments[-1]['analytical_history'] = dict(axis=scalar_axis,expected=scalar_memory,native_tolerance_ratio=analytical_ratio,rk4_tolerance_ratio=rk4_analytical_ratio,passed=analytical_ok)
                segments[-1]['passed'] = segments[-1]['passed'] and analytical_ok
            actual = final;reference = fine
        cases.append(dict(id='path-'+name,kind='independent-rk4-reference',initial=start,strain_segments=history,segments=segments,passed=all(s['passed'] for s in segments)))
    # Explicit numerical cap case in the accepted 1% overshoot band.
    state = initial+[1.005*R,0,0,0,0,0]
    args,code,result = invoke('evaluate',state,axis,defaults)
    expected = reference_rate(state,axis,defaults)
    ok,ratio = compare(result.get('values',[]),expected,TOLERANCES['rate'])
    cases.append(dict(id='numerical-rho-cap',kind='atlas-numerical-convention',arguments=args,expected=expected,actual=result.get('values'),max_tolerance_ratio=ratio,passed=ok and code==0 and result.get('ok') is True))
    for name,state,params in [('outside-history-ball',initial+[1.02*R,0,0,0,0,0],defaults),('tensile',[-1e5]*3+[0,0,0,.7]+zero,defaults),('inverted-stiffness',initial+zero,defaults[:10]+[1.,2.]+defaults[12:])]:
        args,code,result = invoke('integrate',state,axis,params)
        cases.append(dict(id='rollback-'+name,kind='invalid-state-or-parameters',arguments=args,initial=state,result=result,passed=code!=0 and result.get('ok') is False and result.get('state')==state))
    return dict(kind='igs-verification-report',model=MODEL,catalogue_hash=description['sha256'],parameters=defaults,parameter_variants=variants,
        oracle='Project-authored Cartesian IGS operator using odd/even decomposition of the separate VW96 Cartesian host; analytically eliminated collinear history and fixed-step RK4 (full-state for noncollinear paths). No DSL evaluator or production integrator; not independent authorship or executed external code.',
        tolerances={k:dict(stress_absolute_Pa=v[0],void_ratio_absolute=v[1],history_absolute=v[2],relative=v[3]) for k,v in TOLERANCES.items()},
        runtime=dict(python=platform.python_version(),platform=platform.platform(),solver_sha256=sha256(solver)),cases=cases,passed=all(c['passed'] for c in cases))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver',type=Path,default=ROOT/'build/atlas_solver')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args();report = execute(args.solver.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in report['cases'])}/{len(report['cases'])} IGS checks passed; {args.output}")
    for case in report['cases']:
        if not case['passed']: print('FAILED '+case['id'])
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
