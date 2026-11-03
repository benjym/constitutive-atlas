from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
BASE=Path('/private/tmp/mc-current-shared-package-v3/site')
ROOT=Path('/Users/bmar5496/code/constitutive-atlas/web')
ASSETS=Path('/private/tmp/atlas-ensemble-all-tests-v1/assets')
FILES={'ensemble.mjs','ensemble-view.mjs','ensemble-queue.mjs','ensemble-plots.mjs','ensemble-experiments.mjs','ensemble.css'}
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  relative=path.split('?',1)[0].lstrip('/')
  if relative in FILES:return str(ROOT/relative)
  if relative in {'ensemble-tests.json','ensemble-index.json','ensemble-experiment.json'} or relative.startswith(('ensemble-tests/','vendor/plotly-')):return str(ASSETS/relative)
  return super().translate_path(path)
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE),**kwargs)
ThreadingHTTPServer(('127.0.0.1',58749),Handler).serve_forever()
