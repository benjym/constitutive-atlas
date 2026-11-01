"""Source/interpreter and exact-wire preflight for the finalized candidate."""
from pathlib import Path
import json,sys,struct,hashlib
B=Path(__file__).resolve().parent;R=B.parents[4];sys.path.insert(0,str(R));sys.path.insert(0,str(B.parent))
from atlas.model import load,interpret
from reference import quantities,residual
from decimal import localcontext
m=load(B/'candidate.json');req=json.loads((B/'requests.json').read_text());old=json.loads((B.parent/'candidate.json').read_text());new=json.loads((B/'candidate.json').read_text())
assert {k for k in new if new[k]!=old[k]}=={'name','description'}
assert hashlib.sha256((B/'candidate.json').read_bytes()).hexdigest()==req['candidate_sha256']
def bitify(x):
 if isinstance(x,float):return struct.pack('>d',x).hex()
 if isinstance(x,list):return [bitify(v) for v in x]
 if isinstance(x,dict):return {k:bitify(v) for k,v in x.items()}
 return x
assert bitify(req)==json.loads((B/'requests-binary64.json').read_text())
results=[]
for c in req['cases']:
 z=c['target'];n=c['initial'];p=c['parameters'];de=c['de']
 r=interpret(m,{'sigma':z[:6],'h':z[6]},{'sigma':n[:6],'h':n[6]},de,p);values=list(r['sigma'].v)+[r['h']];error=max(map(abs,values))/p['p_ref'];assert error<=2e-10,(c['id'],error)
 with localcontext() as ctx:
  ctx.prec=100;ref=list(map(float,residual(z,n,de,p)));branch=quantities(z,n,p)[2]
 assert branch==c['branch'];assert max(abs(a-b) for a,b in zip(values,ref))/p['p_ref']<=2e-10
 results.append(dict(id=c['id'],normalized_residual=error,branch=branch))
out=dict(identity='duncan-final-candidate-interpreter-v1',candidate_sha256=req['candidate_sha256'],wire_manifest_verified=True,scientific_fields_equal_e2=True,cases=results,pass_=True,compiled_calls=0)
(B/'input-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS:72 source/interpreter endpoints, exact wires and candidate identity')
