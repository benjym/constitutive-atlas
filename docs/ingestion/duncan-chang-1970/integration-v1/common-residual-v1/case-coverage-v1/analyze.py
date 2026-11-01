from pathlib import Path
import json,math,hashlib
p=Path(__file__).parent
assert not (p/'analysis.json').exists()
a=json.loads((p/'results.json').read_text());out=[]
for r in a['pairs']:
 if r.get('comparison_passed') is not False:continue
 tol=1e-7 if r['name'].startswith('legacy/') else 1e-10
 differences=[]
 def walk(n,w,path):
  if isinstance(w,bool) or w is None or isinstance(w,str):
   if n!=w:differences.append(dict(path=path,native=n,wasm=w,kind='non-numeric'))
  elif isinstance(w,(int,float)):
   relative=abs(n-w)/max(1,abs(n),abs(w))
   if relative>tol:differences.append(dict(path=path,native=n,wasm=w,scaled_difference=relative,kind='numeric'))
  elif isinstance(w,list):
   assert len(n)==len(w)
   for i,(v,z) in enumerate(zip(n,w)):walk(v,z,path+f'[{i}]')
  elif isinstance(w,dict):
   assert n.keys()==w.keys()
   for k in w:
    if k!='elapsed_ms':walk(n[k],w[k],path+'.'+k)
 walk(r['native'],r['wasm'],'result')
 out.append(dict(name=r['name'],tolerance=tol,outside_tolerance=differences))
(p/'analysis.json').write_text(json.dumps({'scope':'All original comparison fields examined without stopping at first mismatch; diagnostic only. Same normalized numeric predicates, no acceptance replacement.','pairs':len(a['pairs']),'status':a['status'],'failed_cases':out},indent=2)+'\n')
for r in out:
 from collections import Counter
 kinds=Counter(x['path'].split('].')[-1].split('[')[0] for x in r['outside_tolerance']);print(r['name'],len(r['outside_tolerance']),dict(kinds))
