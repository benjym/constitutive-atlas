"""Record reproducible engine-capability checks, not model admission evidence."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();solver=ROOT/'build/atlas_time_solver'
    description=json.loads(subprocess.check_output([str(solver),'--describe'],cwd=ROOT,text=True))
    expected=[json.loads(p.read_text()) for p in sorted((ROOT/'tests/fixtures/time').glob('*.json'))]
    if description['models']!=expected:raise ValueError('Native fixture catalogue is stale; rebuild before verification')
    commands=[[sys.executable,'-m','unittest','discover','-s','tests','-p','test_parent_reset.py','-v'],['node','tools/test_time_wasm.mjs']]
    runs=[]
    for command in commands:
        process=subprocess.run(command,cwd=ROOT,env={**os.environ,'ATLAS_TIME_SOLVER':str(solver)},text=True,capture_output=True,timeout=120)
        runs.append(dict(command=command,returncode=process.returncode,stdout=process.stdout,stderr=process.stderr))
    files=['atlas/model.py','atlas/dsl.py','atlas/compiler.py','atlas/structure.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp','schemas/model.schema.json','CMakeLists.txt','tests/test_parent_reset.py','tests/fixtures/parent-reset-cases.json','tools/test_time_wasm.mjs','tools/verify_parent_resets.py','docs/PARENT_INCREMENT_RESETS.md']
    files+=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests/fixtures/time').glob('*.json'))
    artifacts=['build/atlas_time_solver','build-wasm/time-fixtures.js','build-wasm/time-fixtures.wasm']
    passed=all(run['returncode']==0 for run in runs)
    report=dict(kind='engine-capability-verification',capability='parent-increment-reset',schema_version='0.1',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                scope='Synthetic reset semantics only; no SANISAND equation execution, reference equivalence, independent review or admission claim.',
                analytical_matrix_cases=len(json.loads((ROOT/'tests/fixtures/parent-reset-cases.json').read_text())['cases']),
                native_fixture_catalogue_hash=description['sha256'],passed=passed,runs=runs,
                source_files=[dict(path=p,sha256=sha(ROOT/p)) for p in files],
                built_artifacts=[dict(path=p,sha256=sha(ROOT/p)) for p in artifacts])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f'Parent reset verification {"passed" if passed else "failed"}; {args.output}')
    return 0 if passed else 1

if __name__=='__main__':sys.exit(main())
