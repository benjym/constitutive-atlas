"""Run an explicit J2 increment history with the ordinary native CLI."""
import argparse
import json
from pathlib import Path
import subprocess

def run(solver,spec):
    z=spec['initial'];rows=[]
    for de in spec['increments']:
        csv=lambda a:','.join(format(v,'.17g') for v in a)
        cmd=[str(solver),'--mode','integrate','--model',spec['model'],
             '--parameters',csv(spec['parameters']),'--initial',csv(z),
             '--strain',csv(de),'--integration-settings',spec['integration_settings']]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        data=json.loads(r.stdout);rows.append(data)
        if not data['ok']:break
        z=data['state']
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('solver');ap.add_argument('specification');a=ap.parse_args()
    spec=json.loads(Path(a.specification).read_text());print(json.dumps(run(a.solver,spec),indent=2))
