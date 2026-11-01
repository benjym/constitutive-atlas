"""Independent synthetic expressions only. Does not run author test/generator mains."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json
from decimal import Decimal as Q
D=Path(__file__).resolve().parent;A=D.parent/'native-decimal-reference-v1';spec=importlib.util.spec_from_file_location('reviewed_decimal',A/'decimal_dsl.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
def reject(n,fn):
 try:fn()
 except(m.Rejected,ValueError,ArithmeticError,TypeError):checks.append(n);return
 raise RuntimeError('Unexpected acceptance '+n)
for prec in [80,120]:
 with m.context(prec):
  # Non-axisymmetric integer Cartesian matrix has exact integer cubic trace.
  r=Q(2).sqrt();v=m.Sym((Q(1),Q(3),Q(-2),r*2,r*4,r*(-3)));env={'v':v}
  M=[[1,2,-3],[2,3,4],[-3,4,-2]];expected=sum(M[i][j]*M[j][k]*M[k][i]for i in range(3)for j in range(3)for k in range(3))
  ck('matrix cubic '+str(prec),abs(m.expression('cube_trace(v)',env)-expected)<Q('1e-70'))
  ck('deviator trace '+str(prec),abs(m.expression('trace(dev(v))',env))<Q('1e-70'))
  ck('dot matrix '+str(prec),abs(m.expression('dot(v,v)',env)-sum(x*x for row in M for x in row))<Q('1e-70'))
  for text,want in [('x*x*x+2*x*x-7*x+11',Q(20)),('x*x+2*x',Q(8)),('3',Q(0))]:
   # derivative at3:27+12-7=32, plus cubic h²; second is8.
   h=Q(1)/8;want=Q(32)+h*h if text.startswith('x*x*x')else want
   sec=(m.expression(text,{'x':Q(3)+h})-m.expression(text,{'x':Q(3)-h}))/(2*h);ck(text+str(prec),sec==want)
  ck('binary decimal literal '+str(prec),m.expression('0.2',{})==Q.from_float(.2))
  ck('lazy negative false branch '+str(prec),m.expression('select(1<0,1/0,7)',{})==7)
  for text in ['(1>0)*2','select(0,2,3)','(-3)**0.25','min(v,1)','dot(v,1)','v/0','sqrt(1,2)','v.__class__','[0]*6','1==1','1e999','False','1 if 1 else 2','norm(2)','pow(2,3)']:
   reject(text+str(prec),lambda t=text:m.expression(t,env))
print(json.dumps({'identity':'independent-generic-decimal-synthetic-probes','checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0},indent=2))
