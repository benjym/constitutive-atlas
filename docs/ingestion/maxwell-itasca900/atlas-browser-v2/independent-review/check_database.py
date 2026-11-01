"""Read-only saved Maxwell database projection; no engine or package execution."""
from pathlib import Path
import hashlib,json,sqlite3
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/ingestion/maxwell-itasca900/atlas-browser-v2'
load=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if (Path(__file__).parent/'database-inputs.json').exists():
 for path,h in load(Path(__file__).parent/'database-inputs.json').items():assert sha(R/path)==h,path
report=load(P/'database-projection-v1.json');freeze=load(P/'prospective-freeze-v1.json');site=R/freeze['site'];database=site/'atlas.sqlite';manifest=load(R/freeze['package_manifest'])
assert sha(database)==report['database_sha256']==manifest['files']['atlas.sqlite']
connection=sqlite3.connect(f'file:{database}?mode=ro',uri=True);model='maxwell-itasca900-zero-spin-ode'
row=connection.execute('select executable,definition_json from models where id=?',(model,)).fetchone()
definition=load(R/f'models/research/maxwell/{model}.json');assert row[0]==0 and json.loads(row[1])==definition
registry=load(R/'catalogue/approved-models.json')['models'];records=[json.loads(x[0]) for x in connection.execute('select record_json from model_approvals where model_id=?',(model,))]
assert {x['id'] for x in records}==set(report['approval_ids']) and all(x in registry for x in records)
reviews=connection.execute('select path,sha256,record_json from agent_reviews where model_id=?',(model,)).fetchall()
assert [x[0] for x in reviews]==report['agent_review_paths']
for path,h,record in reviews:assert sha(R/path)==h and json.loads(record)==load(R/path)
urls=sorted(x[0] for x in connection.execute('select distinct url from sources where model_id=?',(model,)))
assert urls==report['source_urls'] and len(urls)==3
assert connection.execute('select count(*) from sources where model_id=?',(model,)).fetchone()[0]==6
assert connection.execute('pragma foreign_key_check').fetchall()==report['foreign_key_errors']==[]
connection.close()
print('PASS: exact frozen packaged SQLite hash; full Maxwell definition, two exact registry approvals, canonical review, three source URLs and no foreign-key errors.')
print('SCOPE: ordinary-engine executable=false retained; dedicated physical-time engine is browser-qualified separately. No whole-package/E6 or scientific expansion.')
