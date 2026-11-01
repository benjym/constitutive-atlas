from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[4];p=Path(__file__).parent;b=Path('/private/tmp/atlas-duncan-integration-v2');src=Path('/private/tmp/atlas-common-scalar-functions-v1/actual-root-wasm-v1');dest=b/'site-v1'
cmd=['python3','-B','tools/build_web.py','--wasm-dir',str(src),'--output',str(dest),'--burgers-wasm-dir',str(b/'retained-inputs/burgers'),'--power-creep-wasm-dir',str(b/'retained-inputs/power-creep'),'--sls-wasm-dir',str(b/'retained-inputs/sls'),'--j2-wasm-dir',str(b/'retained-inputs/j2'),'--maxwell-wasm-dir',str(b/'current-inputs/maxwell'),'--controlled-path-wasm-dir',str(b/'current-inputs/norsand')]
# Freeze actual inputs after accepted packager installation, before package call.
assert (r/'docs/reviews/common-scalar-functions-v1/package-installed-v1.json').is_file()
paths=set()
for directory in ['web','tools','atlas','models','schemas','catalogue']:
 for f in (r/directory).rglob('*'):
  if f.is_file() and f.suffix in ['.py','.mjs','.js','.json','.html','.css'] and '__pycache__' not in f.parts and 'source-snapshots' not in f.parts:paths.add(f)
paths.add(r/'cpp/scalar-functions/NOTICES.txt')
for root in [b/'retained-inputs',b/'current-inputs']:
 paths.update(f for f in root.rglob('*') if f.is_file())
paths.update([src/'atlas.js',src/'atlas.wasm',src/'generated/models.json'])
files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(paths)}
(p/'package-source-freeze-v1.json').write_text(json.dumps({'status':'Prospective before standardpackageobservations','command':cmd,'files':files,'source_catalogue_sha256':'38f03e0099cfee9c89deaa59e729ac43563d4d39b17d321721a199e58d3b77d4','acceptance':'Existing standardbuilder complete package + unchanged supportedpackage, strict-default expectedpolicy, database/presets and actualbrowser checks; no modelomission or numericalgatechange'},indent=2)+'\n');print(len(files),'source and artifact pins frozen before packaging')
