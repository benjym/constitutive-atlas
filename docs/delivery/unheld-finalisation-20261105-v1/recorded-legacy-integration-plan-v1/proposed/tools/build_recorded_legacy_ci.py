"""One serial historical-catalogue target with genuine bounded CI build receipts."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
LEGACY='1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c'
def pin(path):
 p=Path(path).resolve(strict=True)
 if not p.is_file():raise ValueError('regular file required: '+str(p))
 data=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def inventory():
 paths={ROOT/'CMakeLists.txt',ROOT/'.github/workflows/qualification.yml',ROOT/'cpp/main.cpp',ROOT/'tests/recorded_native_fixtures.py',Path(__file__).resolve()}
 for directory,suffixes in [('atlas',{'.py'}),('cpp/include',{'.h','.hpp'}),('schemas',{'.json'}),('cmake',{'.cmake','.txt'})]:
  for base,dirs,files in os.walk(ROOT/directory,followlinks=False):
   if any((Path(base)/n).is_symlink()for n in dirs):raise ValueError('source directory alias')
   dirs[:]=[n for n in dirs if n!='__pycache__']
   paths.update(Path(base)/n for n in files if Path(n).suffix in suffixes)
 for base,dirs,files in os.walk(ROOT/'cpp/scalar-functions',followlinks=False):
  if any((Path(base)/n).is_symlink()for n in dirs):raise ValueError('scalar directory alias')
  paths.update(Path(base)/n for n in files)
 paths.update([ROOT/'tools/generate_recorded_legacy_models.py',*sorted((ROOT/'catalogue/investigations/clay2005-preview-v1/models').glob('*.json'))])
 if any(p.is_symlink()or p.resolve()!=p for p in paths):raise ValueError('physical source files required')
 return {str(p.relative_to(ROOT)):pin(p)for p in sorted(paths)}
def metadata(build):
 cache=build/'CMakeCache.txt';data=cache.read_text();home=re.findall(r'^CMAKE_HOME_DIRECTORY:INTERNAL=(.*)$',data,re.M)
 if home!=[str(ROOT)]:raise ValueError('configured build source mismatch')
 rows=sorted((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake'))
 if len(rows)!=1:raise ValueError('unique configured CXX metadata required')
 text=rows[0].read_text();drivers=re.findall(r'^set\(CMAKE_CXX_COMPILER "([^"\n]+)"\)$',text,re.M)
 if len(drivers)!=1:raise ValueError('unique configured CXX driver required')
 files=[cache,*rows]
 for p in sorted((build/'CMakeFiles/atlas_recorded_legacy_solver.dir').rglob('*')):
  if p.is_file()and(p.suffix in {'.make','.txt','.d'}):files.append(p)
 return {'purpose':'measured at this build step, not an original configure receipt','files':[pin(p)for p in files],'resolved_cxx':pin(Path(drivers[0]))}
def run(build,output,github_output=None):
 build=Path(build).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
 receipt={'identity':'recorded-legacy-actual-CI-build-v1','status':'running','historical_catalogue':LEGACY,'prior_configure_process':None,'observations_are_current_build_step':True}
 def save():
  (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 save();primary=None;before=None;tools=None
 try:
  before=inventory();receipt['source_before']=before;receipt['configured_before']=metadata(build)
  cmake=shutil.which('cmake')
  if not cmake:raise ValueError('qualified cmake command unavailable')
  tools={'cmake':pin(cmake),'python':pin(sys.executable),'cxx':receipt['configured_before']['resolved_cxx']};receipt['tools']=tools
  argv=[tools['cmake']['path'],'--build',str(build),'--target','atlas_recorded_legacy_solver','--parallel','1']
  receipt.update(argv=argv,cwd=str(ROOT),started_epoch=time.time(),process_status='not_started');save()
  try:
   with (output/'build.stdout').open('w')as stdout,(output/'build.stderr').open('w')as stderr:
    process=subprocess.run(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,check=False)
   receipt.update(returncode=process.returncode,process_status='returned')
  except BaseException as error:receipt.update(process_status='raised',process_error=repr(error));raise
  finally:
   receipt['finished_epoch']=time.time();receipt['logs']=[pin(p)for p in [output/'build.stdout',output/'build.stderr']if p.exists()];save()
  if process.returncode!=0:raise RuntimeError('historical target build failed')
  sys.path.insert(0,str(ROOT))
  from tests.recorded_native_fixtures import legacy_paths
  expected=[json.loads(p.read_text())for p in legacy_paths()]
  generated=build/'recorded-legacy-generated';catalogue=json.loads((generated/'models.json').read_text())
  if catalogue['sha256']!=LEGACY or catalogue['models']!=expected or len(expected)!=5:raise ValueError('generated historical catalogue mismatch')
  if hashlib.sha256(json.dumps(catalogue['models'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=LEGACY:raise ValueError('historical catalogue canonical hash mismatch')
  receipt['generated']=[pin(generated/n)for n in ['models.json','models.hpp']];receipt['artifact']=pin(build/'atlas_recorded_legacy_solver');receipt['configured_after']=metadata(build)
  if receipt['configured_after']['resolved_cxx']!=tools['cxx']:raise ValueError('configured compiler changed during build')
  receipt['status']='passed'
 except BaseException as error:primary=error;receipt.update(status='failed',error=repr(error));raise
 finally:
  try:
   after=inventory();receipt['source_after']=after
   if before is not None and after!=before:raise ValueError('source mutated during historical build')
   if tools is not None:
    for row in tools.values():
     if pin(row['path'])!=row:raise ValueError('build tool mutated')
   receipt['post_bindings_unchanged']=True
  except BaseException as error:
   receipt.update(status='failed',post_binding_error=repr(error));save()
   if primary is None:raise
  finally:save()
 if github_output:
  try:
   with Path(github_output).open('a')as stream:stream.write('solver_sha256='+receipt['artifact']['sha256']+'\n')
  except BaseException as error:receipt.update(status='failed',github_output_error=repr(error));save();raise
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--github-output',type=Path);a=p.parse_args();r=run(a.build,a.output,a.github_output);print(json.dumps({'status':r['status'],'solver_sha256':r['artifact']['sha256']}))
