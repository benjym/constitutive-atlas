"""AST/saved-source/manufactured values only; no current source or tool access."""
from pathlib import Path
import ast,hashlib,json,sys
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
check('only PLAN literal changes',new==old.replace("PLAN=HERE.parent/'baseline-qualification-plan-v5'",'PLAN=Path('+repr(str(Path(refs[0]['path']).parent))+')'))
for node in oldtree.body:
 if isinstance(node,ast.FunctionDef):
  other=next(x for x in newtree.body if isinstance(x,ast.FunctionDef) and x.name==node.name)
  check('unchanged complete runner function '+node.name,ast.dump(node,include_attributes=False)==ast.dump(other,include_attributes=False))
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
except StopIteration:check('known metadata-only missing cache compiler branch remains blocked',True)
else:raise AssertionError('expected original branch failure')
print(json.dumps({'identity':'baseline-current16-minimal-plan-source-checks-v1','status':'PASS','count':len(checks),'checks':checks,'actual_source_tools_git_sdk_process_module_material_calls':0,'qualification':'not executed; pending source pins, independent review and metadata-resolution plan'},indent=2))
