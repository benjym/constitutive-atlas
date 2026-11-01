from pathlib import Path
import json,hashlib,subprocess
from fidelity import parse_response,same_response
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];P=HERE.parent/'outer-predictor-v1';RAW=ROOT/'.local/lade-fused-linear-v1';RAW.mkdir(exist_ok=True)
row=json.loads((P/'native-legacy-results.json').read_text())['requests'][44];cmd=row['command'].copy();cmd[0]=str(RAW/'native-build/atlas_lade_domain_candidate')
report={'scope':'exact original native failing-crossbackend legacycase response; not qualification','command':cmd,'timeout_seconds':120,'passed':False}
try:
 p=subprocess.run(cmd,capture_output=True,timeout=120)
 for name,data in [('stdout',p.stdout),('stderr',p.stderr)]:
  f=RAW/('legacy-exact.'+name);f.write_bytes(data);report[name]={'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()}
 baseline=ROOT/row['raw_path'];report.update(returncode=p.returncode,baseline={'path':row['raw_path'],'sha256':hashlib.sha256(baseline.read_bytes()).hexdigest()},exe_sha256=hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest())
 report['passed']=p.returncode==0 and same_response(parse_response(p.stdout),parse_response(baseline.read_text()))
except Exception as error:report['error']=repr(error)
(HERE/'native-legacy-exact-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
