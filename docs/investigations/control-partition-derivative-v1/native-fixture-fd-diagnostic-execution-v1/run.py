"""Retain a single reviewed, expected-failure native diagnostic."""
import datetime, hashlib, json, os, pathlib, subprocess
if not __debug__: raise RuntimeError('Optimization forbidden')
D=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(D/'freeze.json');p=read(D.parent/'native-fixture-fd-diagnostic-v1/plan.json')
s=pathlib.Path(p['source']);t=read(D.parent/'native-ci-fixture-execution-v1/toolchain.json')
env={**os.environ,**t['environment'],**p['env'],'PATH':t['PATH']}
def verify():
    for name,h in f['inputs'].items(): assert sha(pathlib.Path(name))==h,name
    source=read(D.parent/'native-fixture-fd-diagnostic-v1/source-freeze.json')['files']
    assert {str(x.relative_to(s)):sha(x)for x in s.rglob('*')if x.is_file()}==source
    for name,row in t['files'].items(): assert sha(pathlib.Path(name))==row['sha256'],name
for i,argv in enumerate(p['commands']):
    verify();o=D/str(i);o.mkdir(exist_ok=False)
    r={'identity':'md1997-fd-diagnostic-process-v1','argv':argv,'cwd':str(s),'env_changes':{**t['environment'],**p['env'],'PATH':t['PATH']},'start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'started'}
    (o/'process.json').write_text(json.dumps(r,indent=2)+'\n')
    with (o/'stdout').open('wb')as stdout,(o/'stderr').open('wb')as stderr:
        child=subprocess.Popen(argv,cwd=s,env=env,stdout=stdout,stderr=stderr);r['pid']=child.pid;r['returncode']=child.wait()
    r.update(end=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout_sha256=sha(o/'stdout'),stderr_sha256=sha(o/'stderr'))
    verify();r['source_tool_postcheck']=True;r['status']='observed';(o/'process.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'index':i,'returncode':r['returncode'],'receipt':str(o/'process.json')}),flush=True)
    if r['returncode']!=([0,0,1][i]): raise RuntimeError('Unexpected diagnostic process outcome')
