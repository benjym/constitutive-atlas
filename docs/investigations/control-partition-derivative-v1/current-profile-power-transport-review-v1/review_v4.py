"""Superseding exact v4 bounded transport review, AST/synthetic state only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json,tempfile,types
D=Path(__file__).resolve().parent;A=D.parent/'current-profile-actual-power-v3'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def check(name,value):checks.append({'id':name,'passed':bool(value)});assert value,name
def rejects(name,fn):
    try:fn()
    except (RuntimeError,FileExistsError,FileNotFoundError):checks.append({'id':name,'passed':True});return
    raise AssertionError('Unexpected acceptance '+name)
check('exactv4runner',h(A/'run-v4.py')=='40feb6563b372646bf9dd6e1ae2499f7ca3422e00c187d6d94e7517e7dcbf5d9')
check('exactv4freeze',h(A/'freeze-v4.json')=='5618622b9cafc878f2c01a0b6c6c7ddf40957c11ac7791de7b3f38d0ca00b03e')
check('v4allfrozeninputs',all(h(Path(n))==v for n,v in read(A/'freeze-v4.json')['inputs'].items()))
old=ast.parse((A/'run.py').read_text());tree=ast.parse((A/'run-v4.py').read_text())
oldloop=next(n for n in old.body if isinstance(n,ast.For));newloop=next(n for n in tree.body if isinstance(n,ast.For))
check('remaining7stagebodiesbyteequivalentAST',[ast.dump(n)for n in oldloop.body]==[ast.dump(n)for n in newloop.body] and ast.unparse(newloop.iter)=="profile['steps'][1:]")
capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
check('captureverifiesbeforeandafter',ast.unparse(capture.body[0])=='verify()'and ast.unparse(capture.body[-2])=='verify()')
oldcapture=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
check('capturetransportotherwiseunchanged',[ast.dump(n)for n in capture.body[1:-2]]+[ast.dump(capture.body[-1])]==[ast.dump(n)for n in oldcapture.body])
definitions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['verify','configure_receipt']],type_ignores=[])
with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='power-v4-review-')as t:
    root=Path(t);build=root/'build';evidence=root/'evidence';build.mkdir();evidence.mkdir();(build/'CMakeFiles').mkdir()
    cache=build/'CMakeCache.txt';frozen=root/'input';frozen.write_text('synthetic frozen input')
    base_values={'CMAKE_CXX_COMPILER':'/usr/bin/c++','CMAKE_C_COMPILER':'/usr/bin/cc','CMAKE_AR':'/mock/ar','CMAKE_RANLIB':'/mock/ranlib','CMAKE_MAKE_PROGRAM':'/mock/make','CMAKE_GENERATOR':'Unix Makefiles','CMAKE_OSX_SYSROOT':''}
    states={name:{'hash':'known-wrapper'if name.startswith('/usr/bin/')else'known-'+name,'realpath':name,'exists':True}for name in ['/usr/bin/c++','/usr/bin/cc','/mock/ar','/mock/ranlib','/mock/make']}
    class SyntheticTool:
        def __init__(self,name):self.name=name
        def __str__(self):return self.name
        def is_file(self):return states[self.name]['exists']
        def is_absolute(self):return self.name.startswith('/')
        def resolve(self):return states[self.name]['realpath']
    def path(value):return SyntheticTool(str(value))if str(value)in states else Path(value)
    def sha(p):return states[str(p)]['hash']if str(p)in states else h(Path(p))
    tools={name:{'sha256':s['hash'],'realpath':name}for name,s in states.items()if name.startswith('/mock/')}
    tools['/usr/bin/clang']={'sha256':'known-wrapper','realpath':'/usr/bin/clang'}
    ns={'pathlib':types.SimpleNamespace(Path=path),'profile':{'native_build':str(build),'wasm_build':str(build)},'evidence':evidence,'tool':{'files':tools},'sha':sha,'read':read,'json':json,'f':{'inputs':{str(frozen):h(frozen)}},'actual_binding_hashes':{}}
    exec(compile(definitions,'exact-v4-author-functions','exec'),ns)
    def reset(values=None):
        for p in evidence.glob('*.inputs.json'):p.unlink()
        ns['actual_binding_hashes'].clear()
        cache.write_text(''.join(k+':STRING='+v+'\n'for k,v in (base_values if values is None else values).items()))
        for name,s in states.items():s.update(hash='known-wrapper'if name.startswith('/usr/bin/')else'known-'+name,realpath=name,exists=True)
    reset();ns['configure_receipt']('native-configure');ns['verify']()
    receipt=evidence/'native-configure.inputs.json';check('positivealiasesand5toolbindings',len(read(receipt)['actual_tool_pins'])==5 and ns['actual_binding_hashes']=={str(receipt):h(receipt)})
    for name in ['/usr/bin/c++','/usr/bin/cc','/mock/ar']:
        for field,bad in [('hash','different'),('realpath','/different')]:
            reset();ns['configure_receipt']('native-configure');states[name][field]=bad
            rejects('postbinding-'+name+'-'+field,ns['verify'])
    reset();ns['configure_receipt']('native-configure');receipt.unlink();rejects('bindingreceiptdeletion',ns['verify'])
    reset();ns['configure_receipt']('native-configure');receipt.write_bytes(receipt.read_bytes()+b' ');rejects('bindingreceiptmutation',ns['verify'])
    reset();ns['configure_receipt']('native-configure');(evidence/'extra.inputs.json').write_text('{}');rejects('unexpectedbindingreceipt',ns['verify'])
    reset();ns['configure_receipt']('native-configure');oldbytes=receipt.read_bytes();rejects('exclusiveconfigureobservation',lambda:ns['configure_receipt']('native-configure'));check('observationnotrewritten',receipt.read_bytes()==oldbytes)
    reset();ns['configure_receipt']('native-configure');r=read(receipt);states['/usr/bin/c++']['hash']='changed';r['actual_tool_pins']['CMAKE_CXX_COMPILER']['sha256']='changed';receipt.write_text(json.dumps(r));rejects('receiptcannotrepinchangedalias',ns['verify'])
    for key in ['CMAKE_C_COMPILER','CMAKE_GENERATOR']:
        values=dict(base_values);del values[key];reset(values);rejects('missingrequired-'+key,lambda:ns['configure_receipt']('native-configure'))
    reset();states['/usr/bin/cc']['exists']=False;rejects('nonexistentconfiguredcompiler',lambda:ns['configure_receipt']('native-configure'))
    for key,value in [('CMAKE_C_COMPILER','/unknown/unfrozen'),('CMAKE_GENERATOR','Ninja'),('CMAKE_OSX_SYSROOT','/unknown/sdk')]:
        values=dict(base_values);values[key]=value;reset(values);rejects('unreviewedconfiguredvalue-'+key,lambda:ns['configure_receipt']('native-configure'))
    reset();ns['configure_receipt']('native-configure');ns['configure_receipt']('wasm-configure');ns['verify']();check('bothconfigurebindinginventoriesheld',len(ns['actual_binding_hashes'])==2)
(D/'v4-checks.json').write_text(json.dumps({'identity':'independent-current-power-v4-bounded-transport-review','decision':'accepted prospective bounded v4 transport only','checks':checks,'count':len(checks),'builds':0,'compiled_calls':0,'actual_tool_files_modified':False},indent=2)+'\n')
print(json.dumps({'decision':'accepted prospective bounded v4 transport','checks':len(checks),'compiled_calls':0}))
