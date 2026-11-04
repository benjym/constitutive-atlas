"""CI qualification of the SLS isolated common-engine target; frozen references."""
import argparse,copy,importlib.util,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/ingestion/sls-comsol63/execution-v1'
s=importlib.util.spec_from_file_location('sls_study',BASE/'study.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--solver',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    cases=json.loads((BASE/'cases.json').read_text())['cases'];rows=[]
    for source in cases:
        c=copy.deepcopy(source)
        if c.get('restart_from'):
            previous=next(r for r in rows if r['id']==c['restart_from']);parent=json.loads(previous['calls'][0]['stdout'])['state'];c['argv'][c['argv'].index('--initial')+1]=m.csv(parent)
        row=dict(id=c['id'],calls=[])
        for repeat in range(2):
            r=subprocess.run([str(a.solver.resolve()),*c['argv']],capture_output=True,text=True,timeout=180);row['calls'].append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        data=json.loads(row['calls'][0]['stdout'])
        if c['ok']and c['kind']=='direct'and data['ok']:
            r=subprocess.run([str(a.solver.resolve()),'--mode','observe-time','--model',m.MODEL,'--parameters',m.csv(c['parameters']),'--initial',m.csv(data['state']),'--strain-rate',m.csv(c['rate']),'--start-time',str(c['time'])],capture_output=True,text=True,check=True);row['observation']=r.stdout
        rows.append(row);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(capture=rows),indent=2)+'\n')
    report=m.assess(cases,rows);a.output.write_text(json.dumps(dict(report=report,capture=rows),indent=2)+'\n');print('SLS native frozen cases:',report['passed'],report['cases'],'cases;',report['calls'],'material calls')
if __name__=='__main__':main()
