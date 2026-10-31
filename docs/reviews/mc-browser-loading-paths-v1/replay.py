"""Portable independent source replay, never production backend execution."""
from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,shutil
P=Path(__file__).resolve().parent
freeze=json.loads((P/'prospective-freeze.json').read_bytes())
report=[]
with tempfile.TemporaryDirectory(prefix='atlas-browser-source-replay-')as tmp:
 t=Path(tmp)
 for name,digest in freeze['files'].items():
  source=P/name
  if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise RuntimeError('source changed '+name)
  q=t/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(source.read_bytes())
 shutil.copyfile(P/'prospective-freeze.json',t/'prospective-freeze.json')
 expected=(t/'source-input.json').read_bytes();(t/'source-input.json').unlink()
 commands=[[sys.executable,'-B',str(t/'prepare_inputs.py')]]+[[sys.executable,'-B',str(t/'generate_reference.py'),str(n),str(t/f'reference-p{n}.json')]for n in(280,360)]
 for argv in commands:
  r=subprocess.run(argv,cwd=t,text=True,capture_output=True);report.append({'argv':['python3','-B']+argv[2:],'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
  if r.returncode:raise RuntimeError(report[-1])
 if (t/'source-input.json').read_bytes()!=expected:raise RuntimeError('input replay mismatch')
 for n in(280,360):
  if (t/f'reference-p{n}.json').read_bytes()!=(P/f'reference-p{n}.json').read_bytes():raise RuntimeError('precision replay mismatch '+str(n))
result={'identity':'mc-browser-loading-portable-source-replay-v1','passed':True,'input_byte_exact':True,'reference_precisions_byte_exact':[280,360],'commands':report,'candidate_calls':0,'compiled_observations':0}
(P/'replay-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='commands'}))
