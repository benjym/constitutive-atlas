"""Known-endpoint source checks; this does not integrate or qualify a path."""
from pathlib import Path
import sys,json,hashlib,math
from fractions import Fraction as Q
sys.path.insert(0,str(Path(__file__).resolve().parents[6]))
from atlas.model import load,interpret,defaults
HERE=Path(__file__).resolve().parent
model=load(HERE/'model.json');policy=json.loads((HERE/'POLICY.json').read_text());records=[]
def residual_case(name,current,previous,de,parameters=None):
    r=interpret(model,current,previous,de,parameters)
    scale={'sigma':101325,'h':40,'wp':101325}
    norm=max(abs(v)/scale[n] for n,val in r.items() for v in (val.v if hasattr(val,'v') else [val]))
    records.append({'case':name,'max_scaled_residual':norm,'passed':norm<=policy['early_gates']['algebraic_endpoint_state_scaled_residual_tolerance']})
for label,overrides in [('dense',{}),('loose',{'k1':58,'ft':33,'A':.39,'rf':.970,'M':6.80e-4,'l':1.17,'Kur':1600,'n':.86})]:
    p={**defaults(model),**overrides};p0=100000;h=p['ft'];previous={'sigma':[p0,p0,p0,0,0,0],'h':h,'wp':0}
    residual_case(label+'_zero',previous,previous,[0]*6,p)
    p1=110000;E=p['Kur']*p['pa']*(p1/p['pa'])**p['n'];e=(p1-p0)/E
    current={'sigma':[p1,p1,p1,0,0,0],'h':h,'wp':0}
    residual_case(label+'_hydrostatic',current,previous,[e,e,e,0,0,0],p)
    old={'sigma':[200000,100000,100000,0,0,0],'h':h,'wp':0}
    current={'sigma':[400000,200000,200000,0,0,0],'h':h,'wp':0}
    E=p['Kur']*p['pa']*(200000/p['pa'])**p['n']
    residual_case(label+'_constant_f_proportional',current,old,[200000/E,100000/E,100000/E,0,0,0],p)
    # Triaxial endpoint: exact polynomial directional differentiation of g at fixed kappa2,
    # followed by source Eq15/19. No production derived values are used as reference.
    s=[Q(4),Q(1),Q(1),Q(0),Q(0),Q(0)];ref=100000
    def det(v):
        x,y,z,xy,yz,zx=v;return x*y*z+2*xy*yz*zx-x*yz**2-y*zx**2-z*xy**2
    f=sum(s[:3])**3/det(s);k2=Q(str(p['A']))*f+27*(1-Q(str(p['A'])))
    def g(v):return sum(v[:3])**3-k2*det(v)
    gradient=[]
    for i in range(6):
        def central(step):
            plus=s.copy();minus=s.copy();plus[i]+=step;minus[i]-=step
            return (g(plus)-g(minus))/(2*step)
        gradient.append((4*central(Q(1,2))-central(Q(1)))/3)
    a=p['M']*p['pa']*(ref/p['pa'])**p['l'];dw=a*(float(f)-h)/(1-p['rf']*(float(f)-h)/(p['k1']-h))**2
    dl=dw/(3*float(g(s))*ref**3)
    dep=[dl*float(v)*ref**2 for v in gradient[:3]]+[dl*float(v)*ref**2/math.sqrt(2) for v in gradient[3:]]
    E=p['Kur']*p['pa']*(ref/p['pa'])**p['n']
    target=[400000,100000,100000,0,0,0];de=[(x-y)/E+z for x,y,z in zip(target,previous['sigma'],dep)]
    current={'sigma':target,'h':float(f),'wp':dw};residual_case(label+'_plastic_source_endpoint',current,previous,de,p)
report={'model_sha256':hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((HERE/'POLICY.json').read_bytes()).hexdigest(),'scope':'Known-endpoint interpreter residuals only; no advance/solver/backend/path approval','cases':records,'passed':all(x['passed'] for x in records)}
(HERE/'interpreter-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
