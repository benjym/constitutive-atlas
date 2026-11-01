"""Distinguish current local exporter capability from committed release coverage."""
import hashlib,json,sqlite3,subprocess,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
MID='sls-comsol63-deviatoric-zero-spin-ode';result={}
for label,code in [('committed',subprocess.check_output(['git','show','HEAD:atlas/research.py'],cwd=ROOT)),('working',(ROOT/'atlas/research.py').read_bytes())]:
 module=types.ModuleType('atlas.research_audit_'+label);module.__package__='atlas';exec(compile(code,'atlas/research.py','exec'),module.__dict__)
 with tempfile.TemporaryDirectory(prefix='sls-database-audit-') as tmp:
  file=Path(tmp)/'atlas.sqlite';module.export_database(file)
  with sqlite3.connect(file) as c:
   row=c.execute('select executable,definition_json from models where id=?',(MID,)).fetchone();tables={x[0] for x in c.execute("select name from sqlite_master where type='table'")}
   approvals=[json.loads(x[0]) for x in c.execute('select record_json from model_approvals where model_id=?',(MID,))] if 'model_approvals' in tables else []
   reviews=[json.loads(x[0]) for x in c.execute('select record_json from agent_reviews where model_id=?',(MID,))] if 'agent_reviews' in tables else []
   definition=json.loads(row[1]) if row and row[1] else None;expected=json.loads((ROOT/'models/research/sls'/f'{MID}.json').read_text())
   sources=c.execute('select url,locator,role from sources where model_id=?',(MID,)).fetchall()
   result[label]=dict(exporter_sha256=hashlib.sha256(code).hexdigest(),model_present=row is not None,ordinary_executable=bool(row[0]),exact_definition=definition==expected,approval_records=len(approvals),accepted_review_records=sum(x['status']=='accepted' for x in reviews),source_rows=len(sources),foreign_key_check=c.execute('pragma foreign_key_check').fetchall())
print(json.dumps(result,indent=2))
