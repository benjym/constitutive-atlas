"""Execute the prospectively frozen orthotropic source-reference corpus serially."""
import argparse,json,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.orthotropic_reference import assess,csv
BASE=ROOT/'docs/ingestion/orthotropic-ogs/execution-v1'
def qualify(solver,output):
 output=Path(output);output.mkdir(parents=True,exist_ok=True);cases=json.loads((BASE/'references.json').read_text())['cases'];rows=[];states={}
 for c in cases:
  args=c['argv'].copy()
  if c.get('previous'):args[args.index('--initial')+1]=csv(states[c['previous']])
  r=subprocess.run([str(Path(solver).resolve()),*args],capture_output=True,text=True,timeout=30)
  d=json.loads(r.stdout);rows.append(dict(id=c['id'],argv=args,returncode=r.returncode,stderr=r.stderr,response=d))
  if d.get('ok'):states[c['id']]=d['state']
  (output/'raw.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
 report=assess(cases,rows);report['solver_sha256']=hashlib.sha256(Path(solver).read_bytes()).hexdigest();(output/'assessment.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--solver',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(qualify(a.solver,a.output),indent=2))
