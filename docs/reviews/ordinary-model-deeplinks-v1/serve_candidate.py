from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from urllib.parse import urlsplit
from pathlib import Path
ROOT=Path('/private/tmp/atlas-deeplink-candidate-v1')
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if not self.path.startswith('/constitutive-atlas/'):self.send_error(404);return
  self.path=self.path[len('/constitutive-atlas'):];super().do_GET()
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',18786),partial(Handler,directory=str(ROOT))).serve_forever()
