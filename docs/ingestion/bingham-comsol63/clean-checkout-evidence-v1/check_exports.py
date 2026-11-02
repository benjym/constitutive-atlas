"""Pure source/catalogue/export entrypoint; records actual inputs; no children."""
from pathlib import Path
import hashlib,json,os,sqlite3,subprocess,sys,traceback
from unittest.mock import patch
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(root))
from atlas.model import all_models
from atlas.research import export_database
from tools.build_evidence import bundle
reads=set()
def watch(event,args):
 if event=='open':
  path=args[0]
  if not isinstance(path,(str,bytes,os.PathLike)):return
  p=Path(os.fsdecode(path)).absolute()
  if p.is_relative_to(root) and p.suffix!='.pyc' and p.is_file():reads.add(p.relative_to(root).as_posix())
sys.addaudithook(watch)
calls=[]
def blocked(*a,**kw):calls.append(1);raise AssertionError('Child/compiler/engine execution forbidden')
patches=[patch.object(owner,name,blocked) for owner,name in [(subprocess,'Popen'),(subprocess,'run'),(subprocess,'check_call'),(subprocess,'check_output'),(os,'system'),(os,'posix_spawn')]]
for p in patches:p.start()
results={}
try:
 for name,fn in [('validate',lambda:len(all_models())),('database',lambda:export_database(out/'atlas.sqlite')),('evidence_export',lambda:bundle(out/'site',root=root))]:
  try:
   v=fn();results[name]={'passed':True,'result':(str(v) if isinstance(v,Path) else v) if name!='evidence_export' else {'records':len(v['records']),'source_reviews':len(v['reviews']),'agent_reviews':len(v['agent_reviews'])}}
  except Exception as e:
   results[name]={'passed':False,'error_type':type(e).__name__,'error':str(e)};(out/(name+'-failure.log')).write_text(traceback.format_exc())
finally:
 for p in reversed(patches):p.stop()
assert not calls
# Reads are scientific/API inputs observed before this report; hashing adds none.
inputs={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in sorted(reads)}
report={'root':str(root),'checks':results,'inputs':inputs,'compiler_material_subprocess_calls':0,'passed':all(v['passed'] for v in results.values())};(out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='inputs'},indent=2));sys.exit(0 if report['passed'] else 1)
