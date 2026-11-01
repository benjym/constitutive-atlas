from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import time,os
base=Path('/private/tmp/barodesy2017-description-context-v1')
os.chdir(base/'site')
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path.split('?')[0]=='/evidence.json':
   (base/'evidence-requested').write_text(self.path)
   deadline=time.monotonic()+180
   while not (base/'release-evidence').exists() and time.monotonic()<deadline: time.sleep(.1)
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',8896),Handler).serve_forever()
