"""Exercise existing Python initializer only, never compiled code."""
import json, math, sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]));sys.dont_write_bytecode=True
from atlas.model import load
from atlas.initialization import initialize_state
m=load(P.parents[2]/'models/research/nh2004/nakai-hinokio-2004-clay-appendix-v-be.json')
p={k:v['default'] for k,v in m['parameters'].items()}
rows=[]
for pressure,rho,e in [(98000,.03,.83),(196000,0,.83)]:
    x=initialize_state(m,{'sigma':[pressure]*3+[0.]*3,'rho':rho,'e':e,'smp':[1/math.sqrt(3)]*3+[0.]*3},p)
    rows.append(dict(pressure=pressure,rho=rho,e=e,accepted=True,initial=x['initial']))
rendered=json.dumps(rows,indent=2)+'\n'
assert (P/'initialization-probes.json').read_text()==rendered
print('PASS: both reference-inconsistent examples accepted by existing Python initializer; evidence exactly reproduced.')
