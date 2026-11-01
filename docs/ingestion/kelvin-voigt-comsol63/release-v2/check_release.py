"""Read-only verification of terminal CI, tested upload and saved qualification reports."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);p.add_argument('artifact',type=Path);a=p.parse_args()
read=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
workflow=read(a.evidence/'workflow.json');commit='e32f8a86df44298f100394b34e084e313d48b195'
assert workflow['headSha']==commit and workflow['status']=='completed' and workflow['conclusion']=='success'
expected={'native (ubuntu-latest, 3.12)','native (macos-26, 3.14)','wasm','wasm-linux','controlled-path','deploy'}
assert {j['name'] for j in workflow['jobs']}==expected
assert all(j['status']=='completed' and j['conclusion']=='success' for j in workflow['jobs'])
reports={}
for rel in ['native-ci/native-linux.json','native-ci/native-macos.json','wasm-ci/macos/report.json','wasm-ci/linux/report.json']:
 x=read(a.evidence/rel);q=x.get('report',x)
 assert q['passed'] and q['cases']==43 and q['calls']==86 and q['negative_recovery_pairs']==8
 reports[rel]={'sha256':sha(a.evidence/rel),'cases':q['cases'],'calls':q['calls']}
engine=a.artifact/'engine-kelvin-voigt';identity=read(engine/'identity.json');assert identity['release_revision']==commit
id='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';assert identity['model']==id
assert identity['model_sha256']==sha(engine/(id+'.json'))=='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
assert identity['module_sha256']==sha(engine/'kv.mjs') and identity['wasm_sha256']==sha(engine/'kv.wasm')
assert identity['review_sha256']==sha(engine/'review.json')=='7dc232c311541aea981981e1efcfc97448509fbc31d9602b9cead4a7890223c4'
assert identity['approval_sha256']==sha(engine/'approval.json')
manifest=read(engine/'package-manifest.json')
assert all(sha(a.artifact/name)==h for name,h in manifest['files'].items())
connection=sqlite3.connect(f'file:{a.artifact / "atlas.sqlite"}?mode=ro',uri=True)
assert connection.execute('pragma integrity_check').fetchone()[0]=='ok';assert not connection.execute('pragma foreign_key_check').fetchall()
connection.close()
result={'passed':True,'application_commit':commit,'required_successful_jobs':sorted(expected),'reports':reports,'exact_model_review_approval_engine_components':True,'sqlite_integrity_foreign_keys':True,'tested_upload_assets':len([p for p in a.artifact.rglob('*') if p.is_file()])}
(a.evidence/'release-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
