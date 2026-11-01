"""Actual artifact metadata for pre-review preset tests. Never an approval receipt."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('build',type=Path);p.add_argument('output',type=Path);a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(a.source.resolve())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();model=a.source/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json';m=json.loads(model.read_text());catalogue=json.loads((a.build/'generated/models.json').read_text());assert catalogue['models']==[m];assert catalogue['sha256']==hashlib.sha256(json.dumps([m],sort_keys=True,separators=(',',':')).encode()).hexdigest();assert m['id']=='maxwell-itasca900-zero-spin-ode'
identity={'model':m['id'],'model_sha256':sha(model),'catalogue_hash':catalogue['sha256'],'module_sha256':sha(a.build/'maxwell.js'),'wasm_sha256':sha(a.build/'maxwell.wasm'),'scope':'Unreviewed actual-artifact metadata for raw preset/replay tests only; not build qualification, review, admission or package identity.'}
a.output.write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity))
