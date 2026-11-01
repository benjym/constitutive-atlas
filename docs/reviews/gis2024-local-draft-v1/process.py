"""Capture a terminal process receipt, including failure, before returning its status."""
import json,subprocess,sys,time
from pathlib import Path
receipt=Path(sys.argv[1]);command=sys.argv[2:];assert not receipt.exists();start=time.time()
r=subprocess.run(command,capture_output=True,text=True)
receipt.write_text(json.dumps({'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'started_unix':start,'finished_unix':time.time()},indent=2)+'\n')
print(json.dumps({'receipt':str(receipt),'returncode':r.returncode}));raise SystemExit(r.returncode)
