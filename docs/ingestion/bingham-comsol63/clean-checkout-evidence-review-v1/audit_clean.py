from pathlib import Path
import sys,json,os,subprocess,hashlib,traceback
from unittest.mock import patch
O=Path(__file__).resolve().parent;R=O.parents[3]
root=Path(sys.argv[1]).resolve();label=sys.argv[2];out=O/label;out.mkdir(exist_ok=False);reads=set();blocked=[]
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).absolute()
  if p.is_relative_to(root) and not p.is_relative_to(O):reads.add(p.relative_to(root).as_posix())
sys.addaudithook(audit)
sys.path.insert(0,str(root))
from atlas.model import all_models
from atlas import research
from atlas.agent_review import validate_review
from tools.build_evidence import bundle
assert research.ROOT==root,(research.ROOT,root)
def deny(*a,**k):blocked.append(str(a));raise AssertionError('Process/material/network execution forbidden')
for name in ['Popen','run','check_call','check_output']:setattr(subprocess,name,deny)
for name in ['system','posix_spawn','execv','execve']:setattr(os,name,deny)
import urllib.request,socket
urllib.request.urlopen=deny;socket.create_connection=deny
results=[]
def run(name,fn):
 try:v=fn();results.append({'name':name,'passed':True,'result':v})
 except Exception as e:results.append({'name':name,'passed':False,'error_type':type(e).__name__,'error':str(e).replace(str(root),'<ROOT>')})
run('all_models',lambda:len(list(all_models())))
reg=json.loads((root/'catalogue/approved-models.json').read_text());reviews=sorted({a['review']['path'] for a in reg['models'] if a.get('status')=='approved' and a.get('review',{}).get('kind')=='agent-model-review'})
for name in reviews:run('approval:'+name,lambda n=name:validate_review(root/n,root=root,for_approval=True)['id'])
def db():
 research.export_database(out/'atlas.sqlite');import sqlite3
 with sqlite3.connect(out/'atlas.sqlite') as c:return {n[0]:c.execute('select count(*) from '+n[0]).fetchone()[0] for n in c.execute("select name from sqlite_master where type='table'").fetchall()}
run('database_export',db)
run('evidence_export',lambda:{k:len(v) for k,v in bundle(out/'evidence-site',root=root).items() if isinstance(v,list)})
x={'source_root':str(root),'results':results,'read_inputs':sorted(reads),'process_or_material_or_remote_calls':blocked,'all_passed':all(z['passed'] for z in results)};(O/(label+'.json')).write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'all_passed':x['all_passed'],'checks':len(results),'failures':[z for z in results if not z['passed']],'read_inputs':len(reads),'blocked_calls':blocked},indent=2))
