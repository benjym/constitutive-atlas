"""Typed initialization preflight only, with no constitutive integration."""
import copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from atlas.model import load
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
m=load(ROOT/'docs/reviews/gis2024-v03-research-freeze-v1/model.json')
def named(z):return {'sigma':z[:6],'e':z[6],'h':z[7:13],'Omega':z[13]}
rows=json.loads((HERE/'laboratory-cases.json').read_bytes())['cases'];states={r['id'].split('/')[0]:r['specification']for r in rows};valid=0;rejected=[]
for key,s in states.items():
 before=copy.deepcopy(s);assert initialize_state(m,named(s['initial']),dict(zip(m['parameters'],s['parameters'])))['initial']==s['initial'];assert s==before;valid+=1
for row in json.loads((HERE/'guard-cases.json').read_bytes()):
 if row['rejection_layer']!='engine_domain':continue
 s=row['specification'];before=copy.deepcopy(s)
 try:initialize_state(m,named(s['initial']),dict(zip(m['parameters'],s['parameters'])))
 except (ValidationError,ValueError,ArithmeticError):rejected.append(row['id'])
 else:raise AssertionError('invalid state accepted: '+row['id'])
 assert s==before
print(json.dumps({'distinct_valid_initializations':valid,'declared_domain_rejections':rejected,'initialization_mutation':False,'constitutive_integrations':0,'compiled_calls':0,'laboratory_qualification':False},indent=2))
