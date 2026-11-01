import json,runpy,copy,contextlib,io,tempfile,subprocess,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'execution-v3':'6cc2d1917fff40debda7291c8cbc0d5dfcb87f599cc0489d0fb9f38716d85926','parity-v6':'78e1df94a76a6152eb8edf299374019ce5e4851328aea2814582bb531bcbedf7','ordinary-regression-v5':'65f9b41dc45b23f04cbc0398f2b8a3227ee29e18612f62f5a58812597f648a65'}
for name,h in expected.items():
 assert sha(P/name/'manifest.json')==h
 for file,digest in json.loads((P/name/'manifest.json').read_text()).items():assert sha(P/name/file)==digest
for name in ['requests.json','POLICY.md','check_reports.py','prepare.py','run_wasm.mjs']:
 assert (P/'execution-v1'/name).read_bytes()==(P/'execution-v3'/name).read_bytes()
with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(D.parent/'execution-prospective-review-v1/check_synthetic.py'))
base=ns['report'];base['identity']['manifest_sha256']=sha(P/'execution-v3/manifest.json');tests=[]
for name,mutate,expectedpass in [('synthetic new identity ideal',lambda r:None,True),('old manifest identity',lambda r:r['identity'].__setitem__('manifest_sha256',sha(P/'execution-v1/manifest.json')),False),('missing source case',lambda r:r['cases'].pop(ns['first']),False)]:
 r=copy.deepcopy(base);mutate(r)
 with tempfile.TemporaryDirectory(dir=D) as tmp:
  tmp=Path(tmp);inp=tmp/'SYNTHETIC.json';out=tmp/'checks.json';inp.write_text(json.dumps(r));p=subprocess.run(['python3','-B',str(P/'execution-v3/check_reports.py'),str(inp),'--output',str(out)],capture_output=True,text=True)
  result=json.loads(out.read_text());assert result['passed']==expectedpass
  tests.append({'test':name,'expected':expectedpass,'checker_accepted':result['passed'],'failed_checks':result['failures'],'expectation_met':True})
(D/'final-main-checks.json').write_text(json.dumps({'scope':'synthetic source-checker identity reachability; no backend call','verified_manifests':expected,'numerical_policy_request_checker_unchanged':True,'tests':tests},indent=2)+'\n')
print(json.dumps({'passed':True,'tests':len(tests),'all_final_manifest_bindings':True}))
