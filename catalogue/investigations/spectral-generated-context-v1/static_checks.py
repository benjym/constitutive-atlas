"""Complete validator fixtures; source-only, before compiled observations."""
from pathlib import Path
import json,sys,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'frozen'))
from atlas.model import load,validate
from atlas.dsl import ValidationError
from atlas.history import validate_program
from atlas.initialization import validate_recipe

def run():
 records=[]
 def check(label,validator,value,allowed,marker=''):
  try:validator(value)
  except ValidationError as exc:
   if allowed or (marker and marker not in str(exc)):raise AssertionError((label,str(exc)))from exc
   records.append({'case':label,'accepted':False,'diagnostic':str(exc)})
  else:
   if not allowed:raise AssertionError('incorrectly accepted '+label)
   records.append({'case':label,'accepted':True})
 model=load(P/'models/max-observable.json')
 for alias in (False,True):
  for mode in ('direct','cancel','unselected'):
   m=copy.deepcopy(model);expr='principal_max_value(sigma)'
   if alias:m['derived']=[{'name':'query','expr':expr},{'name':'copied','expr':'query+p_ref'}];expr='copied'
   if mode=='cancel':expr='0*'+expr
   elif mode=='unselected':expr='select(1>0,0*p_ref,'+expr+')'
   m['equations']['q']=expr+'/tau';check('equation '+str(alias)+' '+mode,validate,m,False,'equation shape or dimensions mismatch')
   m=copy.deepcopy(model)
   if alias:m['derived']=[{'name':'query','expr':'principal_max_value(sigma)'}];expr='query'
   else:expr='principal_max_value(sigma)'
   if mode=='cancel':expr='0*'+expr
   elif mode=='unselected':expr='select(1>0,0*p_ref,'+expr+')'
   m['observables'][0]['expr']=expr;check('observable '+str(alias)+' '+mode,validate,m,False,'observable shape or dimensions mismatch')
 for target in ('state','observable'):
  for mode in ('direct','cancel','unselected','predicate'):
   m=copy.deepcopy(model);query='principal_max_value(sym(p_ref,2*p_ref,3*p_ref,0*p_ref,0*p_ref,0*p_ref))'
   expr={'direct':query,'cancel':'p_ref+0*'+query,'unselected':'select(1>0,p_ref,'+query+')','predicate':'select('+query+'>0*p_ref,p_ref,2*p_ref)'}[mode]
   (m['state'][0]if target=='state'else m['observables'][0])['scale']=expr
   check(target+' scale '+mode,validate,m,mode=='predicate','scale')
 reset=load(P/'models/reset.json')
 for mode in ('direct-value','aliased-value','unselected-value','consumed-guard','aliased-guard','ordinary-guard'):
  m=copy.deepcopy(reset);u=m['increment_reset']['updates'][0]
  if mode=='direct-value':u['value']='principal_max_value(sigma)*I'
  elif mode=='aliased-value':m['derived']=[{'name':'query','expr':'principal_max_value(sigma)'}];u['value']='query*I'
  elif mode=='unselected-value':u['value']='select(1>0,sigma,principal_max_value(sigma)*I)'
  elif mode=='consumed-guard':u['guard']='select(principal_max_value(sigma)>0*p_ref,1,-1)'
  elif mode=='aliased-guard':m['derived']=[{'name':'query','expr':'principal_max_value(sigma)'},{'name':'decision','expr':'select(query>0*p_ref,1,-1)'}];u['guard']='decision'
  else:u['guard']='principal_max(sigma)'
  check('reset '+mode,validate,m,mode=='ordinary-guard','increment reset')
 timed=load(P/'frozen/models/research/terracotta-2024-fig1.json');recipe=json.loads((P/'frozen/initialization/terracotta-2024-fig1-total-stress.json').read_text())
 for mode in ('term','state','rate','predicate'):
  item=copy.deepcopy(recipe)
  if mode=='term':item['terms'][0]['expr']='principal_max_value(pInput*I)'
  elif mode=='state':item['state']['ev_e']='principal_max_value(phiInput*I)'
  elif mode=='rate':item['initial_strain_rate']='principal_max_value(DvInput*I)*I'
  else:item['terms'][0]['requires']=['principal_max_value(pInput*I)>0*pInput']
  check('initialization '+mode,lambda x:validate_recipe(x,timed),item,mode=='predicate','initial strain rate' if mode=='rate' else 'initialization')
 history=json.loads((P/'history.json').read_text())
 for mode in ('write','cancel-write','unselected-write','signed-guard','predicate-write','output-check'):
  h=copy.deepcopy(history);phase=h['phases'][1]
  if mode=='write':phase['writes']['tensor']='principal_max_value(A)*I'
  elif mode=='cancel-write':phase['writes']['tensor']='0*principal_max_value(A)*I'
  elif mode=='unselected-write':phase['writes']['tensor']='select(1>0,I,principal_max_value(A)*I)'
  elif mode=='signed-guard':phase['guard']='select(principal_max_value(A)>0,1,-1)'
  elif mode=='predicate-write':phase['writes']['tensor']='select(principal_max_value(A)>0,I,I)'
  else:phase['checks']=['principal_max_value(tensor)>=0']
  check('history '+mode,validate_program,h,mode in('predicate-write','output-check'),'history')
 return {'checks':len(records),'accepted':sum(x['accepted']for x in records),'rejected':sum(not x['accepted']for x in records),'records':records,'compiled_observations':0}
if __name__=='__main__':
 report=run();print(json.dumps(report,indent=2))
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
