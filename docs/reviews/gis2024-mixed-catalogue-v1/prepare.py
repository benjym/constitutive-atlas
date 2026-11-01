"""Exclusive mixed-catalogue staging. No build or model integration."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from atlas.compiler import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def stage(destination,backend):
 for rel,h in read(HERE/'source-pins.json').items():assert sha(ROOT/rel)==h,rel
 destination.mkdir(parents=True,exist_ok=False)
 for rel in read(HERE/'source-pins.json'):
  target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
 shutil.copyfile(HERE/'gis-model.json',destination/'models/research-hp-extracted-asbs-gis-2024-v03.json')
 for rel,h in read(HERE/'existing-models.json').items():assert sha(destination/rel)==h
 original=sha(destination/'CMakeLists.txt')
 if backend=='native':
  p=destination/'CMakeLists.txt';s=p.read_text();old='add_executable(atlas_solver cpp/main.cpp)';assert s.count(old)==1;p.write_text(s.replace(old,'add_executable(atlas_solver qualification_runner.cpp)'));shutil.copyfile(HERE/'runner.cpp',destination/'qualification_runner.cpp')
 generate(destination/'expected-generated',sorted((destination/'models').glob('*.json')))
 for name in ['models.json','models.hpp']:assert sha(destination/'expected-generated'/name)==sha(HERE/'generated-eleven'/name)
 result={'backend':backend,'source_files':len(read(HERE/'source-pins.json')),'existing_models':10,'total_models':11,'original_cmake_sha256':original,'staged_cmake_sha256':sha(destination/'CMakeLists.txt'),'generated':{n:sha(destination/'expected-generated'/n)for n in ['models.json','models.hpp']},'integrations':0,'builds':0}
 (destination/'stage.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('backend',choices=['native','wasm']);a.add_argument('destination',type=Path);x=a.parse_args();print(json.dumps(stage(x.destination,x.backend),indent=2))
