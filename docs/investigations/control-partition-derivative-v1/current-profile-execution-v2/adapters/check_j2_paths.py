"""Frozen actual-history assessor; never constructs references from output."""
import argparse
import json
from pathlib import Path
import sys
import os
ROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve();sys.path.insert(0,str(ROOT))
OUTPUT=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()
assert OUTPUT.is_dir() and not OUTPUT.is_relative_to(ROOT), 'Fresh external output directory required'
from tools.study_j2 import close
from tools.run_j2 import run
BASE=ROOT/'docs/ingestion/j2-linear-hardening/execution-v2'

def assess(paths,raw):
    assert len(paths)==len(raw)
    count=0;stress=history=0
    for spec,row in zip(paths,raw):
        assert spec['id']==row['id']
        assert len(row['repeats'])==2 and row['repeats'][0]==row['repeats'][1]
        for rows in row['repeats']:
            assert len(rows)==len(spec['expected'])
            initial=spec['initial']
            for ref,data in zip(spec['expected'],rows):
                assert data['ok'] is True and data['initial']==initial
                stress=max(stress,close(data['state'][:6],ref[:6],.002))
                history=max(history,close(data['state'][6:],ref[6:],2e-10))
                initial=data['state'];count+=1
    return dict(passed=True,calls=count,max_stress_error_Pa=stress,max_history_error=history)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['native','assess']);ap.add_argument('path');a=ap.parse_args()
    paths=json.loads((BASE/'paths.json').read_text())
    if a.mode=='native':
        raw=[dict(id=s['id'],repeats=[run(a.path,s),run(a.path,s)]) for s in paths]
        (OUTPUT/'native-paths-raw.json').write_text(json.dumps(raw,indent=2)+'\n')
    else:raw=json.loads(Path(a.path).read_text())
    print(json.dumps(assess(paths,raw),indent=2))
