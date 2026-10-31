"""Specified binary64 waveform oracle: exact Fraction arithmetic + integer RNE.
This is independent source/reference code, not a production C++ implementation.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import struct,json,sys,math,hashlib
PI2HEX='0x1.921fb54442d18p+0';PI2=F.from_float(float.fromhex(PI2HEX))
def quotient(n,d):
 q,r=divmod(n,d);return q+int(2*r>d or(2*r==d and q%2))
def bits(x):
 sign=int(x<0);x=abs(x)
 if not x:return 0
 n,d=x.numerator,x.denominator;e=n.bit_length()-d.bit_length()
 if(e>=0 and n<d<<e)or(e<0 and n<<(-e)<d):e-=1
 if e < -1022:q=quotient(n<<1074,d);return (sign<<63)|q
 shift=52-e;q=quotient(n<<shift,d)if shift>=0 else quotient(n,d<<(-shift))
 if q==1<<53:q>>=1;e+=1
 if e>1023:return(sign<<63)|(2047<<52)
 return(sign<<63)|((e+1023)<<52)|(q-(1<<52))
def decode(b):
 sign=-1 if b>>63 else 1;e=(b>>52)&2047;m=b&((1<<52)-1)
 if e==2047:raise ValueError('nonfinite')
 if e==0:return sign*F(m,1<<1074)
 q=F((1<<52)|m,1<<52);return sign*q*(1<< (e-1023))if e>=1023 else sign*q/F(1<<(1023-e))
def rn(x):return decode(bits(x))
def hex_(b):return struct.unpack('>d',struct.pack('>Q',b))[0].hex()
def phase(steps,cycles,i):
 assert 1<=steps<=5000 and 0<=cycles<=100 and 0<=i<=steps
 k=(cycles*i)%steps;q,rem=divmod(4*k,steps);j=rem if q%2==0 else steps-rem
 return k,q,j

def waveform(steps,cycles,i):
 k,q,j=phase(steps,cycles,i)
 if j==0:return F(0),{'phase':k,'quadrant':q,'reflected_numerator':j,'endpoint':'zero'}
 sign=-1 if q>=2 else 1
 if j==steps:return F(sign),{'phase':k,'quadrant':q,'reflected_numerator':j,'endpoint':'extremum'}
 ratio=rn(F(j,steps));x=rn(PI2*ratio);z=rn(x*x);term=total=x
 for n in range(1,12):
  term=rn(rn(-term*z)/F((2*n)*(2*n+1)));total=rn(total+term)
 return sign*total,{'phase':k,'quadrant':q,'reflected_numerator':j,'endpoint':None}
def atan_inv(n,precision):
 x=D(1)/n;xx=x*x;term=total=x;k=1;cut=D(10)**(-precision-8)
 while abs(term)>cut:term*=-xx;total+=term/(2*k+1);k+=1
 return total

def truepi(precision):return 16*atan_inv(5,precision)-4*atan_inv(239,precision)
def truesin(x,precision):
 term=total=x;k=1;cut=D(10)**(-precision-8);xx=x*x
 while abs(term)>cut:term*=-xx/D((2*k)*(2*k+1));total+=term;k+=1
 return total

def phases():
 cases=set()
 for n in range(1,33):
  for i in range(n+1):cases.add((n,1,i))
 for n in(63,64,65):
  for i in range(n+1):cases.add((n,1,i))
 for n in(127,128,129,4999,5000):
  for cyc in(1,2,3,7,100):
   for i in{0,1,n-1,n,n//4,max(0,n//4-1),min(n,n//4+1),n//2,max(0,n//2-1),min(n,n//2+1),3*n//4,max(0,3*n//4-1),min(n,3*n//4+1)}:cases.add((n,cyc,i))
 return sorted(cases)
AMPS=['0x0.0p+0','-0x0.0p+0','0x1.0000000000000p+0','-0x1.0000000000000p+0','0x1.47ae147ae147bp-7','0x1.86a0000000000p+17','0x1.7d78400000000p+26','0x0.0000000000001p-1022','0x1.0000000000000p-1022']
def generate(precision):
 out=[];maximum=D(0);maximumcontrol=D(0);violations=[];u=F(1,1<<53);sub=F(1,1<<1074)
 with localcontext()as ctx:
  ctx.prec=precision;pi=truepi(precision);pi2=pi/2
  for n,cyc,i in phases():
   wave,meta=waveform(n,cyc,i);k,q,j=meta['phase'],meta['quadrant'],meta['reflected_numerator'];angle=pi2*D(j)/n
   truth=D(0)if j==0 else D(1)if j==n else truesin(angle,precision)
   if q>=2:truth=-truth
   wf=D(wave.numerator)/D(wave.denominator);error=abs(wf-truth);maximum=max(maximum,error)
   if error>D(128)*D(u.numerator)/D(u.denominator):violations.append([n,cyc,i,'wave'])
   controls=[]
   for text in AMPS:
    amp=F.from_float(float.fromhex(text));raw=amp*wave;b=0 if amp==0 or wave==0 else bits(raw);represented=decode(b);value=D(represented.numerator)/D(represented.denominator);actual=D(amp.numerator)/D(amp.denominator)*truth;err=abs(value-actual);bound=D(130)*D(u.numerator)/D(u.denominator)*abs(D(amp.numerator)/D(amp.denominator))+D(sub.numerator)/D(sub.denominator);maximumcontrol=max(maximumcontrol,err)
    if err>bound:violations.append([n,cyc,i,text,'control'])
    controls.append({'amplitude':text,'control_hex':hex_(b),'control_bits':f'{b:016x}','mathematical_control':format(actual,'.80E')if actual else'0','absolute_error':str(err),'absolute_bound':str(bound)})
   if abs(wave)>1:violations.append([n,cyc,i,'range'])
   out.append({'steps':n,'cycles':cyc,'index':i,**meta,'wave_hex':hex_(bits(wave)),'wave_bits':f'{bits(wave):016x}','mathematical_wave':format(truth,'.80E')if truth else'0','absolute_wave_error':str(error),'controls':controls})
 return {'identity':'cyclic-sine-rne12-independent-reference-v1','precision':precision,'phase_cases':len(out),'amplitude_cases':len(AMPS),'controls':len(out)*len(AMPS),'maximum_absolute_wave_error':str(maximum),'maximum_absolute_control_error':str(maximumcontrol),'violations':violations,'cases':out,'candidate_calls':0,'compiled_calls':0}
if __name__=='__main__':
 r=generate(int(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in r.items()if k!='cases'}));raise SystemExit(0 if not r['violations']else 1)
