from pathlib import Path
import hashlib,json,struct
from fractions import Fraction
P=Path(__file__).parent;R=P/'initial/reference';D=Path('/Users/bmar5496/code/constitutive-atlas/docs/reviews/reproducible-cyclic-controls-v1')
checks=[]
def check(n,b):
 checks.append({'name':n,'passed':b})
 if not b:raise AssertionError(n)
for name,pin in json.loads((R/'source-pins.json').read_text()).items():check('source pin '+name,hashlib.sha256((R/name).read_bytes()).hexdigest()==pin==hashlib.sha256((D/name).read_bytes()).hexdigest())
ref=json.loads((R/'reference-p180.json').read_text());fixture=json.loads((R/'cyclic-bits.json').read_text());check('1080 phase cases',len(fixture)==len(ref['cases'])==1080)
count=0
for a,b in zip(fixture,ref['cases']):
 assert(a['steps'],a['cycles'],a['index'],a['wave_bits'])==(b['steps'],b['cycles'],b['index'],b['wave_bits'])
 for x,y in zip(a['controls'],b['controls']):
  assert x['target_bits']==struct.pack('>d',float.fromhex(y['amplitude'])).hex()and x['control_bits']==y['control_bits'];count+=1
check('9720 exact cyclic controls bound to oracle',count==9720)
ramps=json.loads((R/'monotonic-bits.json').read_text())
for c in ramps:
 t=struct.unpack('>d',bytes.fromhex(c['target_bits']))[0];i=c['index'];n=c['steps'];exact=Fraction.from_float(t)
 # Independent host conversion of exact rational rounded multiplication, then rounded division.
 value=0. if i==0 or t==0 else t if i==n else float(Fraction.from_float(float(exact*i))/n)
 assert struct.pack('>d',value).hex()==c['control_bits'],c
check('all monotonic fixture samples independently reconstructed',bool(ramps))
(P/'reference-binding-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'cyclic_control_count':count,'monotonic_samples':len(ramps),'production_producer_calls':0,'compiled_calls':0},indent=2)+'\n')
print(count,'cyclic controls and',len(ramps),'monotonic samples source-bound; no production calls')
