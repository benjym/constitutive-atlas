"""Prepare a private single-target metadata build; never invoke a compiler here."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from tests.test_stress_scope import scope_fixtures

def prepare(destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=False)
    fixtures=destination/'fixtures';fixtures.mkdir()
    for name,model in scope_fixtures().items():(fixtures/(name+'.json')).write_text(json.dumps(model,indent=2)+'\n')
    generate(destination/'generated',list(fixtures.glob('*.json')))
    cmake=f'''cmake_minimum_required(VERSION 3.20)
project(AtlasScopeMetadata LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_scope_metadata_tests "{ROOT}/tests/test_stress_scope.cpp")
target_include_directories(atlas_scope_metadata_tests PRIVATE "{ROOT}/cpp/include" "{destination}/generated")
'''
    (destination/'CMakeLists.txt').write_text(cmake)
    sources=sorted(set([*ROOT.glob('cpp/include/atlas/*.hpp'),*ROOT.glob('atlas/*.py'),ROOT/'tests/test_stress_scope.cpp',ROOT/'tests/test_stress_scope.py',Path(__file__),Path(__file__).with_name('freeze.json')]))
    pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    generated={str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.rglob('*') if p.is_file()}
    (destination/'pre-build.json').write_text(json.dumps(dict(source_sha256=pins,generated_sha256=generated,material_calls=0),indent=2)+'\n')
    print(destination)
if __name__=='__main__':prepare(sys.argv[1])
