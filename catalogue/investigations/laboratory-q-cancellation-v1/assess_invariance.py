from pathlib import Path
from dataclasses import dataclass
import json,sys,struct
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent
@dataclass(frozen=True)
class Number:
 kind:str
 bits:str
def loads(text):
 def number(kind,text):return Number(kind,struct.pack('>d',float(text)).hex())
 def invalid(text):raise ValueError('Nonfinite JSON constant '+text)
 return json.loads(text,parse_int=lambda text:number('integer',text),parse_float=lambda text:number('real',text),parse_constant=invalid)
newpath=Path(sys.argv[1]);old=loads((s/'baseline/backend-results.json').read_text());new=loads(newpath.read_text())
assert old['status']=='failed'and new['status']=='passed'
assert len(old['pairs'])==len(new['pairs'])==101
# Exclusions belong only to the response clock and the per-point q observable.
def unchanged(value):
 value=dict(value);value.pop('elapsed_ms',None)
 if 'points'in value:
  value['points']=[{k:v for k,v in point.items()if k!='q'}for point in value['points']]
 return value
points=0
for a,b in zip(old['pairs'],new['pairs']):
 assert a['name']==b['name']and a['specification']==b['specification']
 for role in ['native','wasm']:
  assert unchanged(a[role])==unchanged(b[role]),(a['name'],role)
  points+=len(a[role]['points'])
# Structured journal JSON canonicalizes -0. Compare all original raw C API strings
# using tagged numeric kinds and exact binary64 bits to retain signs and bool types.
a=loads((s/'baseline/backend-results.json.raw.json').read_text());b=loads(Path(str(newpath)+'.raw.json').read_text())
assert len(a)==len(b)==382
for i,(x,y)in enumerate(zip(a,b)):
 assert x['role']==y['role']and x['name']==y['name']and x['args']==y['args'],i
 assert unchanged(loads(x['raw']))==unchanged(loads(y['raw'])),('raw',i)
print(json.dumps({'passed':True,'paired_cases':101,'backend_points':points,'raw_calls':382,'allowed_differences':['point.q','response.elapsed_ms'],'all_other_numeric_kinds_and_bits_exact':True,'candidate_calls':0},indent=2))
