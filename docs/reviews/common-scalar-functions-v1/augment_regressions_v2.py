from pathlib import Path
import shutil,json,hashlib
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=p/'generic-regression-v2';assert not dst.exists();shutil.copytree(p/'generic-regression-v1',dst);old=r/'docs/reviews/bounded-partition-retry-v1';same=json.loads((dst/'unchanged-bindings.json').read_text());same={k.replace('generic-regression-v1','generic-regression-v2'):v for k,v in same.items()}
def cp(f,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);same[str(d.relative_to(r))]={'original':str(f.relative_to(r)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
for f in (old/'qualification-v2/prior-tresca').iterdir():
 if f.is_file():cp(f,dst/'partition/prior-tresca'/f.name)
for n in ['driver.cpp','POLICY.md']:cp(old/'recorded-counter-v1'/n,dst/'recorder'/n)
s=(dst/'CMakeLists.txt').read_text().replace('add_executable(atlas_spectral_multiplicity spectral/driver.cpp)','add_executable(atlas_spectral_multiplicity spectral/driver.cpp)\nadd_executable(atlas_recorded_retry_counter recorder/driver.cpp)').replace('foreach(target atlas_partition_regression atlas_partition_analytical atlas_spectral_multiplicity)','foreach(target atlas_partition_regression atlas_partition_analytical atlas_spectral_multiplicity atlas_recorded_retry_counter)');s+='target_include_directories(atlas_recorded_retry_counter PRIVATE partition/generated)\n';(dst/'CMakeLists.txt').write_text(s);(dst/'unchanged-bindings.json').write_text(json.dumps(same,indent=2)+'\n');fs=[f for f in dst.rglob('*') if f.is_file()];(p/'generic-regression-freeze-v2.json').write_text(json.dumps({'identity':'common-scalar-generic-regressions-v2','source':str(dst),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'status':'Prospective oldunchangedNewtongates81,Tresca219+history12+guards,partition8+42derivatives,recorder12work,spectral73all38seeds; no newcompiledobservations'},indent=2)+'\n')
cs={};tmp='/private/tmp/atlas-common-scalar-functions-v1'
for backend in ['native','wasm']:
 cs[backend+'_configure']=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(dst),'-B',tmp+'/generic-'+backend+'-v2','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
 for t in ['atlas_partition_analytical','atlas_partition_regression','atlas_spectral_multiplicity','atlas_recorded_retry_counter']:cs[backend+'_build_'+t]=['cmake','--build',tmp+'/generic-'+backend+'-v2','--target',t,'--parallel','1']
(p/'generic-regression-commands-v2.json').write_text(json.dumps(cs,indent=2)+'\n');print(len(fs),'generic v2files',len(same),'unchangedwitnesses')
