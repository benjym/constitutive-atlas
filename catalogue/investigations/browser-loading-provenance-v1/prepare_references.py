from pathlib import Path
import json,struct,hashlib,importlib.util
from fractions import Fraction as F
s=Path(__file__).parent;r=Path('/Users/bmar5496/code/constitutive-atlas');original=r/'docs/reviews/reproducible-cyclic-controls-v1'
(s/'reference').mkdir(exist_ok=True)
for name in ['reference.py','policy.json','reference-p180.json','prospective-source-freeze.json','proof-results.json']:
 (s/'reference'/name).write_bytes((original/name).read_bytes())
spec=importlib.util.spec_from_file_location('oracle',original/'reference.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
data=json.loads((original/'reference-p180.json').read_text())
cases=[]
for c in data['cases']:
 cases.append({'steps':c['steps'],'cycles':c['cycles'],'index':c['index'],'wave_bits':c['wave_bits'],'controls':[{'target_bits':struct.pack('>d',float.fromhex(a['amplitude'])).hex(),'control_bits':a['control_bits']}for a in c['controls']]})
(s/'reference/cyclic-bits.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
monotonic=[]
for n in [1,2,3,7,16,63,64,65,4999,5000]:
 for i in sorted({0,1,n//4,n//2,n-1,n}):
  for text in oracle.AMPS:
   target=float.fromhex(text)
   if abs(target)>.1:continue
   exact=F.from_float(target)
   bits=0 if not exact or i==0 else int.from_bytes(struct.pack('>d',target),'big')if i==n else oracle.bits(oracle.rn(exact*i)/n)
   monotonic.append({'steps':n,'index':i,'target_bits':struct.pack('>d',target).hex(),'control_bits':f'{bits:016x}'})
(s/'reference/monotonic-bits.json').write_text(json.dumps(monotonic,separators=(',',':'))+'\n')
(s/'reference/source-pins.json').write_text(json.dumps({name:hashlib.sha256((original/name).read_bytes()).hexdigest()for name in ['reference.py','policy.json','reference-p180.json','prospective-source-freeze.json','proof-results.json']},indent=2)+'\n')
print('source-only fixtures',len(cases),'phase cases',len(monotonic),'ramp samples; no production calls')
