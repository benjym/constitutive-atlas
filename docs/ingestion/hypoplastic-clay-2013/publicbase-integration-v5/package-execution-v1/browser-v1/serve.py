from pathlib import Path
import argparse,json,hashlib,datetime,mimetypes
from http.server import HTTPServer,BaseHTTPRequestHandler
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;plan=json.loads((here/'PLAN.json').read_bytes());site=Path(plan['site'])
manifest=json.loads((here.parent/'PACKAGE_MANIFEST.json').read_bytes())['files']
sha=lambda b:hashlib.sha256(b).hexdigest()
for n,item in manifest.items():
 if sha((site/n).read_bytes())!=item['sha256']:raise ValueError('changed sealed asset '+n)
plan=json.loads((here/'PLAN.json').read_bytes());prefix=plan['url_prefix']
journal=here/'responses.jsonl'
if journal.exists():raise ValueError('new trace identity required')
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  name=self.path.split('?',1)[0]
  if name in (prefix,prefix+'index.html'):rel='index.html'
  elif name.startswith(prefix):rel=name[len(prefix):]
  else:self.send_error(404);return
  # Serve only exact sealed relative paths; no directory listing or external files.
  if rel not in manifest:self.send_error(404);return
  body=(site/rel).read_bytes();h=sha(body)
  if h!=manifest[rel]['sha256']:self.send_error(409,'sealed asset changed');return
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(rel)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('Pragma','no-cache');self.send_header('X-Atlas-Asset-SHA256',h);self.end_headers()
  sent=self.wfile.write(body);self.wfile.flush()
  row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET','path':name,'relative_path':rel,'status':200,'body_sha256':h,'body_bytes':len(body),'write_returned_bytes':sent,'content_length':len(body),'write_completed':True,'cache_control':'no-store','request_if_none_match':self.headers.get('If-None-Match'),'request_if_modified_since':self.headers.get('If-Modified-Since'),'user_agent':self.headers.get('User-Agent'),'referer':self.headers.get('Referer')}
  with journal.open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
 def log_message(self,*args):pass
server=HTTPServer(('127.0.0.1',a.port),Handler)
startup={'identity':'clay2013-currentpublic-v4-browser-delivery','port':server.server_port,'url':'http://127.0.0.1:'+str(server.server_port)+prefix+'#laboratory?model=hypoplastic-clay-2013','sealed_assets':len(manifest),'scope':'Actual browser only; fresh nonce/no-store/full200delivery. No CLI probes, private sources or browser cache/CPU attestation.'}
(here/'STARTUP.json').write_text(json.dumps(startup,indent=2)+'\n')
print(json.dumps(startup),flush=True)
server.serve_forever()
