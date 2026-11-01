"""Stage normal sources and a disclosed native C-API entrypoint; no build/run."""
import argparse,hashlib,importlib.util,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('frozen_gis_prepare',ROOT/'docs/reviews/gis2024-v03-research-freeze-v1/prepare.py');frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
def stage(destination,backend):
 result=frozen.prepare(destination)
 original=(destination/'CMakeLists.txt').read_bytes();cmake=original.decode()
 if backend=='native':
  assert cmake.count('add_executable(atlas_solver cpp/main.cpp)')==1
  cmake=cmake.replace('add_executable(atlas_solver cpp/main.cpp)','add_executable(atlas_solver qualification_runner.cpp)')
  (destination/'CMakeLists.txt').write_text(cmake);shutil.copyfile(HERE/'runner.cpp',destination/'qualification_runner.cpp')
 result['transport']='test-only persistent existing C ABI'if backend=='native'else'normal Emscripten C ABI'
 result['original_cmake_sha256']=hashlib.sha256(original).hexdigest();result['staged_cmake_sha256']=frozen.sha(destination/'CMakeLists.txt')
 if backend=='native':result['runner_sha256']=frozen.sha(destination/'qualification_runner.cpp')
 (destination/'stage.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('backend',choices=['native','wasm']);p.add_argument('destination',type=Path);a=p.parse_args();print(json.dumps(stage(a.destination,a.backend),indent=2))
