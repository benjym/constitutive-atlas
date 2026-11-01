"""Coordinator execution wrapper; unchanged delegated requests and gates."""
from pathlib import Path
import argparse,json,subprocess,sys
from preflight import D,P,check,sha,build_binding

def main(study):
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--solver');g.add_argument('--wasm-engine');p.add_argument('--build-receipt',required=True);p.add_argument('--output',required=True);p.add_argument('--case',action='append',default=[]);a=p.parse_args();binding=check();backend='wasm' if a.wasm_engine else 'native';artifact=a.wasm_engine or a.solver;binding.update(build_binding(a.build_receipt,backend,artifact));out=Path(a.output).resolve();assert not out.exists(),'preserve prior evidence'
 if study=='md':delegate=P/'resolution-study-v4/run_native.py';subset=a.case
 elif study=='ordinary':delegate=P/'ordinary-regression-v7/run.py';assert not a.case,'all16 ordinary cases required';subset=[]
 else:
  assert study=='coarse' and not a.case,'coarse diagnostic has one frozen request'
  delegate=P/'execution-v3/run_native.py';subset=[json.loads((D/'coarse-diagnostic-policy.json').read_text())['case']['id']]
 command=[sys.executable,'-B',str(delegate),'--wasm-engine' if a.wasm_engine else '--solver',str(Path(artifact).resolve()),'--output',str(out)]
 for c in subset:command+=['--case',c]
 binding.update(study=study,delegate_path=str(delegate),delegate_sha256=sha(delegate),delegate_command=command,subset=subset)
 status=None
 try:status=subprocess.run(command).returncode
 finally:
  if out.exists():
   binding['delegate_returncode']=status
   if (out/'report.json').is_file():binding['report_sha256']=sha(out/'report.json')
   receipt=Path(a.build_receipt).resolve();(out/'coordinator-build-receipt.json').write_bytes(receipt.read_bytes());assert sha(out/'coordinator-build-receipt.json')==binding['coordinator_build_receipt_sha256'],'external receipt drift'
   (out/'runtime-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
 raise SystemExit(status)
