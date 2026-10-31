"""Source-only model checks, without material evaluation or generated-code execution."""
import argparse,ast,hashlib,json,sys,tempfile
from pathlib import Path
P=Path(__file__).parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc_type(t):return {'shape':t.shape,'dimensions':[str(x)for x in t.dim],'value_only':t.value_only}
def run(root):
 sys.path.insert(0,str(root))
 from atlas.structure import check
 from atlas.model import validate,field_type,equation_input_types
 from atlas.dsl import I,Type,parse,infer,cpp,evaluate,ValidationError
 from atlas.compiler import generate
 m=json.loads((P/'model.json').read_text());schema=json.loads((root/'schemas/model-v0.3.schema.json').read_text());check(m,schema)
 symbols={'I':Type('sym'),**equation_input_types(m)}
 symbols.update({n:field_type(f)for n,f in m['parameters'].items()})
 for f in m['state']:symbols[f['name']]=symbols[f['name']+'_n']=field_type(f)
 types={};emitted={}
 for f in m['derived']:
  types[f['name']]=infer(parse(f['expr']),symbols);symbols[f['name']]=types[f['name']];emitted[f['name']]=cpp(parse(f['expr']))
 for f in m['state']:
  types['equation_'+f['name']]=infer(parse(m['equations'][f['name']]),symbols);assert types['equation_'+f['name']]==field_type(f)
  emitted['equation_'+f['name']]=cpp(parse(m['equations'][f['name']]))
 for k in ['domain','initial_checks']:
  for e in m[k]:assert infer(parse(e),symbols)==Type('bool')
 assert types['returned']==Type('sym',types['trial'].dim)and not types['returned'].value_only
 assert m['formulation']['stress']['scope']=='total'and m['initialization']['required_state']==['sigma','ep']
 assert sum(6 if x['shape']=='sym'else 1 for x in m['state'])==12
 try:validate(m)
 except ValidationError as e:validator_failure=str(e)
 else:raise AssertionError('Expected retained total-stress binding gap is no longer present: re-review changed validator before proceeding')
 assert validator_failure=='incremental profile requires effective Cauchy stress state sigma'
 with tempfile.TemporaryDirectory(prefix='atlas-tresca-source-generation-')as td:
  try:generate(td,model_paths=[P/'model.json'])
  except ValidationError as e:generator_failure=str(e)
  else:raise AssertionError('Expected full generator to retain totalstress gap')
 assert generator_failure==validator_failure
 # Walk only the executed lazy arms with an ordinary supplied branch constant.
 # No tensors, eigenvalues or material outputs are evaluated by this traversal.
 def calls(node,b):
  if isinstance(node,ast.Call)and node.func.id=='select':return calls(node.args[1]if evaluate(node.args[0],{'branch':b})else node.args[2],b)
  found=[]
  if isinstance(node,ast.Call):found.append(node.func.id)
  for c in ast.iter_child_nodes(node):found+=calls(c,b)
  return found
 tree=parse(next(x['expr']for x in m['derived']if x['name']=='returned'));route={str(b):calls(tree,b)for b in range(4)}
 assert route['0']==[]
 assert route['1']==['projector_min']and route['2']==['projector_max']
 assert sorted(route['3'])==sorted(['principal_max','principal_min','projector_max','projector_min'])
 assert all('projector'not in x['expr']and 'principal_max('not in x['expr']and 'principal_min('not in x['expr']for x in m['derived']if x['name']!='returned')
 assert emitted['returned'].count('?')==3
 assert m['domain']==['p_ref>0*p_ref','lame_lambda>0*p_ref','mu>0*p_ref','k>0*p_ref']
 result={'version':'tresca-declarative-source-checks-v1','schema_structure':True,'dimensions_and_qualifiers':{n:enc_type(t)for n,t in types.items()},'state_components':12,'persistent_layout':['sigma','ep'],'total_scope_retained':True,'lazy_spectral_routes':route,'no_eager_restricted_projectors':True,'full_validator_expected_failure':validator_failure,'full_generator_expected_failure':generator_failure,'cpp_expression_emission':True,'material_evaluations':0,'compiled_calls':0,'source_ideal_fixtures_recomputed':False,'scientific_admission':False}
 return result,emitted
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--write',action='store_true');a=p.parse_args();r,e=run(a.root)
 if a.write:
  (P/'checks.json').write_text(json.dumps(r,indent=2)+'\n');(P/'expression-emission.json').write_text(json.dumps(e,indent=2)+'\n')
 else:
  assert r==json.loads((P/'checks.json').read_text());assert e==json.loads((P/'expression-emission.json').read_text());pins=json.loads((P/'source-pins.json').read_text())
  for n,h in pins['files'].items():assert sha(a.root/n)==h,n
  for n,h in json.loads((P/'manifest.json').read_text())['files'].items():assert sha(P/n)==h,n
 print('schema, dimensions, qualifiers, lazy branch structure and expected total-stress gate reproduced; no material/compiled execution')
