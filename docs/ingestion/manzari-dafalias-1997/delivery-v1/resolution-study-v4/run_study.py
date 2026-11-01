"""Coordinator-owned execution with explicit current source binding."""
import argparse,json,subprocess,sys
from pathlib import Path
from preflight import D,check,sha
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--solver');g.add_argument('--wasm-engine');p.add_argument('--output',required=True);p.add_argument('--case',action='append',default=[]);a=p.parse_args();binding=check();out=Path(a.output).resolve();assert not out.exists(),'preserve all prior evidence'
cmd=[sys.executable,'-B',str(D/'run_native.py'),'--wasm-engine' if a.wasm_engine else '--solver',a.wasm_engine or a.solver,'--output',str(out)]
for c in a.case:cmd+=['--case',c]
binding.update(backend='wasm' if a.wasm_engine else 'native',artifact_path=str(Path(a.wasm_engine or a.solver).resolve()),artifact_sha256=sha(a.wasm_engine or a.solver),delegate_command=cmd,subset=a.case)
r=subprocess.run(cmd)
if out.exists():
 binding['delegate_returncode']=r.returncode
 if (out/'report.json').is_file():binding['report_sha256']=sha(out/'report.json')
 (out/'runtime-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
raise SystemExit(r.returncode)
