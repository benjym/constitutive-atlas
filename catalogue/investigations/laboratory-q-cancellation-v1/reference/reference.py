"""Independent exact stored-value q reference, no Atlas or candidate imports."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import struct,math,json,hashlib
P=Path(__file__).parent
ALPHA=F(32,1<<53);BETA=F(8,1<<1074)
def decode(b):return struct.unpack('>d',bytes.fromhex(b))[0]
def bits(x):return struct.pack('>d',x).hex()
def square(v):
 a,b,c,u,v,w=v
 return ((a-b)**2+(b-c)**2+(c-a)**2+3*(u*u+v*v+w*w))/2
def sqrt_decimal(x,precision):
 with localcontext()as ctx:
  ctx.prec=precision;return (D(x.numerator)/D(x.denominator)).sqrt()
def certify_rounding(x,q):
 if not x:return bits(q)=='0000000000000000'
 qf=F.from_float(q);lo=F.from_float(math.nextafter(q,0.));hi=F.from_float(math.nextafter(q,math.inf));lower=(lo+qf)/2;upper=(qf+hi)/2
 even=int(bits(q),16)%2==0
 return (x>lower*lower or even and x==lower*lower)and(x<upper*upper or even and x==upper*upper)
def passes_exact_accuracy(q,qsq):
 if not math.isfinite(q)or q<0:return False
 if not qsq:return bits(q)=='0000000000000000'
 value=F.from_float(q);low=max(F(0),(value-BETA)/(1+ALPHA));high=(value+BETA)/(1-ALPHA)
 return low*low<=qsq<=high*high
if __name__=='__main__':
 frozen=json.loads((P/'prospective-freeze.json').read_text())
 for name,pin in frozen['files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==pin,name
 output=[];diagnosis=[]
 for case in json.loads((P/'inputs.json').read_text())['cases']:
  v=[F.from_float(decode(b))for b in case['input_bits']];qsq=square(v);q800=sqrt_decimal(qsq,800);q1200=sqrt_decimal(qsq,1200);rounded=float(q1200)
  assert bits(float(q800))==bits(rounded)and certify_rounding(qsq,rounded)and passes_exact_accuracy(rounded,qsq)
  output.append({'id':case['id'],'input_bits':case['input_bits'],'q_squared_numerator':str(qsq.numerator),'q_squared_denominator':str(qsq.denominator),'q_decimal_800':str(q800),'q_decimal_1200':str(q1200),'q_rounded_bits':bits(rounded),'q_rounded_hex':rounded.hex(),'exact_isotropic_zero':qsq==0,'rounding_cell_certified':True,'reference_passes_frozen_accuracy':True})
  if case['id'].startswith('isotropic-observed'):
   x=v[0];trace=F.from_float(float(3*x));mean=F.from_float(float(trace/3));residual=x-mean;legacy=sqrt_decimal(F(9,2)*residual*residual,1200)
   diagnosis.append({'id':case['id'],'stored_diagonal_hex':decode(case['input_bits'][0]).hex(),'correctly_rounded_trace_hex':float(trace).hex(),'rounded_mean_hex':float(mean).hex(),'exact_residual_numerator':str(residual.numerator),'exact_residual_denominator':str(residual.denominator),'old_deviator_q_from_rounding_hex':float(legacy).hex(),'old_deviator_q_from_rounding_decimal':str(float(legacy)),'exact_pairwise_q_bits':'0000000000000000'})
 (P/'references.json').write_text(json.dumps({'identity':'laboratory-q-exact-stored-value-reference-v1','cases':output,'production_calls':0},indent=2)+'\n')
 (P/'diagnosis.json').write_text(json.dumps({'identity':'laboratory-q-mean-rounding-source-diagnosis-v1','cases':diagnosis,'candidate_calls':0},indent=2)+'\n')
 print(len(output),'exact rational q² references, dual precision and exact rounding-cell certificates; no candidate calls')
