"""Independent closed-form Cartesian/Mandel Burgers references. No Atlas imports.

Each deviatoric mode solves a two-exponential linear system (prescribed strain)
or a first-order forced Kelvin equation (prescribed stress). SI inputs are read
as their exact stored binary64 values. This is not a numerical time integrator.
"""
from decimal import Decimal as D, localcontext
import json
from pathlib import Path
R=Path(__file__).resolve().parent

def number(v): return D.from_float(float(v))
def dev(v):
    mean=sum(v[:3])/3
    return [x-(mean if j<3 else 0) for j,x in enumerate(v)]

def advance(state,strain,rate,h,params,kinds):
    K,gm,gk,em,ev=map(number,params);h=number(h)
    sigma,k=state[:6],state[6:];s=dev(sigma);p=sum(sigma[:3])/3
    v=dev(rate);mean=sum(rate[:3])/3
    sn=[];kn=[];en=[]
    a=-gm*(1/ev+1/em);b=2*gm*gk/ev;c=1/(2*ev);d=-gk/ev
    delta=((a+d)**2-4*(a*d-b*c)).sqrt()
    l1=(a+d+delta)/2;l2=(a+d-delta)/2
    for j in range(6):
        if kinds[j]=='strain':
            # Constant strain rate: shift by the stationary flowing solution.
            ss=2*em*v[j];ks=ss/(2*gk);u=s[j]-ss;w=k[j]-ks
            ud=a*u+b*w
            C1=(ud-l2*u)/(l1-l2);C2=u-C1
            exp1=(l1*h).exp();exp2=(l2*h).exp()
            sj=ss+C1*exp1+C2*exp2
            sd=C1*l1*exp1+C2*l2*exp2
            kj=ks+(sd-a*(sj-ss))/b
            ej=strain[j]+rate[j]*h
            pj=p+K*3*mean*h
        else:
            # Constant/ramped prescribed stress; Kelvin solution by convolution.
            r=gk/ev;z=(-r*h).exp()
            sj=s[j]+v[j]*h
            kj=k[j]*z+s[j]*(1-z)/(2*gk)+v[j]*(h-(1-z)/r)/(2*gk)
            ej=strain[j]+(sj-s[j])/(2*gm)+(kj-k[j])+(s[j]*h+v[j]*h*h/2)/(2*em)
            pj=p+mean*h
            if j<3:ej+=(pj-p)/(3*K)
        sn.append(sj+(pj if j<3 else 0));kn.append(kj);en.append(ej)
    return sn+kn,en

def reference(spec,precision=90):
    with localcontext() as ctx:
        ctx.prec=precision
        state=list(map(number,spec['initial']));strain=list(map(number,spec.get('initial_strain',[0]*6)))
        time=number(spec['start_time'])
        points=[dict(time=str(time),segment=-1,side='left',state=list(map(str,state)),strain=list(map(str,strain)))]
        for idx,seg in enumerate(spec['segments']):
            points.append(dict(time=str(time),segment=idx,side='right',state=list(map(str,state)),strain=list(map(str,strain))))
            kinds=[x['quantity'] for x in seg['controls']]
            # Mixed references use zero normal strain controls and shear stress controls;
            # these do not couple volume to controlled shear components.
            assert len(set(kinds[:3]))==1
            rate=[]
            for j,control in enumerate(seg['controls']):
                initial=(state if control['quantity']=='stress' else strain)[j]
                rate.append(D(0) if control['kind']=='hold' else number(control['value']) if control['kind']=='rate' else (number(control['value'])-initial)/number(seg['duration']))
            origin_state,origin_strain=state,strain
            for sample in range(1,seg['samples']+1):
                h=float(seg['duration'])*sample/seg['samples']
                state,strain=advance(origin_state,origin_strain,rate,h,spec['parameters'],kinds)
                points.append(dict(time=str(time+number(h)),segment=idx,side='left',state=list(map(str,state)),strain=list(map(str,strain))))
            time+=number(seg['duration'])
        return points

if __name__=='__main__':
    requests=json.loads((R/'requests.json').read_text())
    expected={}
    for case in requests['schedules']:
        if not case.get('expected_ok',True):continue
        lo=reference(case['spec'],90);hi=reference(case['spec'],160)
        for x,y in zip(lo,hi):
            for field in ['state','strain']:
                for a,b in zip(x[field],y[field]):
                    assert abs(D(a)-D(b))<D('1e-65')*max(D(1),abs(D(b)))
        expected[case['id']]=hi
    (R/'references.json').write_text(json.dumps(expected,indent=2)+'\n')
    print('Analytical references: 90/160-digit convergence passes for',len(expected),'schedules')
