"""Malformed-input API probes on exact snapshots; no accepted-value oracle."""
import importlib.util,json,sys,types
from pathlib import Path


def check():
 root=Path(__file__).parent/'reviewed-sources/atlas/numerics'
 package=types.ModuleType('_normalized_core_review');package.__path__=[str(root)]
 sys.modules[package.__name__]=package
 for name in ['determinant','normalized_determinant']:
  spec=importlib.util.spec_from_file_location(package.__name__+'.'+name,root/(name+'.py'))
  module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
 evaluate=sys.modules[package.__name__+'.normalized_determinant'].normalized_determinant
 cases={'length5':[1.]*5,'length7':[1.]*7,'bool':[True,1.,1.,0.,0.,0.],'complex':[1+0j,1.,1.,0.,0.,0.],'string':['1',1.,1.,0.,0.,0.],'none_component':[None,1.,1.,0.,0.,0.],'nan':[float('nan'),1.,1.,0.,0.,0.],'positive_infinity':[float('inf'),1.,1.,0.,0.,0.],'negative_infinity':[float('-inf'),1.,1.,0.,0.,0.],'overflowing_integer':[1<<2048,1.,1.,0.,0.,0.],'non_container':None,'generator':(x for x in range(6))}
 rows=[]
 for name,values in cases.items():
  try:evaluate(values)
  except (TypeError,ValueError) as e:rows.append({'case':name,'exception':type(e).__name__})
  else:raise AssertionError('invalid input accepted: '+name)
 return {'kind':'malformed-Python-input-rejection-only','cases':rows,'passed':len(rows),'failed':0,'limits':'Non-sized inputs reject with TypeError; malformed sized containers/components reject with ValueError. No uniform exception-class promise or accepted-value result is tested.'}

if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
