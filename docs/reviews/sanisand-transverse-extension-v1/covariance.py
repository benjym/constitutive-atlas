"""Freeze and assess proper-rotation covariance of actual generated residual/Jets."""
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
NATIVE=ROOT/'docs/reviews/sanisand-v03-monotonic-v1/native-results'

def load(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rot6(v):return [v[0],v[2],v[1],-v[5],v[4],-v[3]]
def rotate(v):
 if len(v)==6:return rot6(v)
 r=v.copy()
 for offset in [0,7,13,19]:r[offset:offset+6]=rot6(v[offset:offset+6])
 return r

def prepare():
 index=load(NATIVE/'index.json');requests=[];parents=[]
 for item in index['records']:
  if not item['id'].startswith('extension-') or '-p20000/' not in item['id']:continue
  path=NATIVE/item['file'];assert sha(path)==item['sha256'];receipt=load(path);response=receipt['response'];points=response['points']
  first=next((i for i,p in enumerate(points) if abs(p['state'][1]-p['state'][2])>1e-3),None)
  indices=sorted({1,(len(points)-1)//4,len(points)-1}|({first-1,first} if first and first>1 else set()))
  parameters=[float(v) for v in receipt['request']['args'][1].split(',')]
  for point in indices:
   z=points[point]['state'];zn=points[point-1]['state'];de=[a-b for a,b in zip(points[point]['strain'],points[point-1]['strain'])]
   identity=item['id']+f'/point{point}';parents.append({'id':identity,'incoming':zn,'current':z,'increment':de})
   for column in range(58):
    seed=[0.]*58;local=column%26 if column<52 else column-52
    seed[column]=(100000. if local<6 else 1.) if column<52 else .01
    for rotated in [False,True]:
     x=rotate(z) if rotated else z;xn=rotate(zn) if rotated else zn;d=rotate(de) if rotated else de
     zs=rotate(seed[:26]) if rotated else seed[:26];ns=rotate(seed[26:52]) if rotated else seed[26:52];ds=rotate(seed[52:]) if rotated else seed[52:]
     requests.append({'id':identity,'column':column,'rotated':rotated,'wire':parameters+x+xn+d+zs+ns+ds})
 return {'state_layout':26,'seed_columns':58,'parents':parents,'requests':requests}


def assess(requests,responses):
 assert len(requests['requests'])==len(responses)
 worst_value=worst_derivative=0.;checks=0;rows=[]
 for i in range(0,len(responses),2):
  a,b=responses[i:i+2];r=requests['requests'][i]
  assert a['ok'] is True and b['ok'] is True
  for name in ['values','directional']:
   assert len(a[name])==len(b[name])==26
   assert all(type(x) in (int,float) and math.isfinite(x) for x in a[name]+b[name])
   rotated=rotate(a[name]);differences=[abs(x-y)/(100000. if j<6 else 1.)/max(1,abs(x)/(100000. if j<6 else 1.),abs(y)/(100000. if j<6 else 1.)) for j,(x,y) in enumerate(zip(rotated,b[name]))]
   error=max(differences)
   if name=='values':worst_value=max(worst_value,error)
   else:worst_derivative=max(worst_derivative,error)
   assert error<=1e-8, (r['id'],r['column'],name,error)
   checks+=26
 return {'proper_rotation_covariance_pass':True,'states':len(requests['parents']),'directions_per_state':58,'compiled_requests':len(responses),'value_and_derivative_components':checks,
         'maximum_scaled_value_difference':worst_value,'maximum_scaled_derivative_difference':worst_derivative,
         'candidate_integrations':0,'scope':'Actual endpoints/incoming states/increments; current26/parent26/loading6 real Jet seed directions, proper-rotation covariance only. Not independent derivative correctness, Newton path or full-update tangent qualification.'}


if __name__=='__main__':
 if sys.argv[1]=='prepare':
  data=prepare();out=Path(sys.argv[2]);out.write_bytes(gzip.compress((json.dumps(data,indent=2)+'\n').encode(),mtime=0))
  print(len(data['parents']),len(data['requests']))
 else:
  requests=load(HERE/'covariance-requests.json.gz');responses=[json.loads(line) for line in Path(sys.argv[2]).read_text().splitlines()]
  print(json.dumps(assess(requests,responses),indent=2))
