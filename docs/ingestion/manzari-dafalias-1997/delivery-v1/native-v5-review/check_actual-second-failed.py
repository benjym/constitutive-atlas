"""Saved evidence only: never invokes a compiler or material artifact."""
import contextlib,hashlib,io,json,runpy,sys,tarfile
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;B=P/'qualification-native-v5';MD=Path('/private/tmp/atlas-control-partition-v1/md-native-v5');O=MD.parent/'ordinary-native-v7';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
runpy.run_path(str(D/'check_inputs.py'),run_name='__main__')
receipt=load(B/'retention-receipt.json');archive=B/receipt['archive'];check('durable archive sha',h(archive)==receipt['sha256'])
with tarfile.open(archive,'r:gz')as t:
 members={x.name:x for x in t.getmembers()if x.isfile()};check('exact80 archive members',len(members)==80 and set(members)=={x['path']for x in receipt['files']})
 for row in receipt['files']:
  blob=t.extractfile(members[row['path']]).read();check('archive+working/'+row['path'],len(blob)==row['size'] and hashlib.sha256(blob).hexdigest()==row['sha256'] and (MD.parent/row['path']).read_bytes()==blob)
for n in ['collect','ordinary']:
 process=load(B/(n+'-process.json'));check(n+'/parent process success',process['returncode']==0)
 check(n+'/new full collector command',any(str(v).endswith('/raw-link-v7/run_bound.py')for v in load(B/(n+'-start.json'))['command']) and '--case'not in load(B/(n+'-start.json'))['command'])
for label,script,args,saved,out in [('MD raw',P/'raw-link-v7/check_raw.py',[str(MD),'--study','md'],'raw-checks.json','rechecked-raw.json'),('ordinary raw',P/'raw-link-v7/check_raw.py',[str(O),'--study','ordinary'],'ordinary-raw-checks.json','rechecked-ordinary-raw.json'),('MD source',P/'resolution-study-v4/check_reports.py',[str(MD/'report.json')],'source-checks.json','rechecked-source.json')]:
 with patch.object(sys,'argv',[str(script)]+args+['--output',str(D/out)]),patch.object(sys,'path',[str(script.parent)]+sys.path),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:check(label+'/checker exit',ex.code==0)
 actual=load(D/out);original=load(B/saved)
 check(label+'/exact saved checker result reproduced',actual==original)
report=load(MD/'report.json');ordinary=load(O/'report.json');source=load(D/'rechecked-source.json');plan=load(P/'resolution-study-v4/requests.json');policy=load(P/'ordinary-regression-v7/policy.json')
check('full35 cases and24special45143calls',list(report['cases'])==[x['id']for x in plan['cases']] and len(report['cases'])==35 and len(report['special'])==24 and report['call_count']==45143)
check('all35 operational outcomes successful',all(x['ok']is True for x in report['cases'].values()))
check('all96943 main checks pass',len(source['checks'])==96943 and all(x['passed']for x in source['checks']))
check('ordinary exact16 expected outcomes',ordinary['passed']is True and len(ordinary['cases'])==16 and [x['model']for x in ordinary['cases']]==[x['model']for x in policy['cases']] and all(x['passed']is True for x in ordinary['cases']))
check('ordinary preserved15successes and1 declared rejection',sum(x['response']['ok']is True for x in ordinary['cases'])==15 and sum(x['response']['ok']is False for x in ordinary['cases'])==1)
(D/'actual-checks.json').write_text(json.dumps({'decision':'accepted bounded actual native study and ordinary outcomes only','compiled_calls':0,'checks':checks},indent=2)+'\n');print('review checks',len(checks),'source',len(source['checks']))
