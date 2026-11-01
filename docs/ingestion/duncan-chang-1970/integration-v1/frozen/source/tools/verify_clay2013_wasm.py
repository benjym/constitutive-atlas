"""Independently reassess every Wasm trajectory against the Decimal closed form."""
import argparse
import json
from pathlib import Path
from atlas.model import load
from atlas.initialization import canonical_hash
from tools.clay2013_integration_study import MODEL_PATH, assess
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);a=p.parse_args()
 report=json.loads(a.report.read_text());model=load(MODEL_PATH)
 if report['version']!='clay2013-isotropic-wasm-0.1' or report['model_sha256']!=canonical_hash(model):raise ValueError('model/report identity mismatch')
 result=assess(report['records'],model)
 print(f'Clay2013 Wasm: {len(result)} exact-reference trajectories assessed')
