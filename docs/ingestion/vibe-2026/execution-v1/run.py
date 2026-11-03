from pathlib import Path
import subprocess,sys,json,datetime,time,hashlib
out=Path(__file__).resolve().parent
name=sys.argv[1];command=sys.argv[2:];log=out/(name+'.log');receipt=out/(name+'.json')
assert not log.exists() and not receipt.exists()
start=time.monotonic();data={'command':command,'cwd':str(Path.cwd()),'started_utc':str(datetime.datetime.now(datetime.timezone.utc))}
receipt.write_text(json.dumps(data,indent=2)+'\n')
with log.open('w') as f:
 p=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
data.update(returncode=p.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
receipt.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data));sys.exit(p.returncode)
