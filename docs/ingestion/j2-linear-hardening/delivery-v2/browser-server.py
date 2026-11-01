from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import json,time,hashlib
ROOT=Path('/private/tmp/atlas-j2-main-v2/site-r3')
CONFIG=Path('/private/tmp/atlas-j2-main-v2/server-config.json')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def do_GET(self):
  path=urlsplit(self.path).path
  if not path.startswith('/constitutive-atlas/'):
   self.send_error(404);return
  self.path=self.path[len('/constitutive-atlas'):]
  config=json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
  if path.endswith(config.get('delay_asset','disabled')):time.sleep(config.get('delay_s',0))
  if config.get('descriptor_mismatch') and path.endswith(('/identity.json','/models.json')) and '/material-point-j2/'in path:
   data=json.loads((ROOT/self.path.lstrip('/').split('?')[0]).read_text())
   if path.endswith('/models.json'):data['sha256']='0'*64
   else:
    data['catalogue_hash']='0'*64
    cat=json.loads((ROOT/'material-point-j2/models.json').read_text());cat['sha256']='0'*64
    data['catalogue_sha256']=hashlib.sha256((json.dumps(cat,indent=2)+'\n').encode()).hexdigest()
   raw=(json.dumps(data,indent=2)+'\n').encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw);return
  super().do_GET()
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);print(server.server_address[1],flush=True);server.serve_forever()
