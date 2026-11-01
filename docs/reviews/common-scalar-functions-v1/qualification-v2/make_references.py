"""Independent Decimal powers/log and Machin/Taylor sine on exact binary64 inputs."""
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from pathlib import Path
import struct,json,math,hashlib
p=Path(__file__).parent;assert not (p/'references.json').exists()
def f(bits):return struct.unpack('>d',bytes.fromhex(bits))[0]
def atan_series(x):
 term=x;total=x;k=1
 while True:
  term*=-x*x;nxt=total+term/(2*k+1)
  if nxt==total:return total
  total=nxt;k+=1
_pi={}
def pi(prec):
 if prec not in _pi:
  with localcontext() as ctx:ctx.prec=prec+30;_pi[prec]=16*atan_series(Decimal(1)/5)-4*atan_series(Decimal(1)/239)
 return _pi[prec]
def sine(x,prec):
 with localcontext() as ctx:
  ctx.prec=prec+30;tau=2*pi(prec);y=x-(x/tau).to_integral_value(rounding=ROUND_HALF_EVEN)*tau;term=y;total=y;k=1
  while True:
   term*=-y*y/Decimal((2*k)*(2*k+1));nxt=total+term
   if nxt==total:break
   total=nxt;k+=1
  ctx.prec=prec;return +total
def enc(x):
 v=float(x);return dict(decimal=str(x),classification='infinity' if math.isinf(v) else 'finite',signbit=math.copysign(1.,v)<0,rounded_bits=struct.pack('>d',v).hex())
rows=[]
for c in json.loads((p/'requests.json').read_text())['cases']:
 if 'reference' not in c:rows.append(dict(id=c['id'],expected=c['expected'],**({'expected_derivatives':c['expected_derivatives']} if 'expected_derivatives' in c else {})));continue
 a=Decimal.from_float(f(c['a_bits']));b=Decimal.from_float(f(c['b_bits']));runs=[]
 for precision in [100,160]:
  with localcontext() as ctx:
   ctx.prec=precision
   if c['reference']=='sine':values=[sine(a,precision)]
   else:
    value=a**b;values=[value]
    if c['reference']=='jet':values.extend([b*(a**(b-1)),value*a.ln()])
   runs.append([enc(x) for x in values])
 assert [v['rounded_bits'] for v in runs[0]]==[v['rounded_bits'] for v in runs[1]],c['id']
 rows.append(dict(id=c['id'],references=runs[1],precision_converged=True))
(p/'references.json').write_text(json.dumps(dict(rows=rows,precisions=[100,160],scope='Independent exact-input Decimal+Machin/Taylor references. Converged binary64 roundings are evidence, not a proof of universal correct rounding. No compiled observations.'),indent=2)+'\n');print(len(rows),'reference rows; all computed roundings converge at100/160digits')
