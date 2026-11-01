from pathlib import Path
import json,hashlib,shutil,re
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=p/'proposed-v3';assert not dst.exists();shutil.copytree(p/'proposed-v2',dst)
def put(name,text):
 f=dst/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)
q=p/'qualification-v2'
for name,target in [('scalar_probe.cpp','tests/scalar_functions_probe.cpp'),('requests.json','tests/fixtures/scalar-functions/requests.json'),('references.json','tests/fixtures/scalar-functions/references.json')]:
 f=dst/target;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q/name,f)
for name,target in [('collect_native.py','tools/collect_scalar_functions.py'),('collect_wasm.mjs','tools/collect_scalar_functions_wasm.mjs'),('assess.py','tools/check_scalar_functions.py')]:
 s=(q/name).read_text()
 if name.endswith('.py'):s=s.replace('p=Path(__file__).parent;',"p=Path(__file__).resolve().parents[1]/'tests/fixtures/scalar-functions';")
 else:s=s.replace("const here=new URL('.',import.meta.url)","const here=new URL('../tests/fixtures/scalar-functions/',import.meta.url)")
 put(target,s)
put('tools/test_scalar_functions.py','''"""Run the frozen391case independent scalar/Jet qualification against a native library."""
from pathlib import Path
import subprocess,sys,tempfile
p=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='atlas-scalar-functions-') as directory:
 d=Path(directory)
 subprocess.run([sys.executable,str(p/'collect_scalar_functions.py'),sys.argv[1],str(d/'raw.json')],check=True)
 subprocess.run([sys.executable,str(p/'check_scalar_functions.py'),str(d/'raw.json'),str(d/'assessment.json')],check=True)
''')
cm=(dst/'CMakeLists.txt').read_text();cm+='''
# Independent bounded common-scalar value/Jet contract; same generic runtime.
if(EMSCRIPTEN)
  add_executable(atlas_scalar_probe EXCLUDE_FROM_ALL tests/scalar_functions_probe.cpp)
  set_target_properties(atlas_scalar_probe PROPERTIES OUTPUT_NAME scalar-functions SUFFIX .js)
  target_compile_options(atlas_scalar_probe PRIVATE -fexceptions)
  target_link_options(atlas_scalar_probe PRIVATE "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlasScalarFunctions" "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1" "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576" "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
else()
  add_library(atlas_scalar_probe SHARED tests/scalar_functions_probe.cpp)
  add_test(NAME atlas_scalar_functions COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/test_scalar_functions.py" "$<TARGET_FILE:atlas_scalar_probe>")
endif()
target_include_directories(atlas_scalar_probe PRIVATE cpp/include)
''';put('CMakeLists.txt',cm)
license=(dst/'cpp/scalar-functions/COPYRIGHT').read_text();notices=['Atlas common scalar functions\n\nAdapted from the musl/Arm and Sun mathematical sources shipped with Emscripten6.0.8. Symbol names and a minimal binary64 compatibility header are adapted; upstream notices remain in source.\n\n',license]
for f in sorted((dst/'cpp/scalar-functions').glob('*')):
 if f.suffix not in ['.c','.h']:continue
 m=re.match(r'(?:\s|/\*.*?\*/)*',f.read_text(),re.S)
 if m and m.group().strip():notices.append('\n\nSource: '+f.name+'\n'+m.group().strip()+'\n')
put('cpp/scalar-functions/NOTICES.txt',''.join(notices))
put('docs/SCALAR_FUNCTIONS.md','''# Common scalar arithmetic

The generic double/Jet power evaluator calls `atlas_scalar_power`; legacy cyclic target generation calls `atlas_cyclic_sine`. Material sine/cosine/logarithm retain their existing functions. The common C library uses the musl/Arm and Sun sources shipped with Emscripten6.0.8, with symbol names and a minimal binary64 compatibility header adapted. See `cpp/scalar-functions/NOTICES.txt` for preserved notices and `docs/reviews/common-scalar-functions-v1/` for exact sources, provenance, independent references, qualifications and retained failures.

Supported qualification uses GCC/Clang/Emscripten, binary64 evaluation width0, default round-to-nearest and no fast-math. `cmake/AtlasScalarFunctions.cmake` enables a C11 static library and propagates `-ffp-contract=off` to live consumers. New CMake consumers must enable C and C++, include the helper before targets, and retain its library linkage and usage flags. Audit actual commands; arbitrary external flags, other rounding modes, compilers and universal correct rounding are outside the established scope. Historical pinned builds retain their own original runtime/source identity.

The391-case independent contract covers selected finite powers/sines, classifications, signed zero, overflow/underflow and all38Jet lanes. Finite scalar error must be at most1ULP; active smooth positive-base derivatives use2e-300+2e-14*abs(reference). Inactive lanes remain positive zero, including singular/nonfinite inputs. Derivative claims at nonsmooth/domain boundaries remain explicitly bounded. Equal native/Wasm output alone is not independent equation verification.

Build `atlas_scalar_probe` explicitly with `--parallel 1`. Native qualification: `python3 tools/test_scalar_functions.py <library>`. Wasm qualification: `node tools/collect_scalar_functions_wasm.mjs <scalar-functions.js> <new-raw.json>` then `python3 tools/check_scalar_functions.py <new-raw.json> <new-assessment.json>`. Existing reports are never overwritten. The CTest `atlas_scalar_functions` test runs the native contract; scalar source/reference changes require fresh independent review and distinct evidence.

Changes affect compiled source identity. Requalify affected material/preset/package consumers and preserve source archives before installing a new runtime. Package distributions containing these routines retain the notices. This software qualification establishes neither experimental validation nor a generic finite-element update tangent.
''')
fs=[f for f in dst.rglob('*') if f.is_file()];(p/'install-proposal-freeze-v3.json').write_text(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'status':'Prospective exactsamequalifiedruntime; additive permanent391case check target/drivers/fixtures/docs/notices; no sharedinstallation'},indent=2)+'\n');print(len(fs),'proposedinstall files')
