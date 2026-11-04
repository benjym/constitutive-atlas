"""Reproduce current Atlas capability observations for SANISAND planning.

These are synthetic capacity/type probes, not SANISAND equations or numerical
verification. The source dossier owns the scientific requirements.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.dsl import Type, ValidationError, infer, parse
from atlas.model import validate


def inspect():
    fixture=json.loads((ROOT/'models/linear-elastic.json').read_text())
    fixture.update(id='sanisand-capacity-probe',status='draft',integration='rate',derived=[],domain=[])
    stress=copy.deepcopy(fixture['state'][0])
    memory=[dict(name=name,unit='1',shape='sym',initial=[0.]*6,scale='1') for name in ('alpha','fabric','alpha_in')]
    fixture['state']=[stress]+memory
    fixture['equations']={'sigma':'0 * p_ref * I',**{f['name']:'0 * I' for f in memory}}
    probes=[]
    for size in (24,25,26,32,33):
        model=copy.deepcopy(fixture)
        if size>=25:
            model['state'].append(dict(name='e',unit='1',shape='scalar',initial=.7,scale='1'))
            model['equations']['e']='0'
        if size==26:
            model['integration']='residual'
            model['state'].append(dict(name='gamma',unit='1',shape='scalar',initial=0.,scale='1',transient=True,multiplier=True))
            model['equations']['gamma']='gamma'
        if size>=32:
            for i in range(size-25):
                name=f'extra{i}';model['state'].append(dict(name=name,unit='1',shape='scalar',initial=0.,scale='1'));model['equations'][name]='0'
        try:
            validate(model);accepted=True;message=None
        except ValidationError as error:
            accepted=False;message=str(error)
        probes.append(dict(kind='synthetic-state-capacity',components=size,accepted=accepted,message=message))
    symbols={'n':Type('sym'),'x':Type()}
    for expression in ('dot(n,n)','cube_trace(n)','dev(n)','select(x > 0, n, 0 * I)','n * n','tensor_square(n)'):
        env={**symbols,'I':Type('sym')}
        try:
            result=infer(parse(expression),env);accepted=True;shape=result.shape;message=None
        except ValidationError as error:
            accepted=False;shape=None;message=str(error)
        probes.append(dict(kind='expression-type',expression=expression,accepted=accepted,shape=shape,message=message))
    paths=['atlas/model.py','atlas/dsl.py','atlas/compiler.py','atlas/structure.py','schemas/model.schema.json','schemas/model-v0.2.schema.json','cpp/include/atlas/tensor.hpp','cpp/include/atlas/solver.hpp','tools/inspect_sanisand_capabilities.py','schemas/run-v0.2.schema.json','cpp/include/atlas/schedule.hpp','tests/fixtures/time/capacity-32.json','tests/test_capacity.py','tests/test_capacity.cpp','tools/test_schedule_wasm.mjs','CMakeLists.txt']
    return dict(kind='capability-investigation',model_candidate='sanisand-2004',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='Synthetic capacity and type observations only; no constitutive execution, original-paper reconciliation or admission claim.',state_requirement=dict(stress=6,void_ratio=1,backstress=6,fabric=6,reversal_backstress=6,persistent_total=25,with_incremental_multiplier=26),probes=probes,source_files=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=inspect();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f"Recorded {len(report['probes'])} synthetic capacity/type observations; {args.output}")


if __name__=='__main__':main()
