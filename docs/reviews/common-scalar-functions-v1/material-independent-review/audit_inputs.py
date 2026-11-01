"""Source-only prospective closure audit; never imports compiled artifacts."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[4]
B=ROOT/'docs/reviews/common-scalar-functions-v1'
D=B/'material-reference-v1'
E=D/'execution-v3'
fail=[]
def check(ok,label):
    if not ok: fail.append(label)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((B/'material-source-freeze-v1.json').read_text())
check(len(freeze['files'])==63,'63 frozen files')
for p,h in freeze['files'].items(): check(Path(p).is_file() and sha(Path(p))==h,'freeze '+p)
actual={str(p) for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
check(actual==set(freeze['files']),'recursive material closure completeness')
bindings=json.loads((D/'unchanged-bindings.json').read_text())
check(len(bindings)==19,'19 bindings')
for original,entry in bindings.items():
    check(sha(ROOT/original)==entry['sha256']==sha(ROOT/entry['copy']),'unchanged '+original)
historical=sum(p.startswith('docs/ingestion/') for p in bindings)
check(historical==18,'18 historical bindings plus current main.cpp')
headers=E/'frozen/cpp/include/atlas'
liveheaders=ROOT/'cpp/include/atlas'
check({p.relative_to(headers) for p in headers.rglob('*') if p.is_file()}=={p.relative_to(liveheaders) for p in liveheaders.rglob('*') if p.is_file()}|{Path('scalar_functions.hpp')},'all current headers plus scalar interface')
source_counts={'proposal':0,'current':0}
for p in (E/'frozen/cpp').rglob('*'):
    if not p.is_file(): continue
    rel=p.relative_to(E/'frozen')
    proposed=B/'proposed-v2'/rel
    expected=proposed if proposed.is_file() else ROOT/rel
    check(expected.is_file() and sha(p)==sha(expected),'cpp source '+str(rel))
    source_counts['proposal' if proposed.is_file() else 'current']+=1
helper=E/'frozen/cmake/AtlasScalarFunctions.cmake'
check(sha(helper)==sha(B/'proposed-v2/cmake/AtlasScalarFunctions.cmake'),'exact helper overlay')
text=helper.read_text()
check('PUBLIC -ffp-contract=off' in text and 'POSITION_INDEPENDENT_CODE ON' in text and 'link_libraries(atlas_scalar_functions)' in text,'helper propagation/PIC')
listed=re.findall(r'\$\{ATLAS_SCALAR_ROOT\}/([^"\n]+)',text)
check(len(listed)==12 and all((E/'frozen'/p).is_file() for p in listed),'12 C source paths resolve inside frozen root')
cmake=(E/'CMakeLists.txt').read_text()
check('LANGUAGES C CXX' in cmake and cmake.index('include(')<cmake.index('add_executable(') and cmake.index('include(')<cmake.index('add_library('),'both consumers inherit helper before creation')
commands=json.loads((B/'material-commands-v1.json').read_text())
for backend in ['native','wasm']:
    c=commands[backend+'_configure']; build=commands[backend+'_build']
    check(c[:2]==(['emcmake','cmake'] if backend=='wasm' else ['cmake','-S']),backend+' configure executable')
    check(c[c.index('-S')+1]==str(E),backend+' exact source')
    check('-DCMAKE_BUILD_TYPE=Release' in c and '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON' in c,backend+' Release and commands')
    check(build==['cmake','--build',c[c.index('-B')+1],'--target','atlas_duncan_api','--parallel','1'],backend+' one explicit serial target')
req=json.loads((E/'requests.json').read_text())
counts={k:len(req[k]) for k in ['cases','paths','invalids','transactions','derivatives','presets']}
check(counts==dict(cases=72,paths=42,invalids=43,transactions=2,derivatives=2,presets=2),'original required matrix')
check('d<=4e-8' in (E/'parity.py').read_text() and 'abs(p-q)<=4e-5' in (E/'parity.py').read_text(),'unchanged parity budgets')
result=dict(identity='common-scalar-duncan-prospective-independent-v1',pass_=not fail,failures=fail,frozen_files=len(freeze['files']),historical_unchanged_files=historical,current_main_binding=1,source_counts=source_counts,matrix=counts,compiled_execution=False)
(Path(__file__).parent/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(bool(fail))
