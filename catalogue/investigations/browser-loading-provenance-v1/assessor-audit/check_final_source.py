from pathlib import Path
import ast,json
P=Path(__file__).parent;F=P/'final';checks=[]
def check(name,b):
 checks.append({'name':name,'passed':b})
 if not b:raise AssertionError(name)
for name in ['freeze.py','execute.py']:
 s=(F/name).read_text();node=ast.parse(s).body[0]
 try:exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec',optimize=2),{})
 except RuntimeError:check(name+' refuses optimized execution before any imports/actions',True)
 else:check(name+' refuses optimized execution',False)
b=(F/'check_backends.mjs').read_text();check('output preservation before compiled module import',b.index('Preserve existing observations')<b.index('const module=await'))
check('raw journal precedes helper validation',"function raw(role,name,args,output)"in b and "raw('wasm',name,args,module.ccall"in b and "raw('native',name,args,p.stdout);assert"in b)
check('same engine direct legacy API comparisons',"row.direct_native=JSON.parse(nativeEngine.ccall('atlas_run_with_settings'"in b and "row.direct_wasm=JSON.parse(wasm.ccall('atlas_run_with_settings'"in b and 'assert.deepEqual(physical(row.direct_native),physical(row.native))'in b and 'assert.deepEqual(physical(row.direct_wasm),physical(row.wasm))'in b)
check('same-instance replay equality','assert.deepEqual(physical(replay),physical(row.wasm))'in b)
check('limited committed prefix gate',"assert.equal(failed.native.ok,false);assert.equal(failed.native.points.length,1)"in b)
check('post failure hard rejection',"if p.returncode:raise RuntimeError"in(F/'execute.py').read_text())
t=(F/'test_loading.mjs').read_text();check('identity negative tests',all(x in t for x in ["delete r.catalogue_hash","r.catalogue_hash=''","delete r.schema_version","r.schema_version='future'"]))
check('zero sign and subnormal roundtrips',"[0,-0,Number.MIN_VALUE,-Number.MIN_VALUE,.002,-.002]"in t)
check('packaging copy includes new module',"'numerics.mjs','loading.mjs','recorded.mjs'"in(F/'tools/build_web.py').read_text())
(P/'final-source-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'production_producer_calls':0,'compiled_calls':0},indent=2)+'\n')
print(len(checks),'final source checks pass; no production execution')
