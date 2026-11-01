"""E2 structural/init contract checks; no material integration or compiled execution."""
from pathlib import Path
import sys,json,hashlib,copy
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.model import load,defaults
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
P=Path(__file__).parent
m=load(P/'model-contract.json');p=defaults(m)
valid={'sigma':[100000.,100000.,100000.,0.,0.,0.],'h':0.}
r=initialize_state(m,valid,p);assert len(r['initial'])==7
r=initialize_state(m,{'sigma':[150000.,100000.,100000.,0.,0.,0.],'h':75000.},p);assert r['initial'][-1]==75000.
rejects=[]
for name,state,params in [
 ('missing_sigma',{'h':0.},p),('missing_h',{'sigma':valid['sigma']},p),
 ('bad_shape',{'sigma':[1.,2.],'h':0.},p),('bad_history',{'sigma':[150000.,100000.,100000.,0.,0.,0.],'h':0.},p),
 ('zero_confinement',{'sigma':[100000.,100000.,0.,0.,0.,0.],'h':100000.},p),
 ('nan_state',{'sigma':[float('nan'),100000.,100000.,0.,0.,0.],'h':0.},p),
 ('bad_nu',valid,p|{'nu':.5}),('bad_Rf',valid,p|{'Rf':1.}),('bad_modulus',valid,p|{'E_failure':0.}),('nan_parameter',valid,p|{'n':float('nan')})]:
 before=copy.deepcopy(state)
 try:initialize_state(m,state,params)
 except (ValueError,ArithmeticError,ValidationError):rejects.append(name)
 else:raise AssertionError('invalid init accepted:'+name)
 # NaN identity is not used as an equality oracle.
 assert repr(state)==repr(before)
print(json.dumps({'pass':True,'valid_explicit_initializations':2,'expected_rejections':rejects,'persistent_components':7,'parameters':10,'material_updates':0,'compiled_calls':0,'model_contract_sha256':hashlib.sha256((P/'model-contract.json').read_bytes()).hexdigest()},indent=2))
