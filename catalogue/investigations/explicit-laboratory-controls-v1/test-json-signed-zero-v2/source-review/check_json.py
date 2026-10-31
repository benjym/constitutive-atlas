"""Pure JSON/binary64 sanity checks: no solver imports or subprocess calls."""
import json, struct
from pathlib import Path
bits=lambda x:struct.pack('>d',x).hex()
cases={
 '-0':'8000000000000000', '0':'0000000000000000',
 '-0.0':'8000000000000000', '0.0':'0000000000000000',
 '5e-324':'0000000000000001', '-5e-324':'8000000000000001',
 '100000':'40f86a0000000000', '9007199254740992':'4340000000000000',
 '1.7976931348623157e308':'7fefffffffffffff',
}
rows=[]
for token,expected in cases.items():
 value=json.loads(token,parse_int=float)
 assert type(value) is float and bits(value)==expected
 rows.append({'token':token,'expected_bits':expected,'actual_bits':bits(value)})
assert bits(json.loads('-0'))=='0000000000000000'
assert bits(json.loads('-0',parse_int=float))=='8000000000000000'
# Callbacks change numeric tokens only; strings, booleans, null and arrays persist.
x=json.loads('{"ok":true,"none":null,"bits":"8000000000000000","count":2,"values":[-0,0,5e-324]}',parse_int=float)
assert x['ok'] is True and x['none'] is None and type(x['bits']) is str
assert x['count']==2 and [bits(v) for v in x['values']]==['8000000000000000','0000000000000000','0000000000000001']
report={'identity':'explicit-controls-json-source-review-v2','scope':'pure JSON only, no solver execution','passed':True,'numeric_cases':rows,'original_default_negative_zero_bits':bits(json.loads('-0')),'corrected_negative_zero_bits':bits(json.loads('-0',parse_int=float)),'non_numeric_types_preserved':True}
Path(__file__).with_name('json-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'numeric_cases':len(rows),'additional_assertions':4}))
