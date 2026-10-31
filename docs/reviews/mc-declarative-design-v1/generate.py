from pathlib import Path
import json,sys,copy
R=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent/'frozen';P=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path(__file__).resolve().parent;P.mkdir(exist_ok=True);sys.path.insert(0,str(R))
from atlas.model import migrate_formulation,load,validate
from atlas.compiler import generate
m=migrate_formulation(load(R/'models/linear-elastic.json'))
m.update(id='mohr-coulomb-sysala-cermak-h0-research',name='Mohr–Coulomb H=0 — Sysala–Cermak v3 research',family='elastoplasticity',status='transcribed',description='Source-pinned constant-cohesion nonassociated backward-Euler return. Strict positive friction/dilation; no cutoff/cap/hardening. Compression-positive small-strain fixed-frame research record, not a public runnable model or scientific admission.')
m['state']=m['state'][:1];m['state'][0]['initial']=[0.,0.,0.,0.,0.,0.];m['initialization']['required_state']=['sigma']
m['parameters']={
'p_ref':{'default':100000.,'min':1.,'max':1e12,'unit':'Pa','label':'Numerical reference stress'},
'E':{'default':30000000.,'min':0.,'max':1.7976931348623157e308,'unit':'Pa','label':'Young modulus'},
'nu':{'default':.25,'min':-1.,'max':.5,'unit':'1','label':'Poisson ratio (strict interior)'},
'c':{'default':10000.,'min':0.,'max':1.7976931348623157e308,'unit':'Pa','label':'Constant cohesion'},
'phi':{'default':0.5235987755982988,'min':0.,'max':1.5707963267948966,'unit':'1','label':'Friction angle in radians (strict interior)'},
'psi':{'default':0.17453292519943295,'min':0.,'max':1.5707963267948966,'unit':'1','label':'Dilation angle in radians (strict interior)'}}
def d(name,expr):m['derived'].append({'name':name,'expr':expr})
m['derived']=[]
for name,expr in [('K','E/(3*(1-2*nu))'),('G','E/(2*(1+nu))'),('sf','sin(phi)'),('sd','sin(psi)'),('cf','cos(phi)'),('h','2*c*cf'),('aa','2*(K-2*G/3)*sd'),('ds','4*K*sd*sf+4*G*(1+sd*sf/3)'),('dl','4*K*sd*sf+G*(3-sf-sd+sd*sf/3)'),('dr','4*K*sd*sf+G*(3+sf+sd+sd*sf/3)'),('da','4*K*sd*sf'),('trial','-(sigma_n+K*trace(de)*I+2*G*dev(de))'),('v1','principal_max_value(trial)'),('v2','principal_mid_value(trial)'),('v3','principal_min_value(trial)'),('ftrial','(1+sf)*v1-(1-sf)*v3-h'),('gsl','(v1-v2)/(2*G*(1+sd))'),('gsr','(v2-v3)/(2*G*(1-sd))'),('gla','(v1+v2-2*v3)/(2*G*(3-sd))'),('gra','(2*v1-v2-v3)/(2*G*(3+sd))'),('class_ga','((2/3)*sf*(v1+v2+v3)-h)/da'),('class_gs','ftrial/ds'),('branch','select(ftrial<=0*p_ref,0,select(class_ga>=max(gla,gra),4,select(class_gs<min(gsl,gsr),1,select(gsl<gsr,2,3))))')]:d(name,expr)
def guard(code,expr,zero):return f'select(branch<{code+.5},select(branch>{code-.5},{expr},{zero}),{zero})'
mx='principal_max(trial)';mn='principal_min(trial)';hi='principal_upper_sum(trial)';lo='principal_lower_sum(trial)'
d('face_gamma',guard(1,f'((1+sf)*{mx}-(1-sf)*{mn}-h)/ds','0'))
d('left_gamma',guard(2,f'((1+sf)*{hi}/2-(1-sf)*{mn}-h)/dl','0'))
d('right_gamma',guard(3,f'((1+sf)*{mx}-(1-sf)*{lo}/2-h)/dr','0'))
r1=f'({mx}-face_gamma*(aa+2*G*(1+sd)))';r2='(principal_mid(trial)-face_gamma*aa)';r3=f'({mn}-face_gamma*(aa-2*G*(1-sd)))'
face=f'{r2}*I+({r1}-{r2})*projector_max(trial)+({r3}-{r2})*projector_min(trial)'
rl=f'({hi}/2-left_gamma*(aa+G*(1+sd)))';r3l=f'({mn}-left_gamma*(aa-2*G*(1-sd)))'
left=f'{rl}*I+({r3l}-{rl})*projector_min(trial)'
rr=f'({lo}/2-right_gamma*(aa-G*(1-sd)))';r1r=f'({mx}-right_gamma*(aa+2*G*(1+sd)))'
right=f'{rr}*I+({r1r}-{rr})*projector_max(trial)'
ret=f'select(branch<0.5,trial,select(branch<1.5,{face},select(branch<2.5,{left},select(branch<3.5,{right},c*cf/sf*I))))'
d('returned_source',ret)
m['equations']={'sigma':'sigma+returned_source'}
m['domain']=['E>0*p_ref','c>0*p_ref','nu>-1','nu<0.5','phi>0','phi<1.5707963267948966','psi>0','psi<1.5707963267948966','K>0*p_ref','G>0*p_ref','ds>0*p_ref','dl>0*p_ref','dr>0*p_ref','da>0*p_ref','sf>0','sf<1','sd>0','sd<1','face_gamma>=0','left_gamma>=0','right_gamma>=0','(1+sf)*principal_max_value(returned_source)-(1-sf)*principal_min_value(returned_source)-h<=5.684341886080802e-14*max(h,max(abs(principal_max_value(returned_source)),abs(principal_min_value(returned_source))))']
m['initial_checks']=['(1-sf)*principal_max_value(sigma)-(1+sf)*principal_min_value(sigma)-h<=5.684341886080802e-14*max(h,max(abs(principal_max_value(sigma)),abs(principal_min_value(sigma))))']
m['sources']=[{'url':'https://arxiv.org/abs/1508.07435v3','locator':'Sysala and Cermak; exact preprint SHA256 bf35ee09d500b8e21aabdddbdfac363c5f68368f150890c60343bc62447c83ca; pp7–13 Eqs3.1–3.6,4.8–4.29 H=0 specialization; grouped return/tangents pp14–16. Atlas compression signs reversed; effective stress is explicit host specialization.','role':'primary formulation and backward-Euler algorithm'}]
validate(m);(P/'model.json').write_text(json.dumps(m,indent=2)+'\n')
generate(P/'generated',[P/'model.json'])
print(json.dumps({'validated':True,'schema_version':'0.3','state_components':6,'derived':len(m['derived']),'compiled_observations':0}))
