#!/usr/bin/env python3
"""Build/run the source-pinned NH2004 clay research model with the common solver.

Example: python3 tools/run_nh2004.py --protocol drained --output /private/tmp/nh2004.json
This is a research formulation, not scientific admission or a deployed web model.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import load
MODEL=ROOT/'models/research/nh2004/nakai-hinokio-2004-clay-appendix-v-be.json'
PROTOCOLS={'oedometric':0,'drained':1,'undrained':2,'stress-controlled':3,'isotropic':4}

def build(directory):
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True)
    source=[MODEL,ROOT/'cpp/main.cpp',*sorted((ROOT/'cpp/include').rglob('*.hpp')),
            *sorted((ROOT/'atlas').rglob('*.py')),ROOT/'schemas/model-v0.3.schema.json']
    digest=hashlib.sha256()
    for f in source:digest.update(str(f.relative_to(ROOT)).encode());digest.update(f.read_bytes())
    fingerprint=digest.hexdigest();stamp=directory/'source-sha256.txt';binary=directory/'build/nh2004_solver'
    if not binary.exists() or not stamp.exists() or stamp.read_text().strip()!=fingerprint:
        generate(directory/'generated',[MODEL])
        cmake=['cmake_minimum_required(VERSION 3.20)','project(nh2004_research LANGUAGES CXX)',
               'set(CMAKE_CXX_STANDARD 20)',f'add_executable(nh2004_solver {json.dumps(str(ROOT/"cpp/main.cpp"))})',
               'target_include_directories(nh2004_solver PRIVATE '+json.dumps(str(ROOT/'cpp/include'))+' '+json.dumps(str(directory/'generated'))+')']
        (directory/'CMakeLists.txt').write_text('\n'.join(cmake)+'\n')
        for cmd in [['cmake','-S',str(directory),'-B',str(directory/'build'),'-DCMAKE_BUILD_TYPE=Debug'],
                    ['cmake','--build',str(directory/'build'),'--target','nh2004_solver','--parallel','1']]:
            subprocess.run(cmd,check=True,stdout=sys.stderr)
        stamp.write_text(fingerprint+'\n')
    return binary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',choices=PROTOCOLS,default='drained')
    parser.add_argument('--target',type=float,help='strain, or deviator stress in Pa for stress-controlled')
    parser.add_argument('--steps',type=int,default=100)
    parser.add_argument('--cycles',type=int,default=0)
    parser.add_argument('--pressure',type=float,default=98000.)
    parser.add_argument('--rho',type=float,default=0.,help='explicit initial density index (dimensionless)')
    parser.add_argument('--void-ratio',type=float,default=.83)
    parser.add_argument('--initial',type=Path,help='JSON array of all16state components, overrides scalar preparation options')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--build-dir',type=Path,default=Path(tempfile.gettempdir())/'constitutive-atlas-nh2004')
    parser.add_argument('--solver',type=Path,help='reuse an explicitly selected existing solver without building')
    args=parser.parse_args();model=load(MODEL)
    state=[args.pressure]*3+[0.]*3+[args.rho,args.void_ratio]+[1/math.sqrt(3)]*3+[0.]*3+[0.,0.]
    if args.initial:state=json.loads(args.initial.read_text())
    if len(state)!=16 or any(type(v)not in(int,float) or not math.isfinite(v)for v in state):parser.error('initial state must contain16finite numbers')
    target=args.target if args.target is not None else (5000. if args.protocol=='stress-controlled' else .01)
    binary=args.solver.resolve() if args.solver else build(args.build_dir)
    cmd=[str(binary),'--mode','run','--model',model['id'],'--initial',','.join(map(str,state)),
         '--protocol',str(PROTOCOLS[args.protocol]),'--target',str(target),'--steps',str(args.steps),
         '--cycles',str(args.cycles),'--integration-settings','2e-10,1e-6,45,14,20000,11']
    result=subprocess.run(cmd,check=True,capture_output=True,text=True)
    response=json.loads(result.stdout);text=json.dumps(response,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
        print(f'{args.output}: ok={response["ok"]}, points={len(response.get("points",[]))}')
    else:sys.stdout.write(text)
    return 0 if response['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
