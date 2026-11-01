from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent
engine=sys.argv[1];rows=[];processes=[]
descriptor=json.loads(subprocess.check_output([engine,'--describe']))
for request in json.loads((p/'requests.json').read_text()):
    args=[str(p/a[1:])if a.startswith('@controls/')else a for a in request['native_arguments']]
    proc=subprocess.run([engine,*args],capture_output=True,text=True)
    assert proc.returncode in(0,1)and not proc.stderr,(request['id'],proc.stderr)
    result=json.loads(proc.stdout);assert proc.returncode==(0 if result['ok']else 1)
    rows.append({'id':request['id'],'result':result})
    processes.append({'id':request['id'],'argv':[engine,*args],'exit_code':proc.returncode,'stderr':proc.stderr})
print(json.dumps({'descriptor':descriptor,'rows':rows,'processes':processes}))
