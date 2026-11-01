"""Separate CLI harness correction; reuse every exact original material response."""
import hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('study',B/'study.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    out=B/'native-observe-v2-raw.json';assert not out.exists()
    rows=json.loads((B/'native-raw.json').read_text());cases=json.loads((B/'cases.json').read_text())['cases'];receipts=[]
    for c,row in zip(cases,rows):
        if 'observation'in row:
            state=json.loads(row['calls'][0]['stdout'])['state']
            cmd=[sys.argv[1],'--mode','observe-time','--model',m.MODEL,'--parameters',m.csv(c['parameters']),'--initial',m.csv(state),'--strain-rate',m.csv(c['rate']),'--start-time',str(c['time'])]
            r=subprocess.run(cmd,capture_output=True,text=True,check=True);row['observation']=r.stdout;receipts.append(dict(id=c['id'],argv=cmd[1:],returncode=r.returncode,stdout=r.stdout))
    out.write_text(json.dumps(rows,indent=2)+'\n');(B/'observation-repair-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    original=json.loads((B/'native-raw.json').read_text());assert all(a['calls']==b['calls']for a,b in zip(original,rows))
    report=m.assess(cases,rows);report['original_material_calls_preserved']=True
    (B/'native-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
