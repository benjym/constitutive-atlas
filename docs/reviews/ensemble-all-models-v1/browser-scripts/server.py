from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
BASE=Path('/private/tmp/mc-current-shared-package-v3/site')
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  relative=path.split('?',1)[0].lstrip('/')
  if relative in ['ensemble.mjs','ensemble-view.mjs','ensemble-queue.mjs']:return str(ROOT/'web'/relative)
  return super().translate_path(path)
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE),**kwargs)
ThreadingHTTPServer(('127.0.0.1',58743),Handler).serve_forever()
