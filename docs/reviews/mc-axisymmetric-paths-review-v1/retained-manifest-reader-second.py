"""Portable source-only replay. Does not import Atlas or execute compiled artifacts."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil

def run(packet):
 packet=Path(packet).resolve();tmp=Path(tempfile.mkdtemp(prefix='mc-axisymmetric-reference-replay-'));print(tmp,flush=True)
 shutil.copytree(packet,tmp,dirs_exist_ok=True)
 manifest=json.loads((tmp/'manifest.json').read_text())
 for rel,pin in manifest['files'].items():assert hashlib.sha256((tmp/rel).read_bytes()).hexdigest()==pin,rel
 for name in ('pre-generation-source-freeze.json','prospective-freeze.json'):
  freeze=json.loads((tmp/name).read_text())
  for rel,pin in freeze['files'].items():assert hashlib.sha256((tmp/rel).read_bytes()).hexdigest()==pin,(name,rel)
 steps=[]
 def call(label,args):
  p=subprocess.run([sys.executable,'-B',*args],cwd=tmp,capture_output=True)
  (tmp/(label+'.replay.stdout')).write_bytes(p.stdout);(tmp/(label+'.replay.stderr')).write_bytes(p.stderr)
  assert p.returncode==0,(label,p.returncode,tmp)
  steps.append(label)
 for precision in (280,360):
  output=f'regenerated-p{precision}.json';call(str(precision),['axisymmetric.py','source-input.json',str(precision),output])
  assert (tmp/output).read_bytes()==(tmp/f'reference-p{precision}.json').read_bytes(),precision
 call('check',['check.py','regenerated-p280.json','regenerated-p360.json','reference-policy.json'])
 assert json.loads((tmp/'check.replay.stdout').read_bytes())==json.loads((tmp/'check-results.json').read_bytes())
 call('algebra',['check_algebra.py'])
 assert json.loads((tmp/'algebra.replay.stdout').read_bytes())==json.loads((tmp/'algebra-results.json').read_bytes())
 call('adequacy',['check_adequacy.py'])
 assert (tmp/'adequacy-results.json').read_bytes()==(packet/'adequacy-results.json').read_bytes()
 result={'passed':True,'reference_files_byte_equal':2,'precision_fields':json.loads((tmp/'check-results.json').read_bytes())['numeric_fields'],'source_only':True,'candidate_calls':0,'compiled_observations':0,'steps':steps}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':run(sys.argv[1]if len(sys.argv)>1 else Path(__file__).resolve().parent)
