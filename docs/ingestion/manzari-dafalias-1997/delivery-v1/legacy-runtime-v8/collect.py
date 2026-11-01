"""Transport-only additive collector; actual calls remain coordinator-owned."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse,json,subprocess,sys
from frozen_logic import D,P,sha,frozen,load,ordinary_hook_source


def audited_factory(original):
 class Audited(original):
  def __init__(self,args,out):
   self.args=args;self.out=out;self.worker=None;self.calls=0
   self.audit={'identity':'md1997-legacy-raw-transport-v8','backend':'wasm'if args.wasm_engine else 'native','artifact_path':str(Path(args.wasm_engine or args.solver).resolve()),'artifact_sha256':sha(args.wasm_engine or args.solver),'original_call_sha256':sha(P/'execution-v3/run_native.py'),'collector_sha256':sha(D/'collect.py'),'worker':None,'closed':False}
   self.save()
   if args.wasm_engine:
    command=['node',str(self.worker_script()),'--worker','--engine',str(Path(args.wasm_engine).resolve())]
    stderr=out/'worker-stderr.txt'
    self.worker=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr.open('w'),text=True,bufsize=1)
    self.audit['worker']={'command':command,'pid':self.worker.pid,'ready_wire':self.worker.stdout.readline(),'exit_code':None,'stderr_path':str(stderr.resolve())};self.save()
    try:assert json.loads(self.audit['worker']['ready_wire'])=={'ready':True},'worker handshake'
    except BaseException:
     self.close();raise
  def worker_script(self):
   # Ordinary transport imports execution-v3; MD imports execution-v3.
   return P/('execution-v3/run_wasm.mjs'if self.study=='ordinary'else 'execution-v3/run_wasm.mjs')
  def save(self):(self.out/'transport.json').write_text(json.dumps(self.audit,indent=2)+'\n')
  def close(self):
   if self.audit['closed']:return
   try:
    if self.worker:
     self.worker.stdin.close();self.audit['worker']['exit_code']=self.worker.wait(timeout=30)
   finally:
    if self.worker:
     stderr=Path(self.audit['worker']['stderr_path']);self.audit['worker']['stderr_sha256']=sha(stderr)
    self.audit.update(closed=True,call_count=self.calls);self.save()
   if self.worker:assert self.audit['worker']['exit_code']==0,'worker transport exit'
 Audited.call=original.call # exactly original request serialization/process execution
 Audited.study=STUDY
 return Audited


def main():
 global STUDY
 parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--study',choices=['legacy-md','ordinary'],required=True);known,remaining=parser.parse_known_args();STUDY=known.study
 frozen()
 for name,digest in json.loads((D/'manifest.json').read_text()).items():assert sha(D/name)==digest,'collector drift: '+name
 sys.argv=[str(D/'collect.py')]+remaining
 if STUDY=='legacy-md':
  module=load('execution-v3/run_native.py');module.Backend=audited_factory(module.Backend);module.main()
 else:
  namespace={'__name__':'ordinary_transport_hook','__file__':str(P/'ordinary-regression-v7/run.py'),'audited_factory':audited_factory}
  exec(ordinary_hook_source(),namespace);namespace['main']()
if __name__=='__main__':main()
