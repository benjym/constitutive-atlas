"""Check an analytical initial-state example; no stress-path/material integration."""
import argparse,copy,hashlib,json,math
from pathlib import Path
from decimal import Decimal,localcontext
from atlas.model import load
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 policy=json.loads((HERE/'policy.json').read_text());example=json.loads((HERE/'example.json').read_text())
 assert sha(HERE/'example.json')==policy['example_sha256']
 model_path=ROOT/example['model']['path'];assert sha(model_path)==policy['model_sha256']==example['model']['sha256']
 model=load(model_path);params=example['parameters'];state=example['state'];original=copy.deepcopy(state)
 assert math.isclose(params['phi_c'],math.radians(22.6),rel_tol=0,abs_tol=1e-15)
 assert {k:params[k] for k in ('N','lambda_star','kappa_star','sigma_star')}=={'N':1.375,'lambda_star':.11,'kappa_star':.016,'sigma_star':1000}
 with localcontext() as ctx:
  ctx.prec=70;v=(Decimal('1.375')-Decimal('.11')*(Decimal('100000')/Decimal('1000')).ln()).exp();e=v-1
 assert str(v)==example['analytical_reference']['specific_volume_decimal70'] and str(e)==example['analytical_reference']['void_ratio_decimal70']
 assert abs(state['e']-float(e))<=policy['gates']['expected_scalar_absolute_error']
 inverse=math.log1p(state['e'])+params['lambda_star']*math.log(example['inputs']['p0_pa']/params['sigma_star'])
 assert abs(inverse-params['N'])<=policy['gates']['NCL_inverse_absolute_error']
 accepted=initialize_state(model,state,params)
 assert state==original and accepted['named_state']==state and accepted['initial']==state['sigma']+[state['e']]
 rejected=[]
 for name,bad in [('missing e',{'sigma':state['sigma']}),('nonpositive isotropic stress',dict(state,sigma=[0.,0.,0.,0.,0.,0.])),('e=-1',dict(state,e=-1.))]:
  before=copy.deepcopy(bad)
  try:initialize_state(model,bad,params)
  except ValidationError:rejected.append(name)
  else:raise AssertionError('invalid initial state accepted: '+name)
  assert bad==before
 assert rejected==policy['expected_rejections'] and sha(model_path)==policy['model_sha256']
 result={'id':example['id'],'pass':True,'model_sha256':sha(model_path),'example_sha256':sha(HERE/'example.json'),'specific_volume':float(v),'void_ratio':state['e'],'inverse_N':inverse,'complete_state_preserved':True,'rejected_invalid_states':rejected,'model_defaults_unchanged':True,'native_calls':0,'wasm_calls':0,'material_updates':0,'experimental_validation':False,'preparation_history_inferred':False}
 args.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS: analytical NCL state, explicit initialization and three immutable rejections; no material updates')
if __name__=='__main__':main()
