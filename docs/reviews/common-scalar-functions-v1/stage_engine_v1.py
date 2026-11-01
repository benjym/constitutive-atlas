"""Fresh ordinary engine source closure, exact proposal overlay, no shared edits."""
from pathlib import Path
import json,hashlib,shutil,subprocess
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=Path('/private/tmp/atlas-common-scalar-functions-v1/engine-source-v1');assert not dst.exists();dst.mkdir(parents=True)
paths={r/'CMakeLists.txt',r/'.github/workflows/verify.yml'}
for directory,patterns in [('atlas',['*.py']),('schemas',['*.json']),('cpp',['*.cpp','*.hpp']),('tests',['*.cpp','*.hpp','*.json']),('models',['*.json']),('cmake',['CMakeLists.txt']),('web',['*.mjs']),('tools',['*.mjs','*.py'])]:
 for pat in patterns:paths.update((r/directory).rglob(pat))
for n in ['laboratory-package-policy.json','laboratory-profile-policy.json','approved-models.json','manifest.json','laboratory-examples.json']:paths.add(r/'catalogue'/n)
original={}
for f in sorted(paths):
 d=dst/f.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);original[str(f.relative_to(r))]=hashlib.sha256(f.read_bytes()).hexdigest()
for f in sorted((p/'proposed-v2').rglob('*')):
 if f.is_file():
  d=dst/f.relative_to(p/'proposed-v2');d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
with (p/'engine-generation-v1.log').open('w') as log:x=subprocess.run(['python3','-B','-m','atlas.compiler',str(dst/'generated')],cwd=dst,stdout=log,stderr=subprocess.STDOUT)
assert x.returncode==0
cat=json.loads((dst/'generated/models.json').read_text());assert len(cat['models'])==14 and cat['sha256']=='38f03e0099cfee9c89deaa59e729ac43563d4d39b17d321721a199e58d3b77d4'
fs=[f for f in dst.rglob('*') if f.is_file()];(p/'engine-source-freeze-v1.json').write_text(json.dumps({'identity':'ordinary14-common-scalar-engine-v1','source':str(dst),'original_live_inputs':original,'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'catalogue_sha256':cat['sha256'],'status':'Prospective before any compiled full engine observations'},indent=2)+'\n')
cs={};tmp='/private/tmp/atlas-common-scalar-functions-v1'
for backend in ['native','wasm']:
 cs[backend+'_configure']=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(dst),'-B',tmp+'/engine-'+backend+'-v1','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
 for target in (['atlas_solver','atlas_numerical_tests','atlas_recorded_tests'] if backend=='native' else ['atlas_solver']):cs[backend+'_build_'+target]=['cmake','--build',tmp+'/engine-'+backend+'-v1','--target',target,'--parallel','1']
(p/'engine-commands-v1.json').write_text(json.dumps(cs,indent=2)+'\n');print(len(fs),'engine files; exact14catalogue retained')
