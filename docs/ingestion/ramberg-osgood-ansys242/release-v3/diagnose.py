import json,math,platform,sys
from pathlib import Path
from unittest.mock import patch
from tools.check_ramberg_osgood import make_requests
f=json.loads(Path('docs/ingestion/ramberg-osgood-ansys242/execution-v1/requests.json').read_text())
with patch('tools.check_ramberg_osgood.sum',math.fsum,create=True):q=make_requests()
d=[]
def walk(a,b,p=''):
 if isinstance(a,dict):
  for k in a:walk(a[k],b[k],p+'/'+k)
 elif isinstance(a,list):
  for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+'/'+str(i))
 elif a!=b:d.append({'path':p,'frozen':a,'regenerated':b,'ulp_error':abs(a-b)/max(math.ulp(a),math.ulp(b)) if isinstance(a,float) else None})
walk(f,q);print(json.dumps({'platform':platform.platform(),'python':sys.version,'differences':d},indent=2))
