from pathlib import Path
import subprocess,json,shutil
r=Path('/Users/bmar5496/code/constitutive-atlas');d=Path('/private/tmp/atlas-example-seven-browser-v1');d.mkdir();cli=['node','/Users/bmar5496/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js','--session','atlas-v03']
for path in sorted((r/'models').glob('*.json')):
 m=json.loads(path.read_text());mid=m['id']
 for label,args in [('select',['select','f3e34',mid]),('export',['click','f3e183'])]:
  p=subprocess.run(cli+args,capture_output=True,text=True,timeout=40);(d/(mid+'-'+label+'.txt')).write_text(p.stdout+p.stderr);assert p.returncode==0
 source=Path.cwd()/'.playwright-cli'/(mid+'-run.json');assert source.exists();shutil.copy2(source,d/(mid+'-run.json'))
 run=json.loads(source.read_text());spec=run['specification'];assert run['result']['ok'];assert spec['model']==mid
 expected=m['state'][0]['initial'];assert spec['initial'][:6]==expected
 assert spec['initial']==[v for f in m['state'] for v in (f['initial']if f['shape']=='sym'else [f['initial']])]
 for a,b in zip(spec['parameters'],(p['default']for p in m['parameters'].values())):assert abs(a-b)<=1e-14*max(1,abs(b))
 print(mid,'pass',len(run['result']['points']),flush=True)
