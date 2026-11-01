"""Run one frozen standard package command, preserving streams and terminal status."""
from pathlib import Path
import json,subprocess,time,datetime
HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'INPUT_FREEZE.json').read_text())
out=HERE/'standard-builder';out.mkdir(exist_ok=False)
record={'argv':freeze['standard_builder_argv'],'cwd':freeze['source_root'],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','builds':0}
(out/'STATUS.json').write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic()
with (out/'stdout.log').open('wb') as a,(out/'stderr.log').open('wb') as b:
    p=subprocess.Popen(record['argv'],cwd=record['cwd'],stdout=a,stderr=b)
    record['pid']=p.pid
    (out/'STATUS.json').write_text(json.dumps(record,indent=2)+'\n')
    code=p.wait()
record.update(status='passed' if code==0 else 'failed',exit_code=code,elapsed_seconds=time.monotonic()-start)
(out/'STATUS.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));raise SystemExit(code)
