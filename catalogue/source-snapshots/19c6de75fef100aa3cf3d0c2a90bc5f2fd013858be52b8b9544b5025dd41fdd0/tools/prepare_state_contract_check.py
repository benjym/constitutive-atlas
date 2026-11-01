"""Prepare a small native state-contract check; compilation is a separate step."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import load, migrate_formulation


def prepare(destination):
    destination=Path(destination).resolve()
    destination.mkdir(parents=True,exist_ok=True)
    definitions=destination/'definitions'
    definitions.mkdir(exist_ok=True)
    paths=[]
    for source in ['models/linear-elastic.json','models/drucker-prager.json','tests/fixtures/time/clock.json']:
        legacy=load(ROOT/source)
        current=migrate_formulation(legacy)
        current['id']+='-v03'
        for model in [legacy,current]:
            path=definitions/(model['id']+'.json')
            path.write_text(json.dumps(model,indent=2)+'\n');paths.append(path)
    generate(destination/'generated',paths)
    cmake=['cmake_minimum_required(VERSION 3.20)',
           'project(atlas_state_contract LANGUAGES CXX)',
           'set(CMAKE_CXX_STANDARD 20)',
           f'add_executable(atlas_state_contract {json.dumps(str(ROOT/"cpp/main.cpp"))})',
           'target_include_directories(atlas_state_contract PRIVATE '+json.dumps(str(ROOT/'cpp/include'))+' '+json.dumps(str(destination/'generated'))+')']
    (destination/'CMakeLists.txt').write_text('\n'.join(cmake)+'\n')
    return destination


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',type=Path)
    print(prepare(parser.parse_args().destination))
