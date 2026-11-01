"""Historical saved-only assessor plumbing probe; never executes a solver."""
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
D=Path('/private/tmp/atlas-maxwell-current-v1/source')
rows=json.loads((ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/native-raw.json').read_text())
with tempfile.TemporaryDirectory(prefix='maxwell-saved-preset-') as tmp:
 dest=Path(tmp)
 for n,cid in [('relaxation','relaxation-schedule'),('creep','creep-schedule'),('oedometer','oedometer'),('load-hold-reverse','load-hold-reverse')]:
  d=json.loads(next(x for x in rows if x['id']==cid)['calls'][0]['stdout'])
  d['specification']=json.loads((D/'examples/maxwell'/f'{n}.json').read_text())
  (dest/f'{n}.json').write_text(json.dumps(d))
 subprocess.run([sys.executable,'-B',str(ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py'),str(D),str(dest)],check=True)
