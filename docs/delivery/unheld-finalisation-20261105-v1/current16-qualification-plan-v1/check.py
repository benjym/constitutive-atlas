"""AST/saved-source/manufactured values only; no current source or tool access."""
from pathlib import Path
import ast,hashlib,json,sys,re,tempfile
sys.dont_write_bytecode=True
import commands as C
P=Path(__file__).resolve().parent;checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
refs=json.loads((P/'reused-inputs.json').read_text())['files']
for r in refs:
 raw=Path(r['path']).read_bytes();check('exact unchanged '+Path(r['path']).name,len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'])
old=Path(refs[3]['path']).read_text();new=(P/'build.py').read_text();oldtree=ast.parse(old);newtree=ast.parse(new)
check('PLAN selects exact old collector',"PLAN=Path("+repr(str(Path(refs[0]['path']).parent))+")"in new)
# Reverse only the declared metadata substitution to compare the whole original main AST.
normalized=new.replace("metadata=sorted((directory/'CMakeFiles').glob('*/CMake'+language+'Compiler.cmake'));assert len(metadata)==1,'exact unique generated compiler metadata required'\n    metadata_pin=m.pin(metadata[0]);receipt.setdefault('compiler_metadata',{})[backend+'_'+language]=metadata_pin;resolved=compiler(metadata[0],language)","line=next(x for x in cache.splitlines() if x.startswith('CMAKE_'+language+'_COMPILER:FILEPATH=') or x.startswith('CMAKE_'+language+'_COMPILER:STRING='));compiler=Path(line.split('=',1)[1]).resolve()")
normalized=normalized.replace('m.pin(resolved)','m.pin(compiler)').replace('run([str(resolved),','run([str(compiler),').replace(';m.verify(metadata_pin)','')
oldmain=next(x for x in oldtree.body if isinstance(x,ast.FunctionDef) and x.name=='main');newmain=next(x for x in ast.parse(normalized).body if isinstance(x,ast.FunctionDef) and x.name=='main')
check('whole runner main unchanged except exact declared compiler substitution',ast.dump(oldmain,include_attributes=False)==ast.dump(newmain,include_attributes=False))
recovery=P.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-execution-v5/build-metadata-recovery-v4/recover.py'
originalresolver=next(x for x in ast.parse(recovery.read_text()).body if isinstance(x,ast.FunctionDef)and x.name=='compiler');resolver=next(x for x in newtree.body if isinstance(x,ast.FunctionDef)and x.name=='compiler')
check('exact independently accepted compiler resolver AST',ast.dump(resolver,include_attributes=False)==ast.dump(originalresolver,include_attributes=False))
ns={'Path':Path,'re':re};exec(compile(ast.Module(body=[resolver],type_ignores=[]),'<exact accepted compiler resolver>','exec'),ns)
with tempfile.TemporaryDirectory(prefix='compiler-mock-',dir=P)as tmp:
 root=Path(tmp);f=root/'CMakeCXXCompiler.cmake'
 for label,data in [('one','set(CMAKE_CXX_COMPILER "/manufactured/clang++")\n'),('missing',''),('duplicate','set(CMAKE_CXX_COMPILER "/a")\nset(CMAKE_CXX_COMPILER "/b")\n'),('unquoted','set(CMAKE_CXX_COMPILER /a)\n'),('wronglanguage','set(CMAKE_C_COMPILER "/a")\n')]:
  f.write_text(data)
  try:answer=ns['compiler'](f,'CXX')
  except AssertionError:check('compiler resolver rejects '+label,label!='one')
  else:check('compiler resolver exact one literal',label=='one'and answer==Path('/manufactured/clang++'))
  
check('new build output is owned HERE',"out=HERE/'actual-build-v1'"in new)
check('native then Wasm explicit single target serial',"[('native',native),('wasm',wasm)]"in new and "'--target','atlas_solver','--parallel','1'"in new)
policy=json.loads(Path(refs[1]['path']).read_text());check('701 original cases',sum(policy['expected_case_counts'].values())==701)
check('five exact candidates',len(policy['candidate_sha256'])==5)
check('seven exact fixed gates',len(policy['unchanged_gate_sha256'])==7)
collector=Path(refs[0]['path']).read_text();check('interface42/replay87 untouched','len(interface)==42 and replay.used==87'in collector)
check('complete source inventory supports additional models',"['atlas','cpp','models','schemas','cmake','tools']"in collector and "len(definitions['models'])==15"not in collector)
pre={'repo':str(C.SOURCE),'compiled_observations':False,'python':{'path':'/manufactured/python'},'node':{'path':'/manufactured/node'}}
argv=C.phase_argv(pre);check('all five phases described',list(argv)==['build','freeze','native','wasm','pair'])
check('unchanged absolute collector routing',all(row[2]==str(C.COLLECTOR) for name,row in argv.items() if name!='build'))
check('new work only',argv['build'][argv['build'].index('--work')+1]==str(C.WORK))
check('actual postbuild freeze explicit artifacts',all(x in argv['freeze']for x in ['--native','--module','--wasm','--source-freeze','--build-receipt']))
preargv=C.source_freeze_argv('/manufactured/python','/manufactured/node',{k:'/manufactured/'+k for k in C.ROLE_KEYS})
check('prefreeze four explicit roles',preargv.count('--tool')==4)
# Retain rather than change the known metadata failure branch.
cache='CMAKE_BUILD_TYPE:STRING=Release\n'
try:next(x for x in cache.splitlines() if x.startswith('CMAKE_CXX_COMPILER:FILEPATH=')or x.startswith('CMAKE_CXX_COMPILER:STRING='))
except StopIteration:check('original cache-only failure reproduced for retained draft',True)
else:raise AssertionError('expected original branch failure')
import observe_phase as O
check('closed environment constructed without inherited variables',set(O.closed_environment())=={'PATH','HOME','XDG_CONFIG_HOME','TMPDIR','LC_ALL','TZ','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE','PYTHONHASHSEED','GIT_CONFIG_NOSYSTEM','GIT_CONFIG_SYSTEM','GIT_CONFIG_GLOBAL','GIT_CONFIG_COUNT','GIT_ATTR_NOSYSTEM','GIT_NO_REPLACE_OBJECTS','GIT_OPTIONAL_LOCKS','GIT_TERMINAL_PROMPT'})
check('outer exact unchanged observer7328',O.OBSERVER_SHA==refs[4]['sha256'])
check('outer1800 and failclosed return status',"timeout=1800"in (P/'observe_phase.py').read_text() and "assert result.returncode==0"in (P/'observe_phase.py').read_text())
current=json.loads((P.parent/'current-reference-script-pins.json').read_text());check('saved currentmain seven fixed gates all match',current['all_equal']is True and {r['path']:r['actual']for r in current['rows']}==policy['unchanged_gate_sha256'])
print(json.dumps({'identity':'baseline-current16-minimal-plan-source-checks-v1','status':'PASS','count':len(checks),'checks':checks,'actual_source_tools_git_sdk_process_module_material_calls':0,'qualification':'not executed; pending current16 candidate overlay, fresh source/tool/cache freeze and independent review'},indent=2))
