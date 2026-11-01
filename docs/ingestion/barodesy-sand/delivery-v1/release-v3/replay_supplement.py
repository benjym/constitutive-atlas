"""Replay literal prospectively frozen transaction requests on current artifacts."""
from pathlib import Path
import json, subprocess, struct, hashlib
HERE=Path(__file__).resolve().parent; PARENT=HERE.parent
native='/private/tmp/atlas-ramberg-osgood-delivery-v1/build-ramberg-native/atlas_solver'
wasm='/private/tmp/atlas-ramberg-osgood-delivery-v1/build-ramberg-wasm/atlas.js'
original=json.loads((PARENT/'transaction-supplement-v1/native-journal.json').read_text())
bits=lambda xs:b''.join(struct.pack('d',v) for v in xs)
reports={}
for backend in ['native','wasm']:
 process=subprocess.Popen(['node',str(PARENT/'wasm-transport.mjs'),wasm],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True) if backend=='wasm' else None
 rows=[]
 for row in original:
  q=row['request']
  if process:
   process.stdin.write(json.dumps(q)+'\n');process.stdin.flush();raw=json.loads(process.stdout.readline())['raw']
  else:
   cmd=[native,'--mode','integrate','--model',q['model'],'--parameters',q['parameters'],'--initial',q['initial'],'--strain',q['strain'],'--integration-settings',q['settings']]
   raw=subprocess.run(cmd,capture_output=True,text=True,check=False).stdout
  rows.append({'id':row['id'],'request':q,'raw':raw});(HERE/(backend+'-supplement.json')).write_text(json.dumps(rows,indent=2)+'\n')
 if process:process.stdin.close();process.wait()
 a,f,b,z=[json.loads(r['raw']) for r in rows];parent=[100000.,100000.,100000.,0.,0.,0.,.75]
 assert a['ok'] and b['ok'] and z['ok'] and not f['ok']
 assert bits(a['state'])==bits(b['state']) and bits(z['state'])==bits(parent) and bits(f['state'])==bits(parent)
 assert f['diagnostics']['attempted_substeps']>0 and f['diagnostics']['discarded_substeps']==f['diagnostics']['attempted_substeps']
 reports[backend]={'pass':True,'calls':len(rows),'failure_diagnostics':f['diagnostics']}
(HERE/'supplement-assessment.json').write_text(json.dumps(reports,indent=2)+'\n')
