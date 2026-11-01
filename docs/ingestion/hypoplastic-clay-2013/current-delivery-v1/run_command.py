"""Bounded serial coordinator execution; retain command, streams, failure status."""
import argparse,datetime,json,os,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('seconds',type=int);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
root=Path(__file__).resolve().parents[4];out=Path(__file__).resolve().parent/'execution'/a.name
out.mkdir(parents=True,exist_ok=False)
command=a.command[1:] if a.command[:1]==['--'] else a.command
assert command and a.seconds>0
record={'command':command,'cwd':str(root),'deadline_seconds':a.seconds,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'}
(out/'STATUS.json').write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic()
with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
 process=subprocess.Popen(command,cwd=root,stdout=stdout,stderr=stderr,start_new_session=True)
 try:code=process.wait(timeout=a.seconds);record.update(status='passed' if code==0 else 'failed',exit_code=code)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGTERM)
  try:process.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
  record.update(status='timeout',exit_code=process.returncode)
record['elapsed_seconds']=time.monotonic()-start
(out/'STATUS.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(0 if record['status']=='passed' else 1)
