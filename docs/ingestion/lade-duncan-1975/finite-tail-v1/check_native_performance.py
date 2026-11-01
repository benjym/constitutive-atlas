"""Exact previously timed-out request; unchanged 120-second hard bound."""
from pathlib import Path
import subprocess,json,time,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
EXE=ROOT/'.local/lade-finite-tail-v1/native-build/atlas_lade_domain_candidate'
RAW=ROOT/'.local/lade-finite-tail-v1/performance-raw.json'
cmd=[str(EXE),'--model','lade-duncan-1975-midpoint-elastic-eq19-gap-v4','--parameters','101325,103,40,0.44,0.957,0.000255,1.32,2300,0.8,0','--initial','60000,60000,60000,0,0,0,13,0','--protocol','1','--target','0.005','--steps','1600','--response-contract','stress-scope-0.1','--integration-settings','7.8125e-13,1e-06,45,20,200000,11,3.90625e-10,1']
started=time.monotonic();report={'command':cmd,'timeout_seconds':120,'exe_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'passed':False}
try:
 p=subprocess.run(cmd,capture_output=True,timeout=120);RAW.write_bytes(p.stdout);r=json.loads(p.stdout);report.update(returncode=p.returncode,ok=r.get('ok'),message=r.get('message'),raw_sha256=hashlib.sha256(p.stdout).hexdigest())
 ref=next(x['reference'] for x in json.loads((HERE/'triaxial-reference-results.json').read_text())['cases'] if x['set']=='dense' and x['reference']['axial_strain']==.005)
 bounds=json.loads((HERE/'triaxial-policy.json').read_text())['native_final_reference_bounds']
 if r.get('ok'):
  point=r['points'][-1];errors={'relative_axial_stress':abs(point['state'][0]-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(point['strain'][1]-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(point['state'][7]-ref['wp'])/max(1,abs(ref['wp']))};report.update(errors=errors,passed=p.returncode==0 and len(r['points'])==1601 and all(errors[k]<=v for k,v in bounds.items()))
except subprocess.TimeoutExpired as e:
 RAW.write_bytes(e.stdout or b'');report.update(timeout=True,raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest())
report['elapsed_seconds']=time.monotonic()-started
(HERE/'native-performance-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
