from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
BASE=Path('/private/tmp/mc-current-shared-package-v3/site')
ROOT=Path('/Users/bmar5496/code/constitutive-atlas/web')
FILES={'ensemble.mjs','ensemble-view.mjs','ensemble-queue.mjs','ensemble-plots.mjs','ensemble.css','vendor/plotly-basic-4.1.1.min.js','vendor/plotly-LICENSE.txt','vendor/plotly-NOTICE.json'}
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  relative=path.split('?',1)[0].lstrip('/')
  return str(ROOT/relative) if relative in FILES else super().translate_path(path)
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE),**kwargs)
ThreadingHTTPServer(('127.0.0.1',58747),Handler).serve_forever()
