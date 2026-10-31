import sys,json,copy,shutil
from pathlib import Path
r=Path('/Users/bmar5496/code/constitutive-atlas');s=Path('/private/tmp/atlas-spectral-dsl-candidate-v1');sys.path.insert(0,str(s))
shutil.copytree(r/'initialization',s/'initialization',dirs_exist_ok=True)
from atlas.model import load,validate
from atlas.dsl import Type,PRESSURE,ValidationError
from atlas.initialization import validate_recipe
from atlas.history import _tree
checks=[]
def expect(label,action,allowed):
 try:action()
 except ValidationError:
  assert not allowed,label
 else:assert allowed,label
 checks.append(label)
m=load(r/'models/linear-elastic.json')
for e,allowed in [('select(principal_max_value(sigma)>p_ref,sigma,sigma)',True),('principal_max_value(sigma)*I',False),('select(1>0,sigma,principal_max_value(sigma)*I)',False)]:
 n=copy.deepcopy(m);n['equations']['sigma']=e;expect('model equation '+e,lambda:validate(n),allowed)
for field in ('domain','initial_checks'):
 n=copy.deepcopy(m);n[field]=['principal_max_value(sigma)>0*p_ref'];expect(field+' predicate',lambda:validate(n),True)
for e,allowed in [('principal_max_value(sigma)',False),('select(principal_max_value(sigma)>0*p_ref,p_ref,-p_ref)',False),('principal_max(sigma)',True),('trace(sigma)',True)]:
 n=copy.deepcopy(m);n['increment_reset']={'scope':'parent_increment','updates':[{'target':'sigma','guard':e,'value':'sigma'}]};expect('reset guard '+e,lambda:validate(n),allowed)
n=copy.deepcopy(m);n['derived'] += [{'name':'query','expr':'principal_max_value(sigma)'},{'name':'decision','expr':'select(query>0*p_ref,p_ref,-p_ref)'}];n['increment_reset']={'scope':'parent_increment','updates':[{'target':'sigma','guard':'decision','value':'sigma'}]};expect('reset guard indirect predicate alias',lambda:validate(n),False)
# Numerical history guards/writes reject value-only returns; Boolean checks accept predicates.
sy={'A':Type('sym',PRESSURE),'p':Type(dim=PRESSURE)}
for e,t,allowed in [('principal_max_value(A)',Type(dim=PRESSURE),False),('principal_max_value(A)>p',Type('bool'),True),('select(principal_max_value(A)>p,p,-p)',Type(dim=PRESSURE),True),('select(1>0,p,principal_max_value(A))',Type(dim=PRESSURE),False)]:expect('history '+e,lambda:_tree(e,sy,t),allowed)
# Initialization is a numerical sink even though it performs no AD itself.
m=load(r/'models/research/terracotta-2024-fig1.json');recipe=json.loads((r/'initialization/terracotta-2024-fig1-total-stress.json').read_text());validate_recipe(recipe,m)
for target in ('term','state','rate'):
 q=copy.deepcopy(recipe)
 if target=='term':
  term=q['terms'][0];term['expr']='principal_max_value(pInput*I)'
 elif target=='state':q['state']['ev_e']='principal_max_value(phiInput*I)'
 else:q['initial_strain_rate']='principal_max_value(DvInput*I)*I'
 expect('initialization '+target+' rejects value-only',lambda:validate_recipe(q,m),False)
q=copy.deepcopy(recipe);q['terms'][0]['requires']=['principal_max_value(pInput*I)>0*pInput'];expect('initialization predicate accepted',lambda:validate_recipe(q,m),True)
from atlas.history import validate_program
program=json.loads((r/'fixtures/history/ordered-copy.json').read_text())
phase=program['phases'][0];phase['bindings']['tensor']={'snapshot':'parent','field':'stress'}
for e,allowed in [('select(principal_max_value(tensor)>0*trace(tensor),1,-1)',False),('select(principal_max(tensor)>0*trace(tensor),1,-1)',True)]:
 q=copy.deepcopy(program);q['phases'][0]['guard']=e
 expect('history signed event guard '+e,lambda:validate_program(q),allowed)
p=Path('/private/tmp/atlas-spectral-source-check-results-v1/consumer-checks.json');p.write_text(json.dumps({'checks':checks,'count':len(checks),'compiled_observations':0},indent=2)+'\n');print('Passed',len(checks),'source consumer checks')
