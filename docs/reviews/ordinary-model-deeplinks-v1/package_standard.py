from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time,datetime,os,signal
R=Path('/Users/bmar5496/code/constitutive-atlas');P=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=R/'docs/ingestion/barodesy-clay-2017/root-registration-v1'
dest=Path('/private/tmp/atlas-deeplink-standard-site-v1');assert not dest.exists()
command=read(old/'package-retry-plan-v2.json')['command'];command[command.index('--output')+1]=str(dest)
files={p:sha(Path(p)) for p in read(old/'package-freeze-v1.json')['files']}
for n in ['web/app.js','tests/test_laboratory_deeplinks.mjs','tests/test_j2_main_routing.mjs','docs/reviews/ordinary-model-deeplinks-v1/installation-result-v1.json','docs/reviews/ordinary-model-deeplinks-v1/independent-review/receipt.json']:
 files[str(R/n)]=sha(R/n)
freeze={'scope':'Standard package after reviewed navigation-only install. Retained qualified engines; unchanged numerical policies. Existing strict GIS default failure retained. No compilation or remote action.','command':command,'timeout_seconds':300,'files':files}
(P/'package-freeze-v1.json').write_text(json.dumps(freeze,indent=2)+'\n')
started=time.monotonic();record={'command':command,'freeze_sha256':sha(P/'package-freeze-v1.json'),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_seconds':300}
with (P/'package-build-v1.stdout.log').open('w') as out,(P/'package-build-v1.stderr.log').open('w') as err:
 proc=subprocess.Popen(command,cwd=R,stdout=out,stderr=err,start_new_session=True);record['pid']=proc.pid
 (P/'package-process-v1.json').write_text(json.dumps(record,indent=2)+'\n')
 try:rc=proc.wait(timeout=300);timed=False
 except subprocess.TimeoutExpired:
  os.killpg(proc.pid,signal.SIGTERM);rc=proc.wait(timeout=10);timed=True
record.update(exit_code=rc,timed_out=timed,elapsed_seconds=time.monotonic()-started)
record['all_frozen_inputs_unchanged']=all(sha(Path(p))==h for p,h in files.items())
(P/'package-build-v1.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if rc or timed or not record['all_frozen_inputs_unchanged']:sys.exit(1)
checks=[]
for kind,tool in [('supported','test_supported_package.mjs'),('strict','test_web_package.mjs')]:
 cmd=['node','tools/'+tool,'--directory',str(dest),'--output',str(P/(kind+'-package-v1.json'))]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=120)
 (P/(kind+'-package-v1.stdout.log')).write_text(z.stdout);(P/(kind+'-package-v1.stderr.log')).write_text(z.stderr)
 checks.append({'command':cmd,'exit_code':z.returncode})
(P/'package-checks-v1.json').write_text(json.dumps(checks,indent=2)+'\n')
assert checks[0]['exit_code']==0
assert checks[1]['exit_code']==1
assert read(P/'strict-package-v1.json')['error']==read(old/'strict-package-v2.json')['error']
durable=R/'.local/private-evidence/ordinary-model-deeplinks-v1/site-v1';assert not durable.exists()
durable.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(dest,durable)
manifest={str(p.relative_to(durable)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(durable.rglob('*')) if p.is_file()}
(P/'package-manifest-v1.json').write_text(json.dumps({'path':str(durable),'files':manifest},indent=2)+'\n')
before=read(P/'candidate-package-v1.json')['files']
delta={'added':sorted(set(manifest)-set(before)),'removed':sorted(set(before)-set(manifest)),'changed':sorted(k for k in set(before)&set(manifest) if before[k]!=manifest[k]),'package_files':len(manifest),'candidate_files':len(before),'strict_failure_unchanged':True}
(P/'package-delta-v1.json').write_text(json.dumps(delta,indent=2)+'\n');print(json.dumps(delta,indent=2))
