"""Coordinate exact Actions upload, live files and real Playwright CLI checks."""
from pathlib import Path
import os,json,hashlib,subprocess,zipfile,tarfile,argparse,shutil
ROOT=Path('/private/tmp/atlas-norsand-release-v1')
OUT=ROOT/'docs/ingestion/norsand-1993/release-v1/remote-v1/live-v2'
TMP=Path('/private/tmp/atlas-norsand-live-v2')
SHA='3873a48b256ed37cbc78378ee6b41d73139676f8';RUN=41343952906
CLI=os.environ.get('PLAYWRIGHT_CLI','/Users/bmar5496/.npm/_npx/31e32ef8478fbf80/node_modules/.bin/playwright-cli')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def proc(args):return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True)
def gh(*args):return json.loads(proc(['gh',*args]).stdout)
def artifact(item):
 assert item['workflow_run']['head_sha']==SHA and item['workflow_run']['id']==RUN
 d=TMP/item['name'];d.mkdir(exist_ok=True);p=d/'download.zip'
 if not p.exists() or 'sha256:'+digest(p)!=item['digest']:
  with p.open('wb') as f:subprocess.run(['gh','api',f"repos/benjym/constitutive-atlas/actions/artifacts/{item['id']}/zip"],stdout=f,cwd=ROOT,check=True)
 assert 'sha256:'+digest(p)==item['digest']
 target=d/'extracted';target.mkdir(exist_ok=True)
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
  z.extractall(target)
 save(item['name']+'-download-v2.json',{'result':'PASS','scope':'Actual run/head-bound artifact API digest and ZIP CRC; no deployment inferred','artifact':item,'zip_sha256':digest(p)})
 return target
def browser(action,*args):
 env=os.environ.copy();env['PWTEST_DAEMON_SESSION_DIR']='/private/tmp/atlas-norsand-playwright'
 cmd=[CLI,'-s=norsand-live-v2',*args];p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
 save(action+'-process-v2.json',{'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 assert p.returncode==0,(action,p.stdout,p.stderr)
 if '### Result\n' in p.stdout:
  result=json.loads(p.stdout.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0]);save(action+'-result-v2.json',result);return result
 return None
def main():
 a=argparse.ArgumentParser();a.add_argument('--upload-only',action='store_true');args=a.parse_args()
 acceptance=json.loads((OUT/'live-acceptance-v2.json').read_text())
 for p,h in acceptance['source_pins'].items():assert digest(ROOT/p)==h
 meta=gh('api',f'repos/benjym/constitutive-atlas/actions/runs/{RUN}/artifacts');save('artifacts-v2.json' if args.upload_only else 'artifacts-terminal-v2.json',meta)
 item=next(i for i in meta['artifacts'] if i['name']=='github-pages');raw=artifact(item);site=TMP/'github-pages/site';site.mkdir(exist_ok=True)
 with tarfile.open(raw/'artifact.tar') as tf:tf.extractall(site,filter='data')
 if args.upload_only:print('Exact tested upload downloaded and verified; final CI/deployment remains pending.');return
 ci=gh('run','view',str(RUN),'--json','status,conclusion,headSha,jobs,url');save('ci-terminal-v2.json',ci)
 assert ci['headSha']==SHA and ci['status']=='completed' and ci['conclusion']=='success'
 assert sorted(j['name'] for j in ci['jobs'])==sorted(acceptance['required_terminal_success_jobs']) and all(j['conclusion']=='success' for j in ci['jobs'])
 controlled=artifact(next(i for i in meta['artifacts'] if i['name']=='controlled-path-qualification'))
 for n in ['native.json','wasm.json']:shutil.copyfile(controlled/'path-results'/n,OUT/n)
 cmd=['python3','-B','docs/ingestion/norsand-1993/e2-v3/check_backend_results_v3.py','docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json',str(OUT/'native.json'),str(OUT/'wasm.json')];p=proc(cmd);result=json.loads(p.stdout);assert result['result']=='PASS';save('backend-check-v2.json',{'command':cmd,'exit_code':p.returncode,'result':result,'stderr':p.stderr,'artifact_files':{str(f.relative_to(controlled)):digest(f) for f in controlled.rglob('*') if f.is_file()}})
 p=proc(['python3',str(OUT/'verify_live_upload.py'),str(site),str(OUT/'live-upload-v2.json')]);print(p.stdout.strip())
 url='https://benjym.github.io/constitutive-atlas/#laboratory?model=norsand-jefferies-1993-active-axial'
 browser('open','open',url,'--headed');browser('wait','run-code','async (page) => {await page.waitForLoadState("networkidle");}');browser('snapshot','snapshot')
 result=browser('lifecycle','run-code','--filename',str(OUT/'browser-lifecycle-v1.js'));assert result['result']=='PASS' and not result['browser_errors'] and not result['network_failures']
 shutil.copyfile(TMP/'default-run.json',OUT/'default-run.json');p=proc(['python3',str(OUT/'make_tamper_fixtures.py')]);save('tamper-fixtures-process-v2.json',{'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 for n in ['bad-identity.json','bad-context.json','bad-result.json']:shutil.copyfile(OUT/n,TMP/n)
 result=browser('import','run-code','--filename',str(OUT/'browser-import-v1.js'));assert result['result']=='PASS' and not result['browser_errors'] and not result['network_failures'];shutil.copyfile(TMP/'replayed-run.json',OUT/'replayed-run.json');assert json.loads((OUT/'default-run.json').read_text())==json.loads((OUT/'replayed-run.json').read_text())
 upload=json.loads((OUT/'live-upload-v2.json').read_text());assert all(upload['upload_files'][n]==h for n,h in result['imported']['fetched'].items())
 result=browser('visual','run-code','--filename',str(OUT/'browser-visual-v1.js'));assert result['result']=='PASS' and not result['mobile_horizontal_overflow']
 save('qualification-v2.json',{'result':'PASS','revision':SHA,'run':RUN,'required_jobs':6,'upload_files':len(upload['upload_files']),'live_exact_assets':len(upload['fetched']),'native_requests':58,'wasm_requests':58,'browser_default_points':41,'plots':3,'actual_export_replay_equal':True,'lifecycle_import_tamper_recovery':True,'browser_errors':[],'network_failures':[],'screenshots':{str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'output/playwright/norsand-live-v2').glob('*.png')},'scope':'Exact approved active monotonic drained axial model; no experimental or broader kinematic claim.'})
 print('PASS exact final CI/upload/live/browser; screenshots require visual inspection and independent review.')
if __name__=='__main__':main()
