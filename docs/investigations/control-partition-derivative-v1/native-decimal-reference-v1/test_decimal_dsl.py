"""Independent analytic/synthetic checks; no MD law or Atlas imports."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from decimal import Decimal
from pathlib import Path
import json,subprocess,sys,os
from decimal_dsl import Sym,Rejected,context,expression,binary,evaluate_model
D=Path(__file__).resolve().parent;passed=[]
def eq(label,a,b):
 if a!=b:raise AssertionError((label,a,b))
 passed.append(label)
def reject(label,fn):
 try:fn()
 except(Rejected,ValueError,ArithmeticError,TypeError):passed.append(label)
 else:raise AssertionError('accepted '+label)
for prec in [80,120]:
 with context(prec):
  q=Decimal;e={'x':q(2),'y':q(3)}
  for text,wanted in [('3',3),('x+y',5),('x-y',-1),('x*y',6),('1/8',q('.125')),('sqrt(4)',2),('log(1)',0),('4**0.5',2),('(-2)**3',-8),('abs(-2)',2),('min(x,y)',2),('max(x,y)',3),('select(x>0, x, log(-1))',2)]:eq(str(prec)+text,expression(text,e),q(wanted))
  # Independent exact central secant of cubic: f'(x)+h^2, x=2, h=.01.
  h=q('.01');a=expression('x**3',{'x':q(2)+h});b=expression('x**3',{'x':q(2)-h});eq('cubic secant'+str(prec),(a-b)/(2*h),q('12.0001'))
  for poly,wanted in [('7*x-2',q(7)),('x*x',q(4)),('8',q(0))]:eq(poly+str(prec),(expression(poly,{'x':q(2)+h})-expression(poly,{'x':q(2)-h}))/(2*h),wanted)
  v=Sym(tuple(map(q,['2','-1','3','4','5','6'])));env={'v':v,'I':Sym(tuple(map(q,[1,1,1,0,0,0])))}
  eq('trace'+str(prec),expression('trace(v)',env),q(4));eq('dot'+str(prec),expression('dot(v,v)',env),q(91));eq('norm'+str(prec),expression('norm(v)',env),q(91).sqrt());eq('dev trace'+str(prec),abs(expression('trace(dev(v))',env))<q('1e-70'),True)
  eq('mixed'+str(prec),expression('2*v-v',env),v)
  # Separate invariant polynomial versus evaluator's Cartesian matrix contraction.
  x,y,z,u,vv,w=v.v;want=x**3+y**3+z**3+q('1.5')*((x+y)*u*u+(y+z)*vv*vv+(x+z)*w*w)+3/q(2).sqrt()*u*vv*w
  err=abs(expression('cube_trace(v)',env)-want);eq('nonaxis cubic'+str(prec),err<q('1e-70'),True)
  eq('binary literal'+str(prec),expression('0.1',{}),q.from_float(.1))
  for text in ['x.foo','x[0]','__import__(1)','sqrt(x,y)','sqrt(x=1)','x<y<3','True','[1,2]','lambda:1','sqrt(-1)','log(0)','1/0','(-2)**0.5','select(1,2,3)','(x>0)+1','missing','dot(x,x)','trace(x)','norm(x)','v+1','v*v','select(x>0,x,v)','select(x>0,x,missing)','select(x>0,x,1e999)']:
   reject(str(prec)+text,lambda t=text:expression(t,{**e,**env}))
  reject('nonfinite'+str(prec),lambda:binary(float('inf')));reject('tensor shape'+str(prec),lambda:Sym((q(1),)));reject('booleaninput'+str(prec),lambda:binary(True))
  model={'schema_version':'0.3','formulation':{'equation_form':'incremental_residual','time_dependence':'strain_path','kinematics':'small_strain_3d','tensor_representation':'mandel'},'parameters':{'k':{'min':0,'max':2}},'state':[{'name':'x','shape':'scalar'}],'derived':[{'name':'v','expr':'k*x'}],'domain':['x>0'],'equations':{'x':'v-x_n'}}
  call=lambda m=model,s={'x':q(2)},p={'k':q(2)}:evaluate_model(m,s,{'x':q(1)},[q(0)]*6,p)
  eq('generic model'+str(prec),call()[0],[q(3)]);reject('domain'+str(prec),lambda:call(s={'x':q(-1)}));reject('bound'+str(prec),lambda:call(p={'k':q(3)}));reject('missingparam'+str(prec),lambda:call(p={}))
  bad={**model,'history':[{}]};reject('history'+str(prec),lambda:call(m=bad));bad2={**model,'derived':[{'name':'x','expr':'1'}]};reject('duplicate'+str(prec),lambda:call(m=bad2))
# Optimizer safety checks only this source, never native artifacts.
cp=subprocess.run([sys.executable,'-O',str(D/'decimal_dsl.py')],capture_output=True,text=True,env={**os.environ,'PYTHONOPTIMIZE':'0'});eq('optimized reject',cp.returncode!=0 and 'Unoptimized'in cp.stderr,True)
(D/'synthetic-results.json').write_text(json.dumps(dict(passed=True,checks=len(passed),labels=passed,precisions=[80,120],no_atlas_imports=True,compiled_calls=0),indent=2)+'\n');print(len(passed),'synthetic checks passed')
