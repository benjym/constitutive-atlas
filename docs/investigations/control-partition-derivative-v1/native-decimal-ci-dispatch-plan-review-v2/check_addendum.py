"""Read-only bindings and generic exact-bit serialization checks; no C++ calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util,struct,math
D=Path(__file__).resolve().parent;C=D.parent;A=C/'native-decimal-ci-dispatch-plan-v2';R=C/'native-decimal-reference-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
def rejects(n,fn):
 try:fn()
 except Exception:checks.append(n);return
 raise RuntimeError('Unexpected acceptance '+n)
ck('exact addendum manifest',sha(A/'manifest.json')=='e432935cf6dc0cb8830fa532be7b0a6b53306be02817583b2a37022adc5cb4c6')
for n,v in read(A/'manifest.json')['files'].items():ck('author file '+n,sha(A/n)==v)
for n,v in read(A/'bindings.json').items():ck('bound input '+n,sha(Path(n))==v)
sys.path.insert(0,str(R));spec=importlib.util.spec_from_file_location('bound_oracle_assessor',R/'assess_saved.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def strings(obj):
 if isinstance(obj,dict):
  for v in obj.values():yield from strings(v)
 elif isinstance(obj,list):
  for v in obj:yield from strings(v)
 elif isinstance(obj,str)and m.HEX.fullmatch(obj):yield obj
for i,v in enumerate(strings(read(R/'requests.json'))):
 mantissa,exponent=v.split('p');trim=mantissa.rstrip('0').rstrip('.')if '.'in mantissa else mantissa;trim=trim+'p'+exponent
 ck('trimmed metadata exact bits '+str(i),struct.pack('>d',m.hexfloat(v))==struct.pack('>d',m.hexfloat(trim)));m.same_metadata(trim,v)
for value in ['0x0p+0','-0x0p+0','0x1p+0','-0x1p+0','0x0.0000000000001p-1022','0x1.fffffffffffffp+1023']:
 ck('finite grammar '+value,math.isfinite(m.hexfloat(value)))
rejects('signed zero difference',lambda:m.same_metadata('-0x0p+0','0x0p+0'));rejects('wrong finite bits',lambda:m.same_metadata('0x1.0000000000001p+0','0x1p+0'))
for value in ['1.0','nan','inf','0X1P+0','0x1p+9999','0x1p0','0x1p+0 suffix']:
 rejects('malformed/nonfinite '+value,lambda v=value:m.hexfloat(v))
print(json.dumps({'identity':'independent-native-decimal-ci-serialization-addendum-review','decision':'ACCEPT_BIT_IDENTICAL_SERIALIZATION_ONLY','checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0},indent=2))
