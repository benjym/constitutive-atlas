"""Coordinator serial build provenance; invoke only after explicit slot handoff."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent
PLAN=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261102-v1/baseline-qualification-plan-v5')
spec=importlib.util.spec_from_file_location('prospective_plan',PLAN/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
 a=argparse.ArgumentParser();a.add_argument('--source-freeze',type=Path,required=True);a.add_argument('--work',type=Path,required=True);a.add_argument('--slot-handoff',required=True);args=a.parse_args()
 assert args.slot_handoff=='unheld-baseline-five-native-then-wasm-v1'
 pre=json.loads(args.source_freeze.read_text());repo=Path(pre['repo']);work=args.work.resolve();out=HERE/'actual-build-v1';assert not out.exists();out.mkdir()
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','EM_CACHE':str(work/'em-cache')}
 commands=[];logs=[];receipt={'identity':'baseline-five-actual-serial-build-v1','slot_handoff':args.slot_handoff,'source_freeze':m.pin(args.source_freeze),'execution_script':m.pin(__file__),'build_tools':pre['build_tools'],'source_sha256':pre['source_sha256'],'build_argv':[],'serial_builds_parallel_1':True,'all_processes_success':False,'commands':commands,'logs':logs,'generated_files':[],'resolved_compilers':{},'compiler_version_logs':[]}
 def save():m.write(out/'receipt.json',receipt)
 def bound():
  for pin in [*pre['inputs'],*pre['build_tools'].values(),pre['node'],pre['python']]:m.verify(pin)
  assert [m.pin(p) for p in m.source_files(repo)]==pre['source_inventory']
 def run(argv,name):
  bound();start=time.time();log=out/(name+'.log');row={'argv':list(map(str,argv)),'cwd':str(repo),'EM_CACHE':env['EM_CACHE'],'source_inventory_pre_sha256':hashlib.sha256(json.dumps(pre['source_inventory'],sort_keys=True).encode()).hexdigest(),'started_epoch':start};commands.append(row);save()
  try:
   with log.open('w') as stream:
    process=subprocess.run(row['argv'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT)
   row.update(returncode=process.returncode,status='process_returned')
  except BaseException as error:
   row.update(status='process_exception',process_error=repr(error))
   raise
  finally:
   row['elapsed_seconds']=time.time()-start
   if log.exists():row['log']=m.pin(log);logs.append(m.pin(log))
   save()
  bound();row['source_post_unchanged']=True;save();assert process.returncode==0,name
  return m.pin(log)
 cmake=pre['build_tools']['cmake']['path'];native=work/'native';wasm=work/'wasm'
 # Preserve the C++ driver invocation name even though the pinned Mach-O target
 # is the same clang binary. CMakeCache retains the actual invocation path.
 native_cxx=str(Path(pre['build_tools']['native_cxx']['path']).with_name('clang++'));native_cc=str(Path(native_cxx).with_name('clang'))
 assert m.pin(native_cxx)==pre['build_tools']['native_cxx']
 try:
  bound();assert (work/'em-cache').is_dir(),'copy preexisting Emscripten cache before build; never write system cache'
  for backend,directory in [('native',native),('wasm',wasm)]:
   assert not directory.exists(),'never overwrite an existing build attempt'
   configure=[cmake,'-S',str(repo),'-B',str(directory),'-DCMAKE_BUILD_TYPE=Release','-DPython3_EXECUTABLE='+pre['python']['path']]
   if backend=='native':configure+=['-DCMAKE_CXX_COMPILER='+native_cxx,'-DCMAKE_C_COMPILER='+native_cc]
   else:configure=[pre['build_tools']['emcmake']['path'],*configure]
   run(configure,backend+'-configure')
   argv=[cmake,'--build',str(directory),'--target','atlas_solver','--parallel','1'];receipt['build_argv'].append(argv);run(argv,backend+'-build')
   cache=(directory/'CMakeCache.txt').read_text();(out/(backend+'-CMakeCache.txt')).write_text(cache)
   receipt.setdefault('cmake_caches',[]).append(m.pin(out/(backend+'-CMakeCache.txt')))
   for language in ['CXX','C']:
    line=next(x for x in cache.splitlines() if x.startswith('CMAKE_'+language+'_COMPILER:FILEPATH=') or x.startswith('CMAKE_'+language+'_COMPILER:STRING='));compiler=Path(line.split('=',1)[1]).resolve()
    receipt.setdefault('all_resolved_compilers',{})[backend+'_'+language]=m.pin(compiler)
    if language=='CXX':receipt['resolved_compilers'][backend]=m.pin(compiler)
    receipt['compiler_version_logs'].append(run([str(compiler),'--version'],backend+'-'+language+'-compiler-version'))
   receipt['generated_files'] += [m.pin(directory/'generated'/name) for name in ['models.hpp','models.json']];save()
  receipt['artifacts']={key:m.sha(path) for key,path in [('native',native/'atlas_solver'),('module',wasm/'atlas.js'),('wasm',wasm/'atlas.wasm')]}
  receipt['artifact_pins']={key:m.pin(path) for key,path in [('native',native/'atlas_solver'),('module',wasm/'atlas.js'),('wasm',wasm/'atlas.wasm')]}
  bound();receipt['all_processes_success']=True;save()
 except BaseException as error:receipt['failure']=repr(error);save();raise
 print(json.dumps({'status':'BUILT','receipt':str(out/'receipt.json'),'artifacts':receipt['artifact_pins']}))
if __name__=='__main__':main()
