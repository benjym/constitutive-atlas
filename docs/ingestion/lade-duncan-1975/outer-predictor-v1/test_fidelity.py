from fidelity import parse_response,same_response
checks=[]
def test(a,b,equal):checks.append(same_response(parse_response(a),parse_response(b)) is equal)
test('{"x":-0}','{"x":0}',False)
test('{"x":-0.0}','{"x":0.0}',False)
test('{"x":1}','{"x":1.0}',False)
test('{"x":true}','{"x":1}',False)
test('{"x":"1"}','{"x":1}',False)
test('{"x":[1,-0,2.0],"ok":true}','{"x":[1,-0,2.0],"ok":true}',True)
test('{"x":1.0}','{"x":1e0}',True)
test('{"x":1,"elapsed_ms":1.0}','{"x":1,"elapsed_ms":2.0}',True)
test('{"x":{"elapsed_ms":1.0}}','{"x":{"elapsed_ms":2.0}}',False)
test('{"x":[1,2]}','{"x":[2,1]}',False)
test('{"x":9007199254740993}','{"x":9007199254740992}',False)
for token in ['NaN','Infinity','-Infinity','1e999']:
 try:parse_response('{"x":'+token+'}');checks.append(False)
 except ValueError:checks.append(True)
assert all(checks)
print({'checks':len(checks),'passed':all(checks)})
