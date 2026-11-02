"""Freeze source-derived Perzyna schedule cases before compiled observations."""
import copy,json,math
from pathlib import Path
from oracle import P,Z,D,ZERO,dev,equivalent,stress,relaxation,creep,rotate_state,rotate,stress_space_history
from study import encode,SOLVER,MODEL
HERE=Path(__file__).resolve().parent
cases=[];convergence=[]
def add(name,z=Z,p=P,mode='relaxation',duration=.3,samples=2,rates=D,segments=None,settings=None):
 if segments is None:
  controls=[dict(quantity='stress' if mode=='creep' else 'strain',kind='rate' if mode=='rate' else 'hold',**({'value':v} if mode=='rate' else {})) for v in rates]
  segments=[dict(id=mode,duration=duration,samples=samples,controls=controls)]
 spec=dict(schema_version='0.2',units='SI',model=MODEL,parameters=list(p),initial=list(z),initial_strain=list(z[:6]),initial_strain_rate=list(rates if mode=='rate' else ZERO),start_time=0.,segments=copy.deepcopy(segments),solver={**SOLVER,**(settings or {})})
 refs=[dict(time=0.,state=list(z),stress=stress(z,p))];state=list(z);time=0.
 for seg in segments:
  for j in range(1,seg['samples']+1):
   dt=seg['duration']/seg['samples'];time+=dt
   if mode in ('relaxation','creep'):
    # Evaluate from each segment's exact incoming reference; semigroup checked independently.
    state=(relaxation if mode=='relaxation' else creep)(state,dt,p)
   else:
    rate=[c.get('value',0.) for c in seg['controls']]
    lo=stress_space_history(state,[(dt,rate)],p,8192)[0];hi=stress_space_history(state,[(dt,rate)],p,16384)[0]
    ds=max(abs(a-b) for a,b in zip(lo['state'],hi['state']));dq=max(abs(a-b) for a,b in zip(lo['stress'],hi['stress']))
    convergence.append(dict(case=name,time=time,state_error=ds,stress_error_Pa=dq));assert ds<5e-11 and dq<.005,(name,ds,dq)
    state=hi['state']
   refs.append(dict(time=time,state=list(state),stress=stress(state,p)))
 c=dict(id=name,ok=True,initial=list(z),specification=spec,references=refs);cases.append(encode(c));return c
# Six independent Mandel channels, both normals and shears, with regular/noninteger powers.
for channel in range(6):
 b=[0.]*6;b[channel]=1.;sd=dev(b);N=[x/equivalent(sd) for x in sd]
 for ratio in [0.,1.,2.]:
  for n in [1.,1.5,2.,3.]:
   p=P[:];p[4]=n;z=[ratio*p[2]/(2*p[1])*v for v in N]+[0.]*7
   add(f'hold-ch{channel}-q{ratio:g}-n{n:g}',z,p,duration=.2,samples=1)
for n in [1.,1.5,2.,3.]:
 p=P[:];p[4]=n
 add(f'creep-positive-n{n:g}',Z,p,mode='creep',duration=.3,samples=2)
 add(f'creep-negative-n{n:g}',[-v for v in Z[:12]]+[0.],p,mode='creep',duration=.3,samples=2)
add('public-relaxation',duration=2.,samples=4)
add('public-creep',mode='creep',duration=2.,samples=4)
add('public-rate',mode='rate',duration=2.,samples=4)
# Hydrostatic elastic rate and hold; all six simultaneous rates tested by the public example.
add('hydrostatic-rate',z=[.001]*3+[0.]*10,mode='rate',duration=.3,samples=2,rates=[.002]*3+[0.]*3)
for n in [1.,2.,3.]:
 p=P[:];p[4]=n
 segments=[]
 for i,(duration,rates) in enumerate([(.35,[-.025,.01,.015,-.005,.002,-.004]),(.25,[.01,-.02,.01,.006,-.004,.003]),(.2,ZERO)]):
  segments.append(dict(id=f'phase-{i}',duration=duration,samples=2,controls=[dict(quantity='strain',kind='rate',value=v) for v in rates]))
 add(f'noncoaxial-reversal-hold-n{n:g}',p=p,mode='rate',segments=segments)
for i,p in enumerate([[30e6,7e6,150e3,.001,1.5],[10e6,4e6,50e3,.0005,3.]]):add(f'custom-coefficients-{i}',p=p,duration=.4,samples=2)
vp=[.001,-.0004,-.0006,.0002,-.0001,.0003];memory=[a+b for a,b in zip(Z[:6],vp)]+vp+[.01]
add('nonzero-history-relaxation',z=memory,duration=.4)
add('nonzero-history-creep',z=memory,mode='creep',duration=.4)
R=[[0.,-1.,0.],[.8,0.,-.6],[.6,0.,.8]]
add('rotated-relaxation',z=rotate_state(Z,R),duration=.4)
add('rotated-rate',z=rotate_state(Z,R),mode='rate',rates=rotate(D,R),duration=.3)
add('refinement-coarse',duration=2.,samples=2,settings=dict(relative_tolerance=1e-4,absolute_scale_fraction=1e-7))
add('refinement-fine',duration=2.,samples=2)
parent=add('restart-parent',duration=.5,samples=1)
restart=add('restart-child',z=relaxation(Z,.5),duration=.5,samples=1);restart['restart_from']='restart-parent';restart['specification']['start_time']=.5
restart['references']=[{**r,'time':r['time']+.5} for r in restart['references']];encode(restart)
template=copy.deepcopy(cases[0])
def bad(name,change,parse=False):
 c=copy.deepcopy(template);c.update(id=name,ok=False,references=[]);change(c['specification']);c['initial']=c['specification']['initial'];
 if parse:c['parse_failure']=True
 cases.append(encode(c))
bad('zero-rate-coefficient',lambda s:s['parameters'].__setitem__(3,0.),True)
bad('negative-yield',lambda s:s['parameters'].__setitem__(2,-1.),True)
bad('singular-exponent-excluded',lambda s:s['parameters'].__setitem__(4,.5),True)
bad('missing-state',lambda s:s.update(initial=[]),True)
bad('negative-alpha',lambda s:s['initial'].__setitem__(12,-.001))
bad('volumetric-plastic-memory',lambda s:s['initial'].__setitem__(6,.001))
def inconsistent(s):s['initial'][6:9]=[.001,-.0005,-.0005]
bad('inconsistent-accumulation',inconsistent)
bad('negative-duration',lambda s:s['segments'][0].update(duration=-.1))
late=add('late-budget-rollback',duration=1.,samples=1,settings=dict(maximum_substeps=2))
late.update(ok=False,late=True)
late['specification']['segments']=[dict(id='committed-prefix',duration=1e-6,samples=1,controls=[dict(quantity='strain',kind='hold') for _ in range(6)]),dict(id='budget-exhaustion',duration=1.-1e-6,samples=1,controls=[dict(quantity='strain',kind='hold') for _ in range(6)])]
small=relaxation(Z,1e-6);late['references']=[dict(time=0.,state=Z,stress=stress(Z)),dict(time=1e-6,state=small,stress=stress(small))];encode(late)
add('post-invalid-recovery',duration=.3,samples=2)
(HERE/'cases.json').write_text(json.dumps({'identity':'perzyna-be-schedule-v1','cases':cases},indent=2)+'\n')
(HERE/'reference-convergence.json').write_text(json.dumps({'passed':True,'low_steps':8192,'high_steps':16384,'state_gate':5e-11,'stress_gate_Pa':.005,'comparisons':convergence},indent=2)+'\n')
print(json.dumps({'cases':len(cases),'rk4_reference_comparisons':len(convergence),'maximum_step':SOLVER['maximum_step'],'compiled_execution':False}))
