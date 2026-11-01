"""Read-only retrospective integrity/coverage audit; no compiled execution."""
import hashlib,json,sqlite3,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];PACKET=ROOT/'docs/ingestion/power-creep-itasca900'
sys.path.insert(0,str(ROOT))
from atlas.model import load
from atlas.compiler import generate
from atlas.research import export_database
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=0
for folder in [PACKET,PACKET/'execution-v1',PACKET/'verification-v1',PACKET/'review-v1',ROOT/'docs/admission/power-creep-approved-v1']:
 m=json.loads((folder/'manifest.json').read_text())
 for p,h in m['files'].items():
  assert sha(folder/p)==h,str(folder/p)
  checked+=1
model=ROOT/'models/research/power-creep/power-creep-itasca900-both-active-ode.json';load(model)
with tempfile.TemporaryDirectory() as tmp:
 generate(tmp,[model]);db=Path(tmp)/'audit.sqlite';export_database(db)
 with sqlite3.connect(db) as c:
  row=c.execute('select status,executable,definition_json is not null from models where id=?',(model.stem,)).fetchone()
  sources=c.execute('select count(*) from sources where model_id=?',(model.stem,)).fetchone()[0]
page=(ROOT/'web/power-creep.html').read_text()
result={'integrity':'passed','manifest_files_checked':checked,'nested_model_validation_generation':'passed','model_sha256':sha(model),'database_export':{'status':row[0],'ordinary_runtime_executable':bool(row[1]),'definition_retained':bool(row[2]),'sources':sources,'approval_retained':False,'gap':'Export uses only top-level definitions; research timed law is exported as candidate without exact definition or approval.'},'browser_coverage_gaps':['No exposed import/replay control','No exposed reset control','No full six-component state inspection in the page','Invalid input/recovery, rapid latest-request changes, all parameter/initial-state interactions not qualified in actual browser','No explicit measurement-comparison applicability explanation'],'delivery_complete':False}
assert 'power-creep-approval.json' in page and 'power-creep-review.html' in page
assert './engine/identity.json' in page and "'/engine/" not in page
print(json.dumps(result,indent=2))
