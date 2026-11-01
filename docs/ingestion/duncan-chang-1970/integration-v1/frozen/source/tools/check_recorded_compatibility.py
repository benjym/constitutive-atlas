"""Compare existing native commands across two explicit binaries; never builds."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess


def compare(prior,current):
    ids=subprocess.check_output([str(prior),'--list'],text=True).splitlines()
    cases=[['--describe']]
    for model in ids:
        for protocol in range(1,6):
            cases.append(['--model',model,'--protocol',str(protocol),'--target','.001','--steps','8'])
        for mode in ['integrate','linearize']:
            base=['--mode',mode,'--model',model,'--strain','.0001,0,0,0,0,0']
            cases.extend([base,base+['--integration-settings','2e-10,1e-7,45,14,20000,11']])
    def run(binary,args):
        p=subprocess.run([str(binary),*args],capture_output=True,text=True,timeout=60)
        d=json.loads(p.stdout);d.pop('elapsed_ms',None)
        return dict(returncode=p.returncode,stderr=p.stderr,response=d)
    rows=[]
    for args in cases:
        a,b=run(prior,args),run(current,args)
        if a!=b:raise ValueError(f'existing native command changed: {args}')
        rows.append(dict(argv=args,prior=a,current=b))
    result=dict(ok=True,cases=len(rows),models=ids,excluded_fields=['elapsed_ms'],
                prior_binary_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),
                new_binary_sha256=hashlib.sha256(current.read_bytes()).hexdigest())
    return result,rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior',type=Path,required=True);parser.add_argument('--current',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    summary,rows=compare(args.prior.resolve(),args.current.resolve());args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'compatibility.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    (args.output/'compatibility-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
