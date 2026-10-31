"""Independent source-only manufacturing; no candidate imports or calls."""
import sys,json,math,hashlib
from pathlib import Path
from decimal import Decimal as D,localcontext
R=Path(sys.argv[1]);out=Path(sys.argv[2]);sys.path.insert(0,str(R));import generate as g
base=json.loads((R/'corpus/inputs.json').read_text());seeds=base['seeds'];found={}
with localcontext() as ctx:
 ctx.prec=280
 phi=D.from_float(.6);s,cf=g.sincos(phi);apex=cf/s;delta=D(2)**-46
 for shape in ((2,1,-3),(3,-1,-2)):
  for numerator in range(1,101):
   mean=apex-D(numerator)/20*delta
   vals=[mean+D(v)*delta for v in shape]
   c={'id':'pending','current':[0.0.hex()]*6,'parent':[0.0.hex()]*6,'loading':[float(-x/2).hex() for x in vals]+[0.0.hex()]*3,'parameters':{'E':2.0.hex(),'nu':0.0.hex(),'c':1.0.hex(),'phi':.6.hex(),'psi':.2.hex(),'p_ref':1.0.hex()},'tags':['supplemental','finite-selected-gap-rejection','source-only-manufactured'],'construction':{'delta':'2^-46','principal_shape':shape,'mean_below_apex_units_delta':str(D(numerator)/20)}}
   q=g.interface(c,seeds,280,False);branch=q['selected_branch']
   if branch in ('left','right') and branch not in found:
    c['id']='finite-unresolved/'+branch;found[branch]=c
   if len(found)==2:break
  if len(found)==2:break
 if len(found)!=2:raise AssertionError('did not construct both edge cases')
inputs={'identity':'mc-finite-unresolved-stored-input-v1','columns':38,'seeds':seeds,'cases':[found[k] for k in ('left','right')]}
out.mkdir(parents=True,exist_ok=True);(out/'inputs.json').write_text(json.dumps(inputs,indent=2,sort_keys=True)+'\n')
print(json.dumps({'cases':list(found),'input_sha256':hashlib.sha256((out/'inputs.json').read_bytes()).hexdigest(),'candidate_calls':0}))
