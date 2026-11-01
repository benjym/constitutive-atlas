import json
import sys
import subprocess
from pathlib import Path
import numpy as np
from reference import augmented_state,initial,matrix
P=Path(__file__).resolve().parent
if (P/'laboratory-responses.json.gz').exists():raise RuntimeError('Retained study exists; use a fresh study directory for recapture.')
binary=sys.argv[1]
z=augmented_state(initial());csv=lambda v:','.join(map(str,v))
rows=[];failed=[]
for protocol in range(5):
 target=5000 if protocol==3 else .01
 cmd=[binary,'--model','nakai-hinokio-2004-clay-appendix-v-be','--mode','run','--initial',csv(z),'--protocol',str(protocol),'--target',str(target),'--steps','100','--integration-settings','2e-10,1e-6,45,14,20000,11']
 out=subprocess.run(cmd,capture_output=True,text=True,timeout=55);r=json.loads(out.stdout);rows.append(r)
 errors=[]
 if not r['ok'] or len(r.get('points',[]))!=101:errors.append('success/point count')
 for point in r.get('points',[]):
  state=point['state'];strain=point['strain']
  if not all(np.isfinite(state)) or min(np.linalg.eigvalsh(matrix(state[:6])))<=0:errors.append('finite/SPD')
  if abs(state[7]-(.83-1.83*sum(strain[:3])))>1e-8:errors.append('void closure')
  if protocol==1 and abs((state[1]+state[2])/2-98000)>.01:errors.append('radial stress')
  if protocol in [2,3] and abs(sum(strain[:3]))>1e-9:errors.append('volume control')
 if protocol==3 and r['ok'] and abs(r['points'][-1]['q_signed']-5000)>.01:errors.append('stress control')
 if errors:failed.append({'protocol':protocol,'errors':sorted(set(errors))})
 print(protocol,r['ok'],len(r.get('points',[])),sorted(set(errors)),flush=True)
(P/'laboratory-responses.json').write_text(json.dumps(rows,indent=2)+'\n')
(P/'laboratory-report.json').write_text(json.dumps({'status':'pass' if not failed else 'failed','failures':failed,'protocol_count':5},indent=2)+'\n')
raise SystemExit(bool(failed))
