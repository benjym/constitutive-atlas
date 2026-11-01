"""Reproduce project-authored draft and analytical references, without solver execution."""
import copy,json,math,hashlib,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[4]; OUT=pathlib.Path(__file__).resolve().parent
base=json.loads((ROOT/'models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json').read_text())
m=copy.deepcopy(base);m.update(id='bingham-comsol63-mises-perfect-zero-spin-ode',name='COMSOL 6.3 Bingham — von Mises perfect viscoplastic dry zero-spin ODE',family='elastoviscoplasticity',description='Small-strain isotropic elastic associative von Mises Bingham law, constant positive yield stress, no isotropic or kinematic hardening and no thermal/pore effects. Compression-positive fixed-frame specialization. Project parameter examples and finite numerical envelope are not source calibration.',status='draft')
b='https://doc.comsol.com/6.3/doc/com.comsol.help.sme/'
m['sources']=[{'url':b+'sme_ug_theory.06.039.html','locator':'Viscoplasticity images057/059; Equivalent Stress images016/022; Bingham Model images076–078; Time Stepping Eq3-149/150','role':'primary vendor mathematical formulation'},{'url':b+'sme_ug_solid.07.024.html','locator':'Bingham; Plasticity Model; Perfectly plastic; No kinematic hardening; Thermal Effects None','role':'primary exact variant and viscosity unit'},{'url':b+'sme_ug_theory.06.029.html','locator':'Linear Viscoelasticity introduction: elastic strain subtraction; isotropic elastic stress images008–010','role':'primary isotropic elasticity and source sign convention'}]
m['parameters']={k:{'default':v,'min':lo,'max':hi,'unit':unit,'label':'Project illustrative '+k} for k,v,lo,hi,unit in [('K',2e7,1e-12,1e30,'Pa'),('G',1e7,1e-12,1e30,'Pa'),('sigma_y',1e5,1e-12,1e30,'Pa'),('eta',2e7,1e-12,1e30,{'si':[1,-1,-1,0]})]}
def state(n,shape,qty):return {'name':n,'shape':shape,'unit':'1','scale':'1','initial':[0]*6 if shape=='sym' else 0,'semantics':{'role':'persistent','quantity':qty,'transformation':'symmetric_spatial_tensor' if shape=='sym' else 'scalar_invariant'}}
m['state']=[state('eps','sym','infinitesimal_strain'),state('eps_vp','sym','viscoplastic_strain'),state('alpha','scalar','accumulated_equivalent_viscoplastic_strain')]
m['derived']=[{'name':'elastic_strain','expr':'eps - eps_vp'},{'name':'sdev','expr':'2 * G * dev(elastic_strain)'},{'name':'q','expr':'sqrt(1.5) * norm(sdev)'},{'name':'lambda_vp','expr':'max(q - sigma_y, 0 * sigma_y) / eta'}]
m['equations']={'eps':'strain_rate','eps_vp':'1.5 * lambda_vp / max(q, sigma_y) * sdev','alpha':'lambda_vp'}
m['domain']=['K > 0 * K','G > 0 * G','sigma_y > 0 * sigma_y','eta > 0 * eta','alpha >= 0','abs(trace(eps_vp)) <= 1e-10'];m['initial_checks']=['alpha >= 0','abs(trace(eps_vp)) <= 1e-10']
m['observables']=[{'name':'stress','shape':'sym','unit':'Pa','scale':'K','expr':'K * trace(elastic_strain) * I + sdev'}];m['initialization']['required_state']=['eps','eps_vp','alpha']
(OUT/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')
# Independent radial solution: s=z*N where N:N=2/3, so q=abs(z).
K,G,Y,eta=2e7,1e7,1e5,2e7

def radial(z,d,t):
 """Exact piecewise constant coaxial strain-rate history, includes yield crossings."""
 a=3*G/eta; remaining=t; alpha=0.; segments=[]
 while remaining>1e-14:
  sign=1 if z>Y else -1 if z < -Y else 0
  # At a yield boundary use outward flow segment; multiplier is zero at boundary.
  if sign==0 and ((z>=Y and d>0) or (z<=-Y and d<0)):sign=1 if d>0 else -1
  if sign==0:
   if d==0:dt=remaining;zn=z
   else:dt=min(remaining,max(0,((Y if d>0 else -Y)-z)/(2*G*d)));zn=z+2*G*d*dt
   da=0.
  else:
   ss=sign*Y+2*eta*d/3;dt=remaining
   if sign*d<0:
    ratio=(sign*Y-ss)/(z-ss)
    if 0<ratio<=1:dt=min(dt,-math.log(ratio)/a)
   zn=ss+(z-ss)*math.exp(-a*dt)
   da=sign*(2*G*d*dt-(zn-z))/(3*G)
  segments.append({'dt':dt,'z_start':z,'z_end':zn,'alpha_increment':da})
  alpha+=max(0,da);remaining-=dt;z=zn
  if dt==0:raise ValueError('zero progress')
 return z,alpha,segments
cases=[]
for channel in range(6):
 bvec=[0.]*6;bvec[channel]=1
 tr=sum(bvec[:3]);dv=[v-(tr/3 if i<3 else 0) for i,v in enumerate(bvec)];fac=math.sqrt(1.5*sum(v*v for v in dv));N=[v/fac for v in dv]
 for z0 in [0,.999*Y,Y,1.001*Y,2*Y,-2*Y]:
  for d in [0,.003,-.012]:
   t=2.;z,da,segs=radial(z0,d,t);e0=[z0/(2*G)*v for v in N];e=[e0[i]+d*t*N[i] for i in range(6)];evp=[e[i]-z/(2*G)*N[i] for i in range(6)]
   cases.append({'id':f'channel-{channel}-z{z0:g}-d{d:g}','parameters':{'K':K,'G':G,'sigma_y':Y,'eta':eta},'initial':e0+[0.]*6+[0.],'strain_rate':[d*v for v in N],'duration':t,'expected':e+evp+[da],'expected_stress':[z*v for v in N],'radial_segments':segs})
# Constant-stress creep references (loading supplied analytically, not alleged runtime stress API).
creep=[]
for ratio in [.5,1,1.5,-1.5]:
 z=ratio*Y;lam=max(abs(z)-Y,0)/eta;creep.append({'signed_equivalent_stress':z,'duration':3.,'equivalent_vp_increment':3*lam,'axial_vp_increment_for_N_xx_2_over_3':3*lam*(1 if z>=0 else -1),'description':'N=(2/3,-1/3,-1/3), eps_vp_dot=1.5 lambda sign(z) N'})
ref={'identity':'bingham-source-radial-analytic-v1','provenance':'Closed-form scalar reduction independently derived from transcribed source; no interpreter/native/Wasm observations','state_order':['eps[6]','eps_vp[6]','alpha'],'cases':cases,'constant_stress_creep':creep,'acceptance_proposal':{'stress_abs_floor_Pa':1,'strain_abs_floor':1e-8,'scaled_error_limit':2e-5,'definition':'max absolute component error divided by max(floor,abs(reference)); freeze execution settings separately before compiled observations','required_additional':'noncoaxial direction changes, rate steps, restart/trial/rollback, domain failures, refinement, Mandel shear, rotational covariance; no finite rotation claim'}}
(OUT/'analytical-references.json').write_text(json.dumps(ref,indent=2)+'\n')
# Algebraic identity checks, not integration/backend verification.
checks=0
for c in cases:
 e=c['expected'][:6];vp=c['expected'][6:12];s=c['expected_stress']; assert abs(sum(vp[:3]))<1e-12
 calc=[2*G*(e[i]-vp[i]) for i in range(6)]
 assert max(abs(a-b) for a,b in zip(calc,s))<1e-8
 assert c['expected'][-1]>=0
 checks+=3
(OUT/'analytical-check.json').write_text(json.dumps({'passed':True,'radial_cases':len(cases),'algebraic_checks':checks,'compiled_execution':False,'creep_reference_cases':len(creep)},indent=2)+'\n')
print(f'{len(cases)} radial cases; {checks} algebraic checks; {len(creep)} creep references')
