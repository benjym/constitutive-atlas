"""Read-only toolchain resolution freeze; no compiler execution."""
from pathlib import Path
import os,shutil,json,hashlib
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
commands=['python3','node','cmake','emcc','emcmake','em++','emar','emranlib','clang','clang++','make','ninja','ar','ranlib','ld','xcrun']
resolved={}
files={}
def add(p):
 p=Path(p)
 if p.is_file():files[str(p)]=dict(realpath=str(p.resolve()),sha256=sha(p))
for n in commands:
 p=shutil.which(n)
 resolved[n]=None if p is None else dict(path=p,realpath=str(Path(p).resolve()))
 if p:add(p)
e=Path('/opt/homebrew/Cellar/emscripten/6.0.8/libexec')
for p in e.rglob('*'):
 if p.is_file() and (p.suffix in ['.py','.cmake','.json','.js'] or (p.parent==e and p.name.startswith('em'))):add(p)
for n in ['clang','clang++','wasm-ld','llvm-ar','llvm-ranlib','llvm-nm','llvm-objcopy','llvm-strip','opt','llc','llvm-as']:
 add(e/'llvm/bin'/n)
for p in (e/'binaryen/bin').glob('*'):add(p)
for base in [e/'llvm/lib',Path('/opt/homebrew/Cellar/cmake/4.4.3/share/cmake/Modules')]:
 if base.exists():
  for p in base.rglob('*'):
   if p.is_file() and (p.suffix in ['.dylib','.cmake','.json']):add(p)
for p in ['/opt/homebrew/opt/python@3.14/bin/python3.14','/opt/homebrew/opt/node/bin/node','/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang','/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++','/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/ld','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.json',str(e/'.emscripten')]:add(p)
keys=['CC','CXX','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','SDKROOT','DEVELOPER_DIR','CMAKE_GENERATOR','CMAKE_TOOLCHAIN_FILE','EM_CONFIG','EM_LLVM_ROOT','EM_BINARYEN_ROOT','EM_NODE_JS','EM_COMPILER_WRAPPER','EMCC_CFLAGS','EMMAKEN_CFLAGS','JAVA_HOME','PYTHON','NODE_OPTIONS','NODE_PATH','DYLD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','MACOSX_DEPLOYMENT_TARGET']
# Ambient overrides must match this freeze; all currently absent.
ambient={k:os.environ.get(k)for k in keys}
assert all(v is None for v in ambient.values()),ambient
obj=dict(identity='profile-toolchain-source-freeze-v2',PATH=os.environ['PATH'],environment={'EMCC_CORES':'1','EM_CACHE':'/private/tmp/atlas-predictor-constraints-v1/em-cache-v1'},ambient_exact=ambient,commands=resolved,files=files,versions={'emcc':'6.0.8-git','cmake':'4.4.3','apple_clang':'21.0.0 clang-2100.4.1.1'},version_observation='Only emcc --version, cmake --version, clang --version and xcrun resolution queries executed; no builds or Atlas calls.',scope='Resolved entry points, Emscripten Python/JS/CMake inputs, LLVM/Binaryen tools and libraries, CMake modules and native compiler/SDK identity. Not a hermetic full OS/SDK/sysroot/runtime-library archive. Actual CMake compiler/linker/cache/SDK receipts must agree before build; retain generated dependency metadata. Cache mutable and excluded from exact source-byte comparison; private path and single owner required.')
(D/'toolchain.json').write_text(json.dumps(obj,indent=2)+'\n');print('Frozen toolchain files:',len(files))
