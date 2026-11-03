"""Read-only GitHub monitor; no local material calls or repository edits."""
from pathlib import Path
import datetime,json,subprocess,sys,time
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
expected="ac22788b918a47c837e61ddd76bde5894b35cc5e"
for attempt in range(181):
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=subprocess.run(["gh","run","view","41682430918","--repo","benjym/constitutive-atlas","--json","databaseId,headSha,status,conclusion,url,jobs"],capture_output=True,text=True,timeout=60)
  if r.returncode:raise RuntimeError(r.stderr)
  result=json.loads(r.stdout);assert result["headSha"]==expected
  observation={"observed_at":started,"run":result}
  with (out/"observations.jsonl").open("a") as f:f.write(json.dumps(observation)+"\n")
  (out/"latest.json").write_text(json.dumps(observation,indent=2)+"\n")
  if result["status"]=="completed":
   (out/"completed.json").write_text(json.dumps(observation,indent=2)+"\n")
   if result["conclusion"]!="success":
    log=subprocess.run(["gh","run","view","41682430918","--repo","benjym/constitutive-atlas","--log-failed"],capture_output=True,text=True,timeout=120)
    (out/"failed.log").write_text(log.stdout);(out/"failed-log.stderr").write_text(log.stderr)
   sys.exit(0 if result["conclusion"]=="success" else 1)
 except Exception as error:
  with (out/"errors.jsonl").open("a") as f:f.write(json.dumps({"observed_at":started,"error":str(error)})+"\n")
 time.sleep(60)
(out/"observation-deadline.json").write_text(json.dumps({"terminal_result_observed":False,"reason":"Three-hour monitor deadline; workflow not cancelled or restarted"})+"\n")
