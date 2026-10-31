"""Prepare private recorded scope cases and one explicit serial gate target."""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tests.laboratory_scope_support import generate_transport_fixture
from gate import plan,csv,sha

def prepare(destination):
    d=Path(destination).resolve();d.mkdir(parents=True,exist_ok=False);generate_transport_fixture(d)
    previous=json.loads(Path(__file__).with_name('previous-sources.json').read_text())
    old=d/'archived-main.cpp';old.write_bytes((ROOT/previous['cpp/main.cpp']['archived_path']).read_bytes())
    cases=plan(json.loads((d/'generated/models.json').read_text())['models']);(d/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
    for i,case in enumerate(cases):
        (d/f'controls-{i}.csv').write_text(csv(case['controls']));(d/f'knots-{i}.csv').write_text(csv(case['knots']))
    zero=next(c for c in cases if c['label']=='total-strain-None');controls=csv(zero['controls']);knots=csv(zero['knots']);initial=csv(zero['initial'])
    driver=f'''#define main atlas_unused_recorded_main
#include "{ROOT}/cpp/main.cpp"
#undef main
int main() {{
const char* id="scope-synthetic-total-elastic";const char* e="0,0,0,0,0,0";const char* c="{controls}";const char* k="{knots}";const char* z="{initial}";
std::cout<<atlas_replay_recorded(id,"bad","bad",e,c,k,"","")<<std::endl;
std::cout<<atlas_replay_recorded_with_restarts(id,"bad","bad",e,c,k,"","","0,0.0001,8")<<std::endl;
std::cout<<atlas_replay_recorded_scope(id,"bad","bad",e,c,k,"","",nullptr)<<std::endl;
std::cout<<atlas_replay_recorded_scope_with_restarts(id,"bad","bad",e,c,k,"","","0,0.0001,8","effective")<<std::endl;
std::cout<<atlas_replay_recorded_scope(id,"",z,e,c,k,"","","total")<<std::endl;
std::cout<<atlas_replay_recorded_scope_with_restarts(id,"",z,e,c,k,"","","0,0.0001,8","total")<<std::endl;
}}
'''
    (d/'api-driver.cpp').write_text(driver)
    (d/'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.20)
project(AtlasRecordedScope LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_recorded_scope_solver "{ROOT}/cpp/main.cpp")
add_executable(atlas_recorded_legacy_solver "{old}")
add_executable(atlas_recorded_scope_api_driver "{d}/api-driver.cpp")
foreach(target atlas_recorded_scope_solver atlas_recorded_legacy_solver atlas_recorded_scope_api_driver)
 target_include_directories(${{target}} PRIVATE "{ROOT}/cpp/include" "{d}/generated")
endforeach()
add_custom_target(atlas_recorded_scope_gate DEPENDS atlas_recorded_scope_solver atlas_recorded_legacy_solver atlas_recorded_scope_api_driver)
''')
    sources=[*ROOT.glob('cpp/include/atlas/*.hpp'),*ROOT.glob('atlas/*.py'),ROOT/'cpp/main.cpp',ROOT/'tests/laboratory_scope_support.py',*Path(__file__).parent.glob('*.py'),Path(__file__).with_name('freeze.json')]
    pre=dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(sources))},generated_sha256={str(p.relative_to(d)):sha(p) for p in sorted(d.rglob('*')) if p.is_file()})
    (d/'pre-build.json').write_text(json.dumps(pre,indent=2)+'\n');print(d)
if __name__=='__main__':prepare(sys.argv[1])
