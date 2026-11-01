"""Exact function extraction and synthetic metadata mocks; never executes runner."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json,tempfile,types,re
D=Path(__file__).resolve().parent;C=D.parent;A=C/'current-profile-actual-power-v3';P=C/'current-profile-execution-v3'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):
 if not v:raise RuntimeError(n)
 checks.append(n)
def reject(n,fn):
 try:fn()
 except (RuntimeError,FileExistsError,FileNotFoundError):checks.append(n);return
 raise RuntimeError('Unexpected acceptance '+n)
ck('exact runner',h(A/'run-v5.py')=='118b9d4c331537b0e47aefcf5ae9f5d16fa77627affa7e3d6c64e85bc2b22268');ck('exact freeze',h(A/'freeze-v5.json')=='cf2c8540edbb029b649ead0b02aaee78d4f432dddc5724c98b203cbec916a449')
f=read(A/'freeze-v5.json');ck('all frozen inputs exact',all(h(Path(n))==v for n,v in f['inputs'].items()))
p=next(x for x in read(P/'plan.json')['profiles']if x['profile']=='power-creep');E=Path(p['output']);tree=ast.parse((A/'run-v5.py').read_text());v4=ast.parse((A/'run-v4.py').read_text());fn=lambda t,n:next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name==n)
import copy
prior_verify=copy.deepcopy(fn(tree,'verify'));del prior_verify.body[2].body[3:6]
ck('verify additive cache/compiler checks only',ast.dump(prior_verify)==ast.dump(fn(v4,'verify')));ck('capture unchanged from acceptedv4',ast.dump(fn(tree,'capture'))==ast.dump(fn(v4,'capture')))
loop=next(x for x in tree.body if isinstance(x,ast.For)and ast.unparse(x.iter)=="profile['steps'][5:]");old=next(x for x in v4.body if isinstance(x,ast.For)and ast.unparse(x.iter)=="profile['steps'][1:]");ck('only remaining3 exact loop bodies',ast.dump(ast.Module(body=loop.body,type_ignores=[]))==ast.dump(ast.Module(body=old.body,type_ignores=[]))and [x['stage']for x in p['steps'][5:]]==['wasm-build','wasm-collect','wasm-assess'])
for st in p['steps'][:5]:
 n=st['stage'];pre=read(E/'stage-receipts'/(n+'.pre.json'));post=read(E/'stage-receipts'/(n+'.post.json'));r=read(E/'processes'/n/'process.json');ck('saved '+n,pre['passed']is True and post['passed']is True and post['exit_status']==0 and r['returncode']==0 and r['argv']==st['argv'])
 for raw in ['stdout','stderr']:ck('saved raw '+n+raw,h(E/'processes'/n/raw)==r[raw+'_sha256'])
ck('existing binding inventory exact',{str(x)for x in E.glob('*.inputs.json')}==set(f['existing_actual_bindings']));ck('binding hashes exact',all(h(Path(n))==v for n,v in f['existing_actual_bindings'].items()))
# Real saved compiler values, no compiler execution.
B=Path(p['wasm_build']);tool=read(P/'toolchain.json');metas=list((B/'CMakeFiles').glob('*/CMake*Compiler.cmake'));actual={}
for m in metas:
 for k,v in re.findall(r'^set\((CMAKE_(?:CXX_COMPILER|C_COMPILER|AR|RANLIB)) "([^"]+)"\)$',m.read_text(),re.MULTILINE):
  ck('actual no conflict '+k,k not in actual or actual[k]==v);actual[k]=v
ck('actual required compiler metadata',set(actual)=={'CMAKE_CXX_COMPILER','CMAKE_C_COMPILER','CMAKE_AR','CMAKE_RANLIB'})
for k,v in actual.items():ck('actual frozen tool '+k,v in tool['files']and h(Path(v))==tool['files'][v]['sha256']and str(Path(v).resolve())==tool['files'][v]['realpath'])
defs=ast.Module(body=[fn(tree,'verify'),fn(tree,'configure_receipt')],type_ignores=[])
with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='power-v5-review-')as td:
 root=Path(td);build=root/'build';evidence=root/'evidence';evidence.mkdir();md=build/'CMakeFiles'/'4.4.3';md.mkdir(parents=True);cache=build/'CMakeCache.txt';meta=md/'CMakeCXXCompiler.cmake'
 tools={}
 for name in ['cc','cxx','ar','ranlib','make']:
  x=root/name;x.write_text(name);tools[str(x)]={'sha256':h(x),'realpath':str(x)}
 names=dict(zip(['CMAKE_C_COMPILER','CMAKE_CXX_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_MAKE_PROGRAM'],tools));base={'CMAKE_GENERATOR':'Unix Makefiles','CMAKE_MAKE_PROGRAM':names['CMAKE_MAKE_PROGRAM']}
 ns={'pathlib':__import__('pathlib'),'re':re,'profile':{'native_build':str(build),'wasm_build':str(build)},'evidence':evidence,'tool':{'files':tools},'sha':h,'read':read,'json':json,'f':{'inputs':{}},'actual_binding_hashes':{}}
 exec(compile(defs,'exact-author-v5-functions','exec'),ns)
 def reset():
  for x in evidence.glob('*.inputs.json'):x.unlink()
  ns['actual_binding_hashes'].clear();cache.write_text(''.join(k+':STRING='+v+'\n'for k,v in base.items()));meta.write_text(''.join('set('+k+' "'+v+'")\n'for k,v in names.items()if k!='CMAKE_MAKE_PROGRAM'))
 reset();ns['configure_receipt']('wasm-configure');ns['verify']();receipt=evidence/'wasm-configure.inputs.json';ck('metadata fallback positive',len(read(receipt)['actual_tool_pins'])==5 and len(read(receipt)['compiler_binding_files'])==1)
 reset();cache.write_text(cache.read_text()+'CMAKE_C_COMPILER:FILEPATH=/different\n');reject('cache metadata conflict',lambda:ns['configure_receipt']('wasm-configure'))
 reset();meta.write_text(meta.read_text()+'set(CMAKE_C_COMPILER "/different")\n');reject('metadata internal conflict',lambda:ns['configure_receipt']('wasm-configure'))
 for k in ['CMAKE_C_COMPILER','CMAKE_CXX_COMPILER','CMAKE_AR','CMAKE_RANLIB']:
  reset();meta.write_text('\n'.join(x for x in meta.read_text().splitlines()if not x.startswith('set('+k+' ')));reject('missing '+k,lambda:ns['configure_receipt']('wasm-configure'))
 reset();ns['configure_receipt']('wasm-configure');original=receipt.read_bytes();reject('exclusive receipt',lambda:ns['configure_receipt']('wasm-configure'));ck('receipt not rewritten',receipt.read_bytes()==original)
 for what in ['meta','cache','receipt','extra','delete','tool']:
  reset();ns['configure_receipt']('wasm-configure')
  target={'meta':meta,'cache':cache,'receipt':receipt,'extra':evidence/'extra.inputs.json','delete':receipt,'tool':Path(names['CMAKE_AR'])}[what]
  oldbytes=target.read_bytes()if target.exists()else None
  if what=='delete':target.unlink()
  else:target.write_bytes((oldbytes or b'')+b' ')
  reject('postbinding drift '+what,ns['verify'])
  if what=='tool':target.write_bytes(oldbytes)
print(json.dumps({'identity':'independent-power-wasm-transport-v5-review-v2','decision':'ACCEPT bounded remaining3 resume transport only','checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0,'actual_source_or_tools_modified':False},indent=2))
