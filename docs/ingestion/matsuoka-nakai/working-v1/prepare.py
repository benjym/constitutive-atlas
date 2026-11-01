"""Generate isolated normal Atlas catalogue and serial CMake target; no build."""
import sys
import json
import hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import load

def prepare(destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    model=P/'model.json';load(model);generate(destination/'generated',[model])
    cmake=['cmake_minimum_required(VERSION 3.20)','project(nh2004_research LANGUAGES CXX)',
      'set(CMAKE_CXX_STANDARD 20)',f'add_executable(nh2004_solver {json.dumps(str(ROOT/"cpp/main.cpp"))})',
      f'target_include_directories(nh2004_solver PRIVATE {json.dumps(str(ROOT/"cpp/include"))} {json.dumps(str(destination/"generated"))})']
    cmake += ['if(EMSCRIPTEN)',
      'set_target_properties(nh2004_solver PROPERTIES OUTPUT_NAME "nh2004" SUFFIX ".mjs")',
      'target_compile_options(nh2004_solver PRIVATE -fexceptions)',
      'target_link_options(nh2004_solver PRIVATE -fexceptions "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sENVIRONMENT=node,web,worker" "-sALLOW_MEMORY_GROWTH=1" "-sSTACK_SIZE=1048576" "-sEXPORTED_RUNTIME_METHODS=[ccall]" "--no-entry")',
      'else()',
      'add_executable(nh2004_transport '+json.dumps(str(P/'transport.cpp'))+')',
      'target_include_directories(nh2004_transport PRIVATE '+json.dumps(str(ROOT/'cpp/include'))+' '+json.dumps(str(destination/'generated'))+' '+json.dumps(str(destination))+')',
      'endif()']
    (destination/'atlas_cli_source.cpp').write_text('#include '+json.dumps(str(ROOT/'cpp/main.cpp'))+'\n')
    (destination/'CMakeLists.txt').write_text('\n'.join(cmake)+'\n')
    source=[ROOT/'cpp/main.cpp',*sorted((ROOT/'cpp/include/atlas').rglob('*.hpp')),*sorted((ROOT/'atlas').glob('*.py')),model,ROOT/'schemas/model-v0.3.schema.json']
    pins={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source}
    receipt=P/'build-source-pins.json'
    if receipt.exists():
        old=json.loads(receipt.read_text())
        assert old==pins,'Pinned source bytes changed; use a separate study identity.'
    else:receipt.write_text(json.dumps(pins,indent=2)+'\n')
    print(destination)
if __name__=='__main__':prepare(sys.argv[1])
