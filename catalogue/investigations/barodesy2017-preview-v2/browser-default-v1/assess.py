from pathlib import Path
import json,math,hashlib
D=Path(__file__).resolve().parent

def assess(d=D):
 d=Path(d)
 for name,pin in json.loads((d/'manifest.json').read_text()).items():
  assert hashlib.sha256((d/name).read_bytes()).hexdigest()==pin,name
 req=json.loads((d/'request.json').read_text());responses={};errors=[];volume=0.;parity=0.
 def check(ok,message):
  if not ok:errors.append(message)
 for backend in ('native','wasm'):
  p=json.loads((d/(backend+'.stdout.txt')).read_text());responses[backend]=p
  check(p.get('ok')is True,backend+' status');points=p.get('points',[]);check(len(points)==101,backend+' points')
  check((d/(backend+'.stderr.txt')).read_bytes()==b'',backend+' stderr')
  for point in points:
   z=point['state'];e=point['strain'];v=z+e+[point[k]for k in ('p','q','q_signed','u','control')]
   check(len(z)==7 and len(e)==6 and all(type(x)in(int,float)and math.isfinite(x)for x in v),backend+' finite shape')
   check(point['p']>0 and z[6]>=0,backend+' domain')
   error=abs(z[6]-((1.8)*math.exp(-sum(e[:3]))-1));volume=max(volume,error);check(error<=1e-6,backend+' volume')
   check(abs(e[0]-point['control'])<=1e-7,backend+' axial control')
   check(abs((z[1]+z[2])/2-100000)<=.012,backend+' radial control')
 for n,w in zip(responses['native'].get('points',[]),responses['wasm'].get('points',[])):
  a=n['state']+n['strain']+[n[k]for k in ('p','q','q_signed','u','control')];b=w['state']+w['strain']+[w[k]for k in ('p','q','q_signed','u','control')]
  for x,y in zip(a,b):
   error=abs(x-y)/max(1.,abs(x),abs(y));parity=max(parity,error);check(error<=1e-10,'backend channel parity')
 return {'pass':not errors,'errors':errors,'maximum_void_error':volume,'maximum_scaled_backend_difference':parity,'points_per_backend':101,'rendered_browser_qa':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(assess(),indent=2))
