from pathlib import Path
import json,subprocess,hashlib
out=Path(__file__).resolve().parent;revision='89047fc6a65865388b0d1b6089083f7f14960475'
expected={41728007865:3,41728007969:6,41728008184:1,41728841056:2};runs=[]
for rid,count in expected.items():
 raw=subprocess.check_output(['gh','run','view',str(rid),'--json','status,conclusion,headSha,jobs,url,createdAt,updatedAt']);d=json.loads(raw)
 assert d['headSha']==revision and d['status']=='completed' and d['conclusion']=='success',(rid,d['status'],d['conclusion'])
 assert len(d['jobs'])==count and all(j['status']=='completed' and j['conclusion']=='success' for j in d['jobs'])
 p=out/f'final-run-{rid}-success-v2.json';assert not p.exists();p.write_bytes(raw);runs.append({'run':rid,'jobs':count,'url':d['url'],'report':p.name,'sha256':hashlib.sha256(raw).hexdigest()})
raw=subprocess.check_output(['gh','api','repos/benjym/constitutive-atlas/deployments/7532325589']);d=json.loads(raw);assert d['sha']==revision and d['environment']=='github-pages'
p=out/'final-deployment-identity-v2.json';assert not p.exists();p.write_bytes(raw)
raw=subprocess.check_output(['gh','api','repos/benjym/constitutive-atlas/deployments/7532325589/statuses']);statuses=json.loads(raw);assert statuses[0]['state']=='success' and statuses[0]['environment_url']=='https://benjym.github.io/constitutive-atlas/'
p=out/'final-deployment-status-v2.json';assert not p.exists();p.write_bytes(raw)
report={'revision':revision,'all_original_workflow_jobs_success':True,'total_jobs':sum(expected.values()),'runs':runs,'pages_deployment':7532325589,'live_comparison':'live-upload-comparison-v2.json','no_gate_changes_during_collection':True};p=out/'terminal-gates-v2.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print('PASS: all',report['total_jobs'],'original workflow jobs and exact Pages deployment')
