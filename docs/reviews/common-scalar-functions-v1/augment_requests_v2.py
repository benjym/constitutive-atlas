from pathlib import Path
import json,struct,math,shutil,hashlib
p=Path(__file__).parent;v=p/'qualification-v2';assert not v.exists();v.mkdir()
for n in ['CMakeLists.txt','scalar_probe.cpp','collect_native.py','collect_wasm.mjs','make_references.py']:shutil.copy2(p/'qualification'/n,v/n)
a=json.loads((p/'qualification/requests.json').read_text());cases=a['cases']
def bits(x):return struct.pack('>d',x).hex()
def e(x):return dict(classification='nan' if math.isnan(x) else 'infinity' if math.isinf(x) else 'finite',signbit=None if math.isnan(x) else math.copysign(1.,x)<0,value=x if math.isfinite(x) else None)
extra=[('jet-finite-overflow-inactive',1e200,2.,0,math.inf,0.,0.),('jet-finite-overflow-active',1e200,2.,3,math.inf,2e200,math.inf),('jet-finite-underflow-inactive',1e-200,2.,0,0.,0.,0.),('jet-negative-zero-cube',-0.,3.,3,-0.,0.,math.nan),('jet-negative-zero-linear',-0.,1.,1,-0.,1.,0.),('jet-negative-zero-pole',-0.,-1.,1,-math.inf,-math.inf,0.)]
for id,x,y,seeds,z,dx,dy in extra:cases.append(dict(id=id,kind=2,a_bits=bits(x),b_bits=bits(y),seeds=seeds,expected=e(z),expected_derivatives=[e(dx),e(dy)]))
a['scope']+='; v2adds6explicitJetoverflow/underflow/signedzerocases, original385unchanged';(v/'requests.json').write_text(json.dumps(a,indent=2,allow_nan=False)+'\n')
s=(p/'qualification/assess.py').read_text().replace('==385','==391');(v/'assess.py').write_text(s)
fs=[Path(__file__),p/'qualification-design-freeze-v1.json',v/'requests.json']+[v/n for n in ['CMakeLists.txt','scalar_probe.cpp','collect_native.py','collect_wasm.mjs','make_references.py','assess.py']];(v/'reference-freeze.json').write_text(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in fs},'cases':len(cases),'unchanged_policies':'1ULP scalar/2e-300+2e-14Jet componentwise,100/160precision,signedzero/inactive/classifications; no compiledobservations'},indent=2)+'\n');print(len(cases),'v2cases;original385exactlyretained')
