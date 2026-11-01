"""Analytical fixtures for generic controlled path interpreter; no material oracle."""
import sys,json,math,copy,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=Path('/private/tmp/atlas-norsand-path-v1');sys.path.insert(0,str(STAGE))
from atlas.path import Context,Settings,initialize,advance,evaluate_stage,stage_inputs
from atlas.model import validate
from atlas.dsl import ValidationError
checks=[]
def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
def reject(name,call):
 try:call()
 except (ValueError,ValidationError,ArithmeticError,TypeError):checks.append(name);return
 raise AssertionError('accepted '+name)
m=json.loads((STAGE/'candidate.json').read_text());m['id']='synthetic-controlled-path';m['formulation']['kinematics']='small_strain_3d'
m['formulation']['inputs']['equation']={'path_coordinate':m['formulation']['inputs']['equation']['path_coordinate']}
for n,key,order in [('u','load',0),('du','load',1),('unused','unused',0)]:m['formulation']['inputs']['equation'][n]={'quantity':'control','shape':'scalar','unit':'1','sampling':'stage','constraint':'finite','binding':{'control':key,'derivative_order':order}}
m['parameters']={'pref':dict(unit='Pa',default=1000,min=1,max=100000)}
m['state']=[dict(name='vscalar',shape='scalar',unit='1',scale='1',initial=1,semantics=dict(role='persistent',quantity='synthetic_scalar',transformation='scalar_invariant')),dict(name='A',shape='sym',unit='Pa',scale='pref',initial=[0]*6,semantics=dict(role='persistent',quantity='synthetic_tensor',transformation='fixed_components'))]
m['initialization']['required_state']=['vscalar','A'];m['derived']=[];m['equations']={'vscalar':'u+du','A':'pref*(u+du)*I'};m['domain']=['vscalar < 100'];m['observables']=[dict(name='stress',shape='sym',unit='Pa',scale='pref',expr='A')]
validate(m);check('load/type validation',True)
state=dict(vscalar=1.,A=[0.]*6);controls=dict(load=2.,unused=3.);params=dict(pref=1000.)
p=initialize(m,state,7.,controls,params);before=copy.deepcopy(p)
q=advance(m,p,.25,controls,dict(load=4.,unused=3.))
check('linear control value and derivative analytic scalar',abs(q.state['vscalar']-3.75)<1e-12)
check('tensor analytic',all(abs(a-b)<1e-9 for a,b in zip(q.state['A'],[2750.]*3+[0.]*3)))
check('nonzero path origin retained',q.coordinate==7.25)
check('parent immutable',p==before)
r=initialize(m,q.state,q.coordinate,q.controls,q.parameters);z=advance(m,r,0,q.controls,q.controls)
check('zero identity',z==q)
reject('retained controls start mismatch',lambda:advance(m,q,.01,controls,q.controls))
for progress in [-1,float('nan'),float('inf')]:reject('invalid progress '+str(progress),lambda:advance(m,p,progress,controls,controls))
reject('zero changed control',lambda:advance(m,p,0,controls,dict(load=3.,unused=3.)))
reject('missing unused control',lambda:advance(m,p,.1,controls,dict(load=2.)))
reject('extra control',lambda:advance(m,p,.1,controls,dict(**controls,extra=1.)))
reject('nonfinite unused control',lambda:advance(m,p,.1,controls,dict(load=2.,unused=float('nan'))))
reject('nonfinite state',lambda:initialize(m,dict(vscalar=float('inf'),A=[0]*6),0,controls,params))
reject('wrong tensor shape',lambda:initialize(m,dict(vscalar=1.,A=[0]*5),0,controls,params))
reject('missing state',lambda:initialize(m,dict(vscalar=1.),0,controls,params))
reject('extra parameter',lambda:initialize(m,state,0,controls,dict(pref=1000.,extra=0)))
reject('parameter bound',lambda:initialize(m,state,0,controls,dict(pref=-1)))
reject('invalid settings',lambda:advance(m,p,.1,controls,controls,Settings(relative=0)))
reject('unrepresentable endpoint',lambda:advance(m,Context(state,1e30,controls,params),1,controls,controls))
# This failure follows accepted early subintervals; the parent must remain exact.
reject('whole-parent rollback after internal progress',lambda:advance(m,p,60,controls,controls))
check('rollback exact parent',p==before)
check('recovery after rejection',advance(m,p,.25,controls,dict(load=4.,unused=3.))==q)
# Curved ODE forces error-based refinement, as opposed to max-step subdivision only.
curved=copy.deepcopy(m);curved['equations']['vscalar']='vscalar';curved['equations']['A']='A';cp=initialize(curved,state,0,controls,params);cq=advance(curved,cp,.5,controls,controls)
check('nonlinear refinement analytic exp',abs(cq.state['vscalar']-math.exp(.5))<2e-7)
reject('forced trial exhaustion',lambda:advance(curved,cp,.5,controls,controls,Settings(max_trials=1)))
invalid=copy.deepcopy(m);invalid['parameters']['u']=dict(unit='1',default=1,min=0,max=2)
reject('input/parameter name collision',lambda:validate(invalid))
invalid=copy.deepcopy(m);invalid['formulation']['inputs']['equation']['du']['unit']='Pa'
reject('control derivative unit mismatch',lambda:validate(invalid))
invalid=copy.deepcopy(m);invalid['formulation']['inputs']['equation']['du']['binding']['derivative_order']=0
reject('duplicate control binding',lambda:validate(invalid))
print(json.dumps(dict(pass_count=len(checks),checks=checks),indent=2))
(HERE/'generic-interpreter-results-v3.json').write_text(json.dumps(dict(pass_count=len(checks),checks=checks,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
(HERE/'synthetic-model-v3.json').write_text(json.dumps(m,indent=2)+'\n')
