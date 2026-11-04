from pathlib import Path
import json,subprocess,hashlib,time
P=Path(__file__).resolve().parent
plan=json.loads((P/'plan.json').read_text());rows=[]
for x in plan['calls']:
 assert hashlib.sha256(Path(x['argv'][0]).read_bytes()).hexdigest()==x['binary_sha256']
 t=time.time();r=subprocess.run(x['argv'],capture_output=True,text=True,timeout=120)
 (P/(x['identity']+'.stdout')).write_text(r.stdout);(P/(x['identity']+'.stderr')).write_text(r.stderr)
 a=json.loads(r.stdout);rows.append({**x,'returncode':r.returncode,'ok':a['ok'],'points':len(a.get('points',[])),'message':a.get('message'),'started_epoch':t,'ended_epoch':time.time()})
 (P/'observations.json').write_text(json.dumps(rows,indent=2)+chr(10))
 assert a.get('integration_settings')==plan['settings'],'wire did not preserve original settings'
print(json.dumps([{k:x[k]for k in ['identity','returncode','ok','points','message']}for x in rows]))
