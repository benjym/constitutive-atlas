"""Prepare one serial native target; no compilation or execution here."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tests.laboratory_scope_support import generate_transport_fixture


def prepare(destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=False)
    generate_transport_fixture(destination)
    previous=json.loads(Path(__file__).with_name('previous-sources.json').read_text())
    old=destination/'archived';old.mkdir()
    shutil.copytree(ROOT/'cpp/include',old/'include')
    for name,record in previous.items():
        target=old/('main.cpp' if name=='cpp/main.cpp' else 'include/atlas/solver.hpp')
        target.write_bytes((ROOT/record['archived_path']).read_bytes())
    main=ROOT/'cpp/main.cpp';driver=destination/'api-driver.cpp'
    driver.write_text(f'''#define main atlas_scope_cli_unused_main
#include "{main}"
#undef main
int main() {{
 const char* id="scope-synthetic-total-elastic";
 const char* initial="100000,100000,100000,0,0,0,0.69999999999999996";
 const char* controls="0000000000000000,0000000000000000";
 std::cout<<atlas_run(id,"bad","bad",2,0,1,0)<<std::endl;
 std::cout<<atlas_run_with_settings(id,"bad","bad",2,0,1,0,"")<<std::endl;
 std::cout<<atlas_run_controls_with_settings(id,"bad","bad",2,controls,"")<<std::endl;
 std::cout<<atlas_run_scope_with_settings(id,"",initial,2,0,1,0,"")<<std::endl;
 std::cout<<atlas_run_controls_scope_with_settings(id,"",initial,2,controls,"")<<std::endl;
 return 0;
}}
''')
    (destination/'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.20)
project(AtlasLaboratoryScope LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_scope_solver "{ROOT}/cpp/main.cpp")
target_include_directories(atlas_scope_solver PRIVATE "{ROOT}/cpp/include" "{destination}/generated")
add_executable(atlas_scope_legacy_solver "{old}/main.cpp")
target_include_directories(atlas_scope_legacy_solver PRIVATE "{old}/include" "{destination}/generated")
add_executable(atlas_scope_api_driver "{driver}")
target_include_directories(atlas_scope_api_driver PRIVATE "{ROOT}/cpp/include" "{destination}/generated")
add_custom_target(atlas_laboratory_scope_gate DEPENDS atlas_scope_solver atlas_scope_legacy_solver atlas_scope_api_driver)
''')
    sources=sorted(set([*ROOT.glob('cpp/include/atlas/*.hpp'),*ROOT.glob('atlas/*.py'),ROOT/'cpp/main.cpp',ROOT/'tests/laboratory_scope_support.py',Path(__file__),Path(__file__).with_name('freeze.json')]))
    pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    generated={str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.rglob('*') if p.is_file()}
    (destination/'pre-build.json').write_text(json.dumps(dict(source_sha256=pins,generated_sha256=generated),indent=2)+'\n')
    print(destination)
if __name__=='__main__':prepare(sys.argv[1])
