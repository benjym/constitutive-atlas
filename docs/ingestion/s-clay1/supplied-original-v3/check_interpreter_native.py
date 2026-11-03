"""Interpreter/native residual parity on exact candidate; not independent law evidence."""
from pathlib import Path
import sys,json,subprocess,random,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];S=R/'.local/s-clay1-delivery-v3/source';sys.path.insert(0,str(S))
from atlas.model import load,interpret
m=load(O/'candidate/s-clay1.json');base={f['name']:f['initial'] for f in m['state']};rng=random.Random(20261103);worst=0;cases=[]
flat=lambda s:[float(x) for f in m['state'] for x in (s[f['name']] if f['shape']=='sym' else [s[f['name']]])]
csv=lambda v:','.join(format(float(x),'.17g') for x in v)
for i in range(50):
 s={**base,'sigma':[20000+rng.uniform(-2000,2000),12500+rng.uniform(-1000,1000),12500+rng.uniform(-1000,1000),rng.uniform(-1000,1000),rng.uniform(-1000,1000),rng.uniform(-1000,1000)],'gamma':rng.uniform(0,.001)}
 d=[rng.uniform(-.001,.001) for _ in range(6)];v=interpret(m,s,base,d);expected=[float(x) for f in m['state'] for x in (v[f['name']].v if f['shape']=='sym' else [v[f['name']]])]
 args=[str(R/'.local/s-clay1-delivery-v3/native/atlas_solver'),'--model','s-clay1','--mode','evaluate','--initial',csv(flat(base)),'--current',csv(flat(s)),'--strain',csv(d)]
 p=subprocess.run(args,capture_output=True,text=True,timeout=60);actual=json.loads(p.stdout)
 cases.append({'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'interpreter':expected})
 assert p.returncode==0 and actual['ok'];scales=[20000]*6+[1]*7+[20000,1]
 e=max(abs(a-b)/t for a,b,t in zip(expected,actual['values'],scales));assert e<1e-10;worst=max(worst,e)
(O/'native-interpreter-calls.json').write_text(json.dumps(cases,indent=2)+'\n')
print(json.dumps({'ok':True,'cases':50,'maximum_scaled_error':worst,'candidate_sha256':hashlib.sha256((O/'candidate/s-clay1.json').read_bytes()).hexdigest()},indent=2))
