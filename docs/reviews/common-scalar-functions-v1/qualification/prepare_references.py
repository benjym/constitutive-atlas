from pathlib import Path
import json,struct,math,hashlib
p=Path(__file__).parent;assert not (p/'requests.json').exists()
def bits(x):return struct.pack('>d',float(x)).hex()
cases=[]
def add(id,kind,a,b=0,seeds=0,**kw):cases.append(dict(id=id,kind=kind,a_bits=bits(a),b_bits=bits(b),seeds=seeds,**kw))
for i,a in enumerate([2.**-1000,2.**-100,.1,.5,float.fromhex('0x1.f7a75cef7f3c8p-1'),math.nextafter(1.,0.),1.,math.nextafter(1.,2.),1.5,2.,10.,1e100]):
 for j,b in enumerate([-12.3,-3.,-2.,-.54,0.,.54,1.,2.,3.,12.3]):add(f'power-{i}-{j}',0,a,b,reference='power')
angles={0.,-0.,.6370451769779303,-1000.,1000.,-.1,.1}
for cycles in [1,2,8]:
 for i in range(65):angles.add(2*3.141592653589793*cycles*i/64)
for k in range(-8,9):
 x=k*math.pi/2;angles.update([x,math.nextafter(x,-math.inf),math.nextafter(x,math.inf)])
for i,a in enumerate(sorted(angles)):add(f'sine-{i}',1,a,reference='sine')
for i,a in enumerate([.0001,.1,.5,1.,2.,10.,10000.]):
 for j,b in enumerate([-2.5,-.54,0.,.54,1.,2.,4.]):add(f'jet-{i}-{j}',2,a,b,3,reference='jet')
# Classification/signedzero contracts explicitly frozen, independent of candidate.
special=[(-0.,3.,'finite',True,0.),(-0.,2.,'finite',False,0.),(-0.,-3.,'infinity',True,None),(0.,-2.,'infinity',False,None),(-2.,.5,'nan',None,None),(-2.,3.,'finite',True,-8.),(-2.,-3.,'finite',True,-.125),(math.nan,0.,'finite',False,1.),(1.,math.nan,'finite',False,1.),(math.nan,1.,'nan',None,None),(math.inf,1.,'infinity',False,None),(-math.inf,3.,'infinity',True,None),(-math.inf,.5,'infinity',False,None)]
for i,(a,b,c,sign,v) in enumerate(special):add(f'power-special-{i}',0,a,b,expected=dict(classification=c,signbit=sign,value=v))
for i,a in enumerate([-0.,math.inf,-math.inf,math.nan]):add(f'sine-special-{i}',1,a,expected=dict(classification='finite' if i==0 else 'nan',signbit=True if i==0 else None,value=0. if i==0 else None))
for i,(a,b,seeds,v,dx,dy) in enumerate([(-2.,2.,1,4.,-4.,0.),(-2.,3.,1,-8.,12.,0.),(-2.,2.,3,4.,-4.,math.nan),(0.,1.,3,0.,1.,math.nan),(0.,0.,3,1.,math.nan,-math.inf),(0.,-1.,0,math.inf,0.,0.),(-2.,.5,0,math.nan,0.,0.)]):
 def e(x):return dict(classification='nan' if math.isnan(x) else 'infinity' if math.isinf(x) else 'finite',signbit=None if math.isnan(x) else math.copysign(1.,x)<0,value=x if math.isfinite(x) else None)
 add(f'jet-special-{i}',2,a,b,seeds,expected=e(v),expected_derivatives=[e(dx),e(dy)])
(p/'requests.json').write_text(json.dumps(dict(cases=cases,scope='Bounded prospective scalar/Jet corpus; binary64 bits authoritative; no compiled observations'),indent=2,allow_nan=False)+'\n')
fs=[Path(__file__),p/'requests.json',p/'scalar_probe.cpp',p.parent/'REFERENCE_POLICY_V1.md',p.parent/'proposed-source-freeze-v2.json']
(p/'reference-freeze.json').write_text(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in fs},'cases':len(cases),'power_ulp_limit':1,'sine_ulp_limit':1,'jet_absolute_tolerance':2e-300,'jet_relative_tolerance':2e-14,'precision':[100,160]},indent=2)+'\n');print(len(cases),'exactbit scalar/Jet cases frozen')
