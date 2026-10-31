"""Bind unchanged independent scalar axisymmetric mathematics to new controls."""
from pathlib import Path
import hashlib,json,sys
from axisymmetric import run
P=Path(__file__).resolve().parent
if __name__=='__main__':
 precision=int(sys.argv[1]);output=Path(sys.argv[2])
 if precision not in(280,360):raise ValueError('frozen precision pair')
 if output.exists():raise RuntimeError('preserve existing output')
 freeze=json.loads((P/'prospective-freeze.json').read_bytes())
 for name,digest in freeze['files'].items():
  if hashlib.sha256((P/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('frozen input/source changed '+name)
 inp=P/'source-input.json';data=json.loads(inp.read_bytes());res=run(data,precision)
 res.update(identity='mc-browser-loading-source-reference-v1',source_input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),loading_identity='linear-rne-v1 / cyclic-sine-rne12-v1')
 output.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'identity':res['identity'],'precision':precision,'paths':len(res['paths']),'points':sum(len(p['points'])for p in res['paths']),'candidate_calls':0,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
