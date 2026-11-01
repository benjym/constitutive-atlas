"""AST-extracted transport functions and synthetic path/hash state only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json,types,tempfile,difflib
D=Path(__file__).resolve().parent;BASE=D.parent;A=BASE/'current-profile-actual-power-v3';P=BASE/'current-profile-execution-v3'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def check(name,value):
    checks.append({'id':name,'passed':bool(value)});assert value,name
check('exactrunner',h(A/'run-v2.py')=='e5950a68168e7c9d5c16881b71e092ddd8fa6a101b31708a18dc3bc79aca3be3')
check('exactfreeze',h(A/'freeze-v2.json')=='36fd868cebb0eec2fa96000e441e042bc15f74514378473fd612125d5d22d2e3')
freeze=read(A/'freeze-v2.json');check('allfreezeinputs',all(h(Path(n))==v for n,v in freeze['inputs'].items()))
plan=read(P/'plan.json');profile=next(p for p in plan['profiles']if p['profile']=='power-creep');tool=read(P/'toolchain.json')
check('exact8stages',len(profile['steps'])==8 and profile['steps'][0]['stage']=='native-configure')
evidence=Path(profile['output']);pre=read(evidence/'stage-receipts/native-configure.pre.json');post=read(evidence/'stage-receipts/native-configure.post.json')
check('priorconfigurepassed',pre['passed']is True and post['passed']is True and type(post['exit_status'])is int and post['exit_status']==0 and pre['command']==profile['steps'][0] and post['command']==profile['steps'][0] and post['pre_receipt_sha256']==h(evidence/'stage-receipts/native-configure.pre.json'))
check('priorconfigureprocesszero',read(evidence/'processes/native-configure/process.json')['returncode']==0)
check('priorconfigurerawhashes',all(h(Path(post[k]['path']))==post[k]['sha256']for k in ['stdout','stderr']))
for alias in ['/usr/bin/c++','/usr/bin/cc']:
    p=Path(alias)
    check('actualexactalias'+alias,p.is_file() and str(p.resolve())==alias and h(p)==tool['files']['/usr/bin/clang']['sha256'])
    check('aliasnotoriginaltoolmap'+alias,alias not in tool['files'])
old=ast.parse((A/'run.py').read_text());new=ast.parse((A/'run-v2.py').read_text())
oldloop=next(n for n in old.body if isinstance(n,ast.For));newloop=next(n for n in new.body if isinstance(n,ast.For))
check('all7remainingstagecommandsunchanged',ast.dump(oldloop.iter)=="Subscript(value=Name(id='profile', ctx=Load()), slice=Constant(value='steps'), ctx=Load())" and ast.dump(oldloop.target)==ast.dump(newloop.target) and [ast.dump(n)for n in oldloop.body]==[ast.dump(n)for n in newloop.body] and ast.unparse(newloop.iter)=="profile['steps'][1:]")
check('capturefunctionunchanged',ast.dump(next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='capture'))==ast.dump(next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name=='capture')))
# Extract definitions only: importing/executing the runner would build artifacts.
definitions=ast.Module(body=[n for n in new.body if isinstance(n,ast.FunctionDef)and n.name in ['verify','configure_receipt']],type_ignores=[])
with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='power-transport-review-')as t:
    root=Path(t);build=root/'build';out=root/'evidence';build.mkdir();out.mkdir();(build/'CMakeFiles').mkdir()
    (build/'CMakeFiles/CMakeCXXCompiler.cmake').write_text('# explicit synthetic compiler metadata\n')
    alias_state={'/usr/bin/c++':{'exists':True,'realpath':'/usr/bin/c++','hash':'known-wrapper'},'/usr/bin/cc':{'exists':True,'realpath':'/usr/bin/cc','hash':'known-wrapper'}}
    class SyntheticAlias:
        def __init__(self,name):self.name=name
        def __str__(self):return self.name
        def is_file(self):return alias_state[self.name]['exists']
        def resolve(self):return alias_state[self.name]['realpath']
    def fakepath(value):
        name=str(value)
        return SyntheticAlias(name)if name in alias_state else Path(value)
    def mocksha(path):return alias_state[str(path)]['hash']if str(path)in alias_state else h(Path(path))
    cache=build/'CMakeCache.txt';cache.write_text('CMAKE_CXX_COMPILER:FILEPATH=/usr/bin/c++\nCMAKE_C_COMPILER:FILEPATH=/usr/bin/cc\nCMAKE_GENERATOR:INTERNAL=Unix Makefiles\n')
    frozen_input=root/'frozen-input';frozen_input.write_text('frozen input')
    ns={'pathlib':types.SimpleNamespace(Path=fakepath),'profile':{'native_build':str(build),'wasm_build':str(build)},'evidence':out,'tool':{'files':{'/usr/bin/clang':{'sha256':'known-wrapper','realpath':'/usr/bin/clang'}}},'sha':mocksha,'json':json,'f':{'inputs':{str(frozen_input):h(frozen_input)}}}
    exec(compile(definitions,'exact-author-functions','exec'),ns)
    ns['configure_receipt']('native-configure');receipt=read(out/'native-configure.inputs.json')
    check('syntheticexactaliasesaccepted',receipt['passed']is True and len(receipt['actual_tool_pins'])==2)
    alias_state['/usr/bin/c++']['hash']='changed-after-configuration'
    ns['verify']()
    check('B1aliasdriftnotcheckedbysubsequentverify',receipt['actual_tool_pins']['CMAKE_CXX_COMPILER']['sha256']!=alias_state['/usr/bin/c++']['hash'])
    (D/'witness-alias-postbinding-gap.json').write_text(json.dumps({'synthetic_only':True,'receipt':receipt,'later_alias_hash':alias_state['/usr/bin/c++']['hash'],'runner_verify_accepts':True,'actual_tool_files_modified':False},indent=2)+'\n')
    alias_state['/usr/bin/c++']['hash']='known-wrapper';alias_state['/usr/bin/cc']['exists']=False
    ns['configure_receipt']('native-configure');receipt=read(out/'native-configure.inputs.json')
    check('B2missingconfiguredcompileraccepted',receipt['passed']is True and 'CMAKE_C_COMPILER'not in receipt['actual_tool_pins'])
    (D/'witness-missing-compiler.json').write_text(json.dumps({'synthetic_only':True,'receipt':receipt,'actual_tool_files_modified':False},indent=2)+'\n')
    alias_state['/usr/bin/cc']['exists']=True
    for mode in ['hash','realpath']:
        alias_state['/usr/bin/cc'][mode]='different'
        try:ns['configure_receipt']('native-configure')
        except RuntimeError:checks.append({'id':'wrongalias'+mode+'rejected','passed':True})
        else:raise AssertionError('wrong alias accepted')
        alias_state['/usr/bin/cc'][mode]='known-wrapper'if mode=='hash'else'/usr/bin/cc'
(D/'checks.json').write_text(json.dumps({'decision':'blocked prospective transport review','checks':checks,'builds':0,'compiled_calls':0,'actual_alias_files_modified':False},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'decision':'blocked','compiled_calls':0}))
