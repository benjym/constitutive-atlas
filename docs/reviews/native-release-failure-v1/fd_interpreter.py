import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/Users/bmar5496/code/constitutive-atlas')
from atlas.model import load,evaluation_environment,defaults
from atlas.dsl import parse,evaluate
root=Path('/Users/bmar5496/code/constitutive-atlas');rows=[]
for path in sorted((root/'models').glob('*.json')):
 m=load(path);p=defaults(m);zn={f['name']:copy.deepcopy(f['initial']) for f in m['state']};z=copy.deepcopy(zn);z['sigma'][:4]=[110000,95000,100000,500]
 for f in m['state']:
  if f.get('multiplier'):z[f['name']]=.0001
  if f['name']=='h':z['h'][:2]=[.00002,-.00001]
 env=evaluation_environment(m,z,zn,[.00001,-.000005,-.000005,.000003,0,0],_check_domain=False)
 scales=[]
 for f in m['state']:
  scale=evaluate(parse(f['scale']),env);scales.extend([(f['name'],j if f.get('shape')=='sym' else None,scale)for j in range(6 if f.get('shape')=='sym' else 1)])
 probes=[]
 for name,j,scale in scales:
  for sign in [-1,1]:
   trial=copy.deepcopy(z)
   if j is None:trial[name]+=sign*1e-6*scale
   else:trial[name][j]+=sign*1e-6*scale
   try:
    e=evaluation_environment(m,trial,zn,[.00001,-.000005,-.000005,.000003,0,0],_check_domain=False)
    failed=[c for c in m['domain']if not evaluate(parse(c),e)]
    if failed:probes.append({'field':name,'component':j,'sign':sign,'value':trial[name],'failed_domain':failed})
   except Exception as exc:probes.append({'field':name,'component':j,'sign':sign,'error':str(exc)})
 rows.append({'model':m['id'],'components':len(scales),'invalid_fd_probes':probes})
print(json.dumps(rows,indent=2))
