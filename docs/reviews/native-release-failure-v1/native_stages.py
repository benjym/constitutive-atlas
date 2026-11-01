import json,subprocess,math,hashlib
from pathlib import Path
r=Path('/Users/bmar5496/code/constitutive-atlas');solver='/private/tmp/atlas-mc-execution-v3/native/build/atlas_solver';m=json.loads((r/'models/research-hp-extracted-asbs-gis-2024-v03.json').read_text());initial=sum([f['initial']if isinstance(f['initial'],list)else[f['initial']]for f in m['state']],[]);params=','.join(str(p['default'])for p in m['parameters'].values());de=[.0002,-.00004,-.00004,.00003,0,0];calls=[];rows=[]
out=Path('/private/tmp/atlas-release-profile-v1/native-stages.json')
def evaluate(z,previous,inc,label):
 argv=[solver,'--mode','evaluate','--model',m['id'],'--parameters',params,'--current',','.join(map(str,z)),'--initial',','.join(map(str,previous)),'--strain',','.join(map(str,inc))];p=subprocess.run(argv,capture_output=True,text=True,timeout=30);row={'label':label,'argv':argv,'status':p.returncode,'stdout':p.stdout,'stderr':p.stderr};calls.append(row);out.write_text(json.dumps({'rows':rows,'calls':calls}));assert not p.stderr;body=json.loads(p.stdout);assert p.returncode==(0 if body['ok']else 1);return body
for depth in range(15):
 row={'depth':depth,'midpoints':[]};rows.append(row)
 def midpoint(z,inc,label,defect):
  rec={'label':label};row['midpoints'].append(rec)
  a=evaluate(z,z,inc,label+'/k1');rec['k1_ok']=a['ok']
  if not a['ok']:return None
  mid=[u+.5*v for u,v in zip(z,a['values'])];b=evaluate(mid,z,inc,label+'/k2');rec.update(mid=mid,k2_ok=b['ok'])
  if not b['ok']:return None
  end=[u+v for u,v in zip(z,b['values'])];c=evaluate(end,end,[0]*6,label+'/domain');rec.update(end=end,domain_ok=c['ok'])
  if not c['ok']:return None
  if defect:
   e=evaluate(end,z,inc,label+'/k3');rec['k3_ok']=e['ok']
   if not e['ok']:return None
   rec['defect']=[(u-2*v+w)/6 for u,v,w in zip(a['values'],b['values'],e['values'])]
  return end
 inc=[math.ldexp(v,-depth)for v in de];full=midpoint(initial,inc,f'{depth}/full',False)
 if full is not None:
  half=midpoint(initial,[.5*v for v in inc],f'{depth}/half',True)
  if half is not None:two=midpoint(half,[.5*v for v in inc],f'{depth}/two',True)
out.write_text(json.dumps({'rows':rows,'calls':calls},indent=2)+'\n')
print(json.dumps([{'depth':x['depth'],'stages':[{k:v for k,v in y.items()if k.endswith('_ok')or k=='label'}for y in x['midpoints']]}for x in rows],indent=2))
