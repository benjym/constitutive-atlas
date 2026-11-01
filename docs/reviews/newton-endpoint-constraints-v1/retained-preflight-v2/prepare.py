"""One-shot generic solver regression source/input freeze before execution."""
from pathlib import Path
import json,shutil,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from atlas.compiler import generate
F=B/'frozen';F.mkdir(exist_ok=True)
assert not (B/'freeze.json').exists()
D=R/'docs/ingestion/duncan-chang-1970/material-v1';T=R/'catalogue/investigations/tresca-solution-constraints-v4'
for p in sorted((R/'cpp/include').rglob('*')):
    if p.is_file():dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
for name,p in [('00-tresca.json',T/'frozen/model.json'),('01-duncan.json',D/'candidate.json')]:shutil.copyfile(p,F/name)
m=json.loads((F/'01-duncan.json').read_text());m['id']='fixture-newton-history';m['name']='Synthetic linear stress and maxhistory fixture';m['description']='Analytical generic endpoint constraint regression; not a physical model';m['sources']=[{'url':'https://github.com/benjym/constitutive-atlas','locator':'Generic solver regression synthetic equations; no physical source claim','role':'Synthetic analytical fixture'}]
m['equations']['sigma']='sigma-sigma_n-p_ref*de';m['domain']=['p_ref>0*p_ref','least>0*p_ref','h_n>=D_old'];(F/'02-fixture.json').write_text(json.dumps(m,indent=2)+'\n')
m['id']='fixture-infeasible-root';m['name']='Synthetic inadmissible root';m['equations']['h']='h-h_n';(F/'03-infeasible.json').write_text(json.dumps(m,indent=2)+'\n')
generate(F/'generated',[F/'00-tresca.json',F/'01-duncan.json',F/'02-fixture.json',F/'03-infeasible.json'])
for name in ['corpus.inc','history.inc','checks.inc']:shutil.copyfile(T/name,F/name)
requests=[]
for case in json.loads((D/'references.json').read_text())['cases']:
    requests.append(dict(id=case['id'],model=1,parameters=list(case['parameters'].values()),initial=case['initial'],de=case['de'],target=case['target'],expect_success=True))
base=requests[0];p=base['parameters'];z=[100000.]*3+[0.]*4
for label,de,target,h in [('primary',[.1,0.,0.,0.,0.,0.],[110000.,100000.,100000.,0.,0.,0.],10000.),('hydro',[.1]*3+[0.]*3,[110000.]*3+[0.]*3,0.),('extension',[0.,.1,.1,0.,0.,0.],[100000.,110000.,110000.,0.,0.,0.],10000.),('unload',[-.05,0.,0.,0.,0.,0.],[105000.,100000.,100000.,0.,0.,0.],10000.)]:
    requests.append(dict(id='synthetic-'+label,model=2,parameters=p,initial=z if label!='unload' else [110000.,100000.,100000.,0.,0.,0.,10000.],de=de,target=target+[h],expect_success=True))
for label,model,de,initial,setting in [('infeasible-root',3,[.1,0.,0.,0.,0.,0.],z,{}),('domain-boundary',2,[-2.,0.,0.,0.,0.,0.],z,{}),('invalid-parent',2,[0.]*6,[110000.,100000.,100000.,0.,0.,0.,0.],{}),('iteration-exhaustion',2,[.1,0.,0.,0.,0.,0.],z,{'max_iterations':1})]:
    requests.append(dict(id='synthetic-'+label,model=model,parameters=p,initial=initial,de=de,target=initial,expect_success=False,settings=setting))
(B/'requests.json').write_text(json.dumps(requests,indent=2)+'\n')
# Exact binary values embedded as bit_cast constants, never decimal C++ literals.
def wire(xs):return '{'+','.join('std::bit_cast<double>(std::uint64_t('+str(__import__('struct').unpack('>Q',__import__('struct').pack('>d',x))[0])+'ULL))' for x in xs)+'}'
lines=['struct Request{std::string id;int model;State p,z,de;int iterations;};','inline std::vector<Request> requests(){return {']
for c in requests:lines.append('{"'+c['id']+'",'+str(c['model'])+','+','.join(wire(c[k]) for k in ['parameters','initial','de'])+','+str(c.get('settings',{}).get('max_iterations',45))+'},')
lines+=['};}'];(F/'requests.hpp').write_text('\n'.join(lines)+'\n')
shutil.copyfile(B/'driver.cpp',F/'driver.cpp')
(F/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(AtlasNewtonEndpointRegression LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_newton_regression EXCLUDE_FROM_ALL driver.cpp)
target_include_directories(atlas_newton_regression PRIVATE cpp/include generated)
target_compile_options(atlas_newton_regression PRIVATE -Wall -Wextra -Wno-unused-variable -Wno-misleading-indentation -fno-fast-math -ffp-contract=off)
if(EMSCRIPTEN)
 target_compile_options(atlas_newton_regression PRIVATE -fexceptions)
 target_link_options(atlas_newton_regression PRIVATE -fexceptions "-sENVIRONMENT=node" "-sEXIT_RUNTIME=1" "-sSTACK_SIZE=1048576" "-sALLOW_MEMORY_GROWTH=1")
 set_target_properties(atlas_newton_regression PROPERTIES OUTPUT_NAME newton-regression SUFFIX ".js")
endif()
''')
files={}
for folder in [R/'atlas',R/'schemas']:
 for source in sorted(folder.glob('*.py' if folder.name=='atlas' else '*.json')):
  dest=F/source.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
for source in sorted(F.rglob('*')):
 if source.is_file():files[source.relative_to(B).as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
for name in ['CONTRACT.md','requests.json','driver.cpp','assess.py','prepare.py']:files[name]=hashlib.sha256((B/name).read_bytes()).hexdigest()
for name in ['corpus-requests.txt','history-requests.txt','corpus-requests.json','history-inputs.json','corpus-policy.json','assess_corpus.py','assess_history.py']:
 source=T/name
 if source.exists():dest=B/'prior-tresca'/name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest);files[dest.relative_to(B).as_posix()]=hashlib.sha256(dest.read_bytes()).hexdigest()
tools={}
for cmd in [['c++','--version'],['cmake','--version'],['emcc','--version'],['node','--version']]:
 r=subprocess.run(cmd,capture_output=True,text=True);tools[' '.join(cmd)]=dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
(B/'freeze.json').write_text(json.dumps(dict(identity='newton-endpoint-constraints-v1',files=files,toolchains=tools,build_order='native then Wasm; one explicit target --parallel1'),indent=2)+'\n')
print(len(files),'frozen files',len(requests),'newton requests')
