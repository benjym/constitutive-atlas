"""Check the proposed explicit contract without rewriting any model record."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from atlas.model import migrate_formulation,validate
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError

def run():
 cross=json.loads((HERE/'crosswalk.json').read_text());path=ROOT/cross['research_definition'];raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==cross['research_definition_sha256']
 old=json.loads(raw);before=copy.deepcopy(old);model=migrate_formulation(old)
 for state,semantics in zip(model['state'],cross['state_contract']):
  assert state['name']==semantics['name'];state['semantics']=semantics['semantics']
 validate(model)
 assert old==before and path.read_bytes()==raw
 assert model['schema_version']=='0.3' and 'integration' not in model
 assert model['formulation']==cross['formulation'] and model['initialization']==cross['initialization']
 assert [{'name':s['name'],'shape':s['shape'],'unit':s['unit'],'semantics':s['semantics']} for s in model['state']]==cross['state_contract']
 unchanged=['parameters','derived','equations','domain','sources','id','status']
 for k in unchanged:assert old[k]==model[k],k
 assert [{k:v for k,v in s.items() if k!='semantics'} for s in model['state']]==old['state']
 params={k:v['default'] for k,v in model['parameters'].items()}
 state={s['name']:copy.deepcopy(s['initial']) for s in model['state']}
 immutable=copy.deepcopy((model,state,params));out=initialize_state(model,state,params)
 assert len(out['initial'])==14 and (model,state,params)==immutable
 canonical=hashlib.sha256(json.dumps(old,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 bindings={}
 for backend in ['native','wasm']:
  report=json.loads((ROOT/f'catalogue/investigations/gis2024-integration-v1/{backend}.json').read_text())
  assert report['model_sha256']==canonical and len(report['records'])==20
  bindings[backend]={'canonical_model_sha256':canonical,'trajectories':20,'identity_matches_current_legacy_definition':True,'qualifies_v03_copy':False}
 rejected=[]
 negatives={}
 for field in state:
  bad=copy.deepcopy(state);del bad[field];negatives['missing_'+field]=bad
 bad=copy.deepcopy(state);bad['Omega']=1.01;negatives['Omega_above_one']=bad
 bad=copy.deepcopy(state);bad['h']=[2*params['R'],0,0,0,0,0];negatives['memory_outside_radius']=bad
 bad=copy.deepcopy(state);bad['e']=-.1;negatives['negative_void_ratio']=bad
 for name,bad in negatives.items():
  snapshot=copy.deepcopy((bad,params,model))
  try:initialize_state(model,bad,params)
  except ValidationError:rejected.append(name)
  else:raise AssertionError(name+' accepted')
  assert (bad,params,model)==snapshot
 assert initialize_state(model,state,params)['initial']==out['initial']
 return {'kind':'gis2024-v03-contract-consistency','pass':True,'scalarized_persistent_state':14,'source_material_parameters':18,'numerical_parameters':['p_scale'],'unchanged_fields':unchanged+['state values/layout/scales'],'positive_initializations':2,'rejected_initializations':rejected,'historical_definition_bindings':bindings,'input_isolation':True,'definition_bytes_unchanged':True,'trajectory_calls':0,'compiled_calls':0,'scientific_admission':False,'scope':'In-memory contract/explicit initializer consistency only; not new source algebra, backend qualification or source preparation.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args();text=json.dumps(run(),indent=2)+'\n'
 if a.output:a.output.write_text(text)
 print(text,end='')
