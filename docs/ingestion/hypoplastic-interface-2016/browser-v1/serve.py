"""Serve only the final public package under the actual project-path prefix."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,os
P=Path(__file__).resolve().parent
site=Path('/private/tmp/atlas-interface2016-delivery-v1/site-v2')
assert (site/'material-point-interface2016/engine-path/package-manifest.json').is_file()
root=site.parent/'http-root-v1';root.mkdir(exist_ok=True);link=root/'constitutive-atlas'
if not link.exists():link.symlink_to(site,target_is_directory=True)
assert link.is_symlink() and link.resolve()==site.resolve() and set(p.name for p in root.iterdir())=={'constitutive-atlas'}
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
record=dict(pid=os.getpid(),port=server.server_port,url=f'http://127.0.0.1:{server.server_port}/constitutive-atlas/index.html',site=str(site),served_root=str(root),owner='MODEL-hypoplastic-interface-2016',status='running')
(P/'server.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
try:server.serve_forever()
finally:server.server_close()
