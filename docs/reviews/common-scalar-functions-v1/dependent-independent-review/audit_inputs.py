"""Read-only prospective dependent source/command audit; no compiled calls."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent
errors=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(ok,label):
    if not ok:errors.append(label)
f=json.loads((B/'dependent-source-freeze-v1.json').read_text());src=Path(f['source']);files=f['files']
check(len(files)==518,'518 frozen files')
check({str(p) for p in src.rglob('*') if p.is_file() and '__pycache__' not in p.parts}==set(files),'recursive closure completeness')
for p,h in files.items():check(sha(p)==h,'frozen '+p)
consumer=json.loads((B/'consumer-source-freeze-v1.json').read_text());croot=Path(consumer['source'])
check(len(consumer['files'])==503,'503 parent consumer files')
for p,h in consumer['files'].items():check(sha(src/Path(p).relative_to(croot))==h,'unchanged consumer '+p)
commands=json.loads((B/'dependent-commands-v1.json').read_text());patches=commands['driver_path_patches'];check(len(patches)==1,'one path patch')
for p,h in commands['unchanged_inputs'].items():
    check(sha(R/p)==h,'original numerical gate '+p)
    if p==patches[0]['path']:
        original=(R/p).read_bytes();old=b'/private/tmp/atlas-maxwell-execution-v1/cli';new=str(src.parent/'cli').encode()
        check(original.count(old)==1 and (src/p).read_bytes()==original.replace(old,new),'only CLI temporary output path changed')
        check(sha(src/p)==patches[0]['copied_sha256'],'patch identity')
    else:check(sha(src/p)==h,'unchanged numerical gate '+p)
old=json.loads((R/'docs/ingestion/maxwell-itasca900/atlas-build-v1/prospective-commands.json').read_text())['commands']
for key,value in old.items():
    if key.endswith('_configure') or key.endswith('_build'):continue
    expected=[x.replace('/private/tmp/atlas-maxwell-current-v1/source',str(src)).replace('/private/tmp/atlas-maxwell-current-v1/native','/private/tmp/atlas-common-scalar-functions-v1/consumers-native-v1/maxwell').replace('/private/tmp/atlas-maxwell-current-v1/wasm','/private/tmp/atlas-common-scalar-functions-v1/consumers-wasm-v1/maxwell').replace('/private/tmp/atlas-maxwell-current-v1/presets',str(src.parent/'presets')).replace(str(R/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py'),str(src/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py')) for x in value]
    actual=commands['commands']['maxwell_'+key]
    check(actual['command']==expected and actual['cwd']==str(src),'exact old Maxwell command path translation '+key)
for backend in ['native','wasm']:
    configure=commands['commands'][f'norsand_{backend}_configure']['command'];build=commands['commands'][f'norsand_{backend}_build']['command']
    check(configure[:2]==(['emcmake','cmake'] if backend=='wasm' else ['cmake','-S']),'configure executable '+backend)
    check(configure[configure.index('-S')+1]==str(src/'cmake/controlled-path'),'controlled source '+backend)
    check('-DCMAKE_BUILD_TYPE=Release' in configure and '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON' in configure,'Release/commands '+backend)
    selected=next(x.split('=',1)[1].split(';') for x in configure if x.startswith('-DATLAS_PATH_MODELS='))
    check(selected==[str(src/p) for p in ['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json']],'three definitions and exact ABI order '+backend)
    check(all(str(Path(p)) in files for p in selected),'all selected definitions frozen '+backend)
    check(build==['cmake','--build',configure[configure.index('-B')+1],'--target','atlas_path_capability','--parallel','1'],'explicit serial target '+backend)
for p in ['cmake/maxwell/CMakeLists.txt','cmake/controlled-path/CMakeLists.txt']:
    text=(src/p).read_text();check('LANGUAGES C CXX' in text and text.index('AtlasScalarFunctions.cmake')<text.index('add_'),'helper before consumers '+p)
req=json.loads((src/'docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json').read_text())['requests']
check(len(req)==58 and sum(x['expected_status']==1 for x in req)==40 and sum(x['expected_status']==0 for x in req)==18,'NorSand58/40/18')
maxwell=json.loads((src/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text())['cases']
check(len(maxwell)==24 and sum(not x['ok'] for x in maxwell)==6,'Maxwell24 double-call main and6 rejection/recovery pairs')
result=dict(identity='common-scalar-dependent-prospective-independent-v1',pass_=not errors,failures=errors,frozen_files=len(files),unchanged_consumer_files=len(consumer['files']),unchanged_original_inputs=len(commands['unchanged_inputs']),driver_path_patches=len(patches),Maxwell_main_cases=len(maxwell),NorSand_requests=len(req),compiled_execution=False)
(O/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(errors))
