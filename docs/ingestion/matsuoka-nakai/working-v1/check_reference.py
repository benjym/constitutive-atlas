import json
import sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[3]))
from reference import terms,rate,initial,augmented_state,I
from atlas.model import load,interpret
m=load(P/'model.json')

def mapping(v):
    out={};k=0
    for f in m['state']:
        size=6 if f['shape']=='sym' else 1
        out[f['name']]=list(map(float,v[k:k+size])) if size==6 else float(v[k]);k+=size
    return out

rng=np.random.default_rng(4142024)
fixtures=[];seen=set()
for stress,rho in (([137200.,88200.,68600.,0.,0.,0.],.03),([294000.,49000.,49000.,0.,0.,0.],0.)):
 for _ in range(120):
    z=stress+[rho,.8];de=rng.normal(size=6)*1e-6
    dz,branch=rate(z,de,diagnostics=True)
    t=terms(stress,rho);ds=dz[:6]/98000
    dp=de-t['C']@ds
    coeff=np.linalg.lstsq(np.column_stack((t['m'],I/3)),dp,rcond=None)[0]
    current=augmented_state(z);current[-2:]=list(coeff)
    old=augmented_state(np.array(z)-dz)
    got=interpret(m,mapping(current),mapping(old),list(map(float,de)))
    flat=np.array([x for f in m['state'] for x in (got[f['name']].v if f['shape']=='sym' else [got[f['name']]])])
    flat[:6]/=98000
    err=float(max(abs(flat)))
    assert err<2e-8,(branch,err)
    if branch not in seen:fixtures.append(dict(branch=branch,parent=old,current=current,de=list(de),scaled_residual_error=err));seen.add(branch)
# rotated non-diagonal fixture from first regular source state
from reference import matrix,mandel
q=np.array([[.6,-.8,0],[.8,.6,0],[0,0,1.]])
f=fixtures[0];old=f['parent'].copy();cur=f['current'].copy()
for v in (old,cur):
 for offset in (0,8):v[offset:offset+6]=list(mandel(q@matrix(v[offset:offset+6])@q.T))
de=list(map(float,mandel(q@matrix(f['de'])@q.T)));r=interpret(m,mapping(cur),mapping(old),de)
assert max(abs(x) for x in r['smp'].v)<2e-12
fixtures.append(dict(branch='rotated-'+f['branch'],parent=old,current=cur,de=de))
assert {'elastic','AF','AF_IC','IC_only','softening'}<=seen,seen
target=P/'residual-fixtures.json'
rendered=json.dumps(fixtures,indent=2)+'\n'
if target.exists():assert target.read_text()==rendered,'Retained fixture differs; use a new study identity.'
else:target.write_text(rendered)
print('Independent residual branches:',sorted(seen),'and rotated fixture pass')
