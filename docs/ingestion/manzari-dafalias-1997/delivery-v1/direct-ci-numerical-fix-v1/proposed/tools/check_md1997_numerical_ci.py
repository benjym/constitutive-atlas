"""Run native numerical checks, requiring the frozen Decimal assessor for exact MD17."""
from pathlib import Path
import argparse,hashlib,json,os,stat,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MD='manzari-dafalias-1997-constant-m-be-v1'
MD_SHA='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'
NATIVE='explicit-gis20-occ-restart-duncan-sclay1-v6'
DECIMAL='md1997-decimal-fd-reference-current17-v1'
SIXTEEN=set('barodesy-clay-2017 barodesy-sand drucker-prager duncan-chang-1970-endpoint-average hypoplastic-clay-2005 hypoplastic-clay-2013 hypoplastic-sand-igs97 hypoplastic-sand-vw96 linear-elastic modified-cam-clay mohr-coulomb original-cam-clay-sw-electronic-log-recovery-v1 ramberg-osgood-ansys242 research-hp-extracted-asbs-gis-2024-v03 s-clay1 tresca-associated-perfect-bk2022v1-be'.split())
REFERENCE_FILES={'requests.json': 'ee4158da6cc5f8f9bec55bb56183fd465e8ba1f710d83d1fa0f08d631e3bc098', 'reference.json': '74ae57a2b70b7042ef8e8408b589911d8fce723f8c27aac62accb34f4299e299', 'POLICY.md': '79152e516054320064d67b9dc333be0945d6738362b4ab17b968ffaaf84f087c', 'decimal_dsl.py': 'c0d7c733db1432f67370d832c6f4a9dc6db5b94ba2ddfa0955cec39aadf91668', 'assess_saved.py': '099dc18ab3fb8e60732c4bbe8423bc991debe181dc2faa77d401393125b7cb7d'}
def require(value,message):
 if not value:raise ValueError(message)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(data):return hashlib.sha256(data).hexdigest()
def read_regular(path):
 require(not path.is_symlink()and stat.S_ISREG(path.stat().st_mode),'regular input required: '+str(path));return path.read_bytes()
def record(path):
 data=read_regular(path);return {'sha256':digest(data),'bytes':len(data)}
def write(path,value):
 with path.open('x')as out:json.dump(value,out,sort_keys=True,indent=2);out.write('\n')
def json_read(path):return json.loads(read_regular(path))
def model_set(models):
 require(type(models)is list and all(type(m)is dict and type(m.get('id'))is str for m in models),'catalogue models')
 ids=[m['id']for m in models];require(len(ids)==len(set(ids)),'duplicate model ID');names=set(ids)
 require(names in(SIXTEEN,SIXTEEN|{MD}),'numerical CI requires exact reviewed16 or MD17 model membership')
 if MD in names:require(digest(read_regular(ROOT/'models'/(MD+'.json')))==MD_SHA,'exact MD source definition')
 return MD in names

def source_inventory():
 # Numerical compilation inputs only, including full model membership; no build/cache/docs scan.
 names={'CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tests/test_solver.cpp','tools/check_md1997_numerical_ci.py'}
 for directory,suffixes in [('atlas',{'.py'}),('cpp/include',{'.hpp','.h'}),('schemas',{'.json'})]:
  for base,dirs,files in os.walk(ROOT/directory,followlinks=False):
   require(all(not(Path(base)/n).is_symlink()for n in dirs),'source directory alias')
   dirs[:]=[n for n in dirs if n!='__pycache__']
   for n in files:
    path=Path(base)/n
    if path.suffix in suffixes:names.add(path.relative_to(ROOT).as_posix())
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'models').glob('*.json'))
 names.update('tools/md1997_decimal_reference_current17_v1/'+n for n in REFERENCE_FILES)
 return {n:record(ROOT/n)for n in sorted(names)}
def bindings(build):return {n:record(build/n)for n in ['generated/models.json','generated/models.hpp','atlas_numerical_tests']}
def require_unchanged(before,after):require(before==after,'numerical source/generated/executable inputs changed during execution')
def run_process(argv,cwd,environment,stdout,stderr,timeout):
 with stdout.open('xb')as out,stderr.open('xb')as err:
  return subprocess.run(argv,cwd=cwd,env=environment,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=timeout,check=False).returncode

def run(build,output):
 build=build.resolve();output=output.absolute();require(not output.exists(),'fresh numerical output directory required');output.mkdir(parents=True)
 report={'identity':'direct-md1997-numerical-ci-v1','passed':False};before=None;compiled=None
 try:
  before=source_inventory();compiled=bindings(build);write(output/'source-before.json',before);write(output/'build-before.json',compiled)
  catalog=json_read(build/'generated/models.json');require(set(catalog)=={'schema_version','sha256','models'}and catalog['schema_version']=='0.1','generated catalogue schema')
  require(digest(canonical(catalog['models']))==catalog['sha256'],'generated catalogue canonical hash')
  md=model_set(catalog['models']);sources=[json_read(p)for p in sorted((ROOT/'models').glob('*.json'))];require(catalog['models']==sources,'generated catalogue differs from complete current source models')
  env=dict(os.environ)
  for name in ['ATLAS_NATIVE_FIXTURES','ATLAS_NUMERICAL_FIXTURES','ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256','PYTHONPATH']:env.pop(name,None)
  env.update(ATLAS_NATIVE_FIXTURES=NATIVE,PYTHONOPTIMIZE='0',PYTHONDONTWRITEBYTECODE='1')
  executable=str(build/'atlas_numerical_tests');argv=[executable];binding_hash=None
  if md:
   for name,want in REFERENCE_FILES.items():require(record(ROOT/'tools/md1997_decimal_reference_current17_v1'/name)['sha256']==want,'frozen Decimal input: '+name)
   binding={'identity':'md1997-decimal-native-build-binding-current17-v1','purpose':'actual','source_freeze_sha256':digest(canonical(before)),'fixture_sha256':before['tests/test_solver.cpp']['sha256'],'generated_catalogue_sha256':compiled['generated/models.json']['sha256'],'executable_sha256':compiled['atlas_numerical_tests']['sha256'],'executable_path':executable,'working_directory':str(build),'model_sha256':MD_SHA}
   write(output/'build-binding.json',binding);binding_hash=digest((output/'build-binding.json').read_bytes());env.update(ATLAS_NUMERICAL_FIXTURES=DECIMAL,ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256=binding_hash)
  code=run_process(argv,str(build),env,output/'native.stdout',output/'native.stderr',600)
  report.update(model_count=len(catalog['models']),numerical_returncode=code,decimal_assessment_required=md)
  if md:
   process={'identity':'md1997-decimal-direct-process-current17-v1','purpose':'actual','argv':argv,'cwd':str(build),'returncode':code,'stdout':{'path':str(output/'native.stdout'),'sha256':digest((output/'native.stdout').read_bytes())},'stderr':{'path':str(output/'native.stderr'),'sha256':digest((output/'native.stderr').read_bytes())},'selectors':{'ATLAS_NATIVE_FIXTURES':NATIVE,'ATLAS_NUMERICAL_FIXTURES':DECIMAL,'PYTHONOPTIMIZE':'0'},'executable_sha256':compiled['atlas_numerical_tests']['sha256']};write(output/'process.json',process)
  require(type(code)is int and code==0,'native numerical child failed')
  if md:
   reference=ROOT/'tools/md1997_decimal_reference_current17_v1';assessment=output/'assessment.json'
   cmd=[sys.executable,'-B',str(reference/'assess_saved.py'),'--requests',str(reference/'requests.json'),'--reference',str(reference/'reference.json'),'--process',str(output/'process.json'),'--build-binding',str(output/'build-binding.json'),'--build-binding-sha256',binding_hash,'--output',str(assessment)]
   assess_code=run_process(cmd,str(ROOT),env,output/'assessor.stdout',output/'assessor.stderr',600);report['assessor_returncode']=assess_code
   require(type(assess_code)is int and assess_code==0 and assessment.is_file(),'Decimal assessor failed or produced no assessment');result=json_read(assessment)
   require(result.get('identity')=='md1997-decimal-saved-assessment-current17-v1'and result.get('passed')is True and result.get('purpose')=='actual'and type(result.get('comparisons'))is int and result['comparisons']==588 and result.get('failures')==[],'all588 frozen Decimal comparisons must pass')
   require(result.get('build_binding_sha256')==binding_hash and result.get('process_sha256')==digest((output/'process.json').read_bytes())and result.get('raw_output_sha256')==digest((output/'native.stdout').read_bytes()),'assessment actual child/binding linkage')
   report['comparisons']=result['comparisons']
  report['passed']=True
 except BaseException as error:report['error']={'type':type(error).__name__,'message':str(error)};raise
 finally:
  try:
   after=source_inventory();after_compiled=bindings(build);write(output/'source-after.json',after);write(output/'build-after.json',after_compiled)
   if before is not None:require_unchanged(before,after)
   if compiled is not None:require_unchanged(compiled,after_compiled)
  except BaseException as error:report['passed']=False;report['post_error']={'type':type(error).__name__,'message':str(error)};raise
  finally:write(output/'result.json',report)
 print(json.dumps(report,sort_keys=True));return report

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build',type=Path,default=ROOT/'build');parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();run(args.build,args.output)
if __name__=='__main__':main()
