"""Coordinator execution wrapper; unchanged delegated requests and gates."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse,json,subprocess,sys
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'runtime-rebind-v5'))
from preflight import P,check,sha,build_binding
D=Path(__file__).resolve().parent

def main(study):
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--solver');g.add_argument('--wasm-engine');p.add_argument('--build-receipt',required=True);p.add_argument('--output',required=True);p.add_argument('--case',action='append',default=[]);a=p.parse_args();binding=check();backend='wasm' if a.wasm_engine else 'native';artifact=a.wasm_engine or a.solver;binding.update(build_binding(a.build_receipt,backend,artifact));out=Path(a.output).resolve();assert not out.exists(),'preserve prior evidence'
 assert study in ['md','ordinary'] and not a.case,'full unchanged study required'
 original=P/('resolution-study-v4/run_native.py'if study=='md'else 'ordinary-regression-v7/run.py');delegate=D/'collect.py'
 command=[sys.executable,'-B',str(delegate),'--study',study,'--wasm-engine'if a.wasm_engine else '--solver',str(Path(artifact).resolve()),'--output',str(out)]
 binding.update(identity='md1997-raw-link-runtime-binding-v7',study=study,delegate_path=str(delegate),delegate_sha256=sha(delegate),delegate_command=command,subset=[],original_harness_path=str(original),original_harness_sha256=sha(original),raw_link_manifest_sha256=sha(D/'manifest.json'),v5_preflight_identity=binding['identity'])
 status=None
 try:status=subprocess.run(command).returncode
 finally:
  if out.exists():
   binding['delegate_returncode']=status
   if (out/'report.json').is_file():binding['report_sha256']=sha(out/'report.json')
   receipt=Path(a.build_receipt).resolve();(out/'coordinator-build-receipt.json').write_bytes(receipt.read_bytes());assert sha(out/'coordinator-build-receipt.json')==binding['coordinator_build_receipt_sha256'],'external receipt drift'
   (out/'runtime-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
 raise SystemExit(status)

if __name__=='__main__':
 if len(sys.argv)<2 or sys.argv[1] not in ['md','ordinary']:raise SystemExit('first argument: md or ordinary')
 study=sys.argv.pop(1);main(study)
