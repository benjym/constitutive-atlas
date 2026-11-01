from pathlib import Path
import json,sqlite3,hashlib,sys,time
from collections import Counter
root=Path('/private/tmp/atlas-mc-admission-public-v1');out=Path('/private/tmp/atlas-mc-admission-evidence-v1');sys.path.insert(0,str(root));from atlas.research import export_database;from tools.build_evidence import bundle
plan=json.loads((out/'INSTALL.json').read_text());candidate={p:(root/p).read_bytes()for p in plan['new_files']};reg=root/'catalogue/approved-models.json';after=reg.read_bytes();before=(out/'registry-before.json').read_bytes()
def exports(label):
 p=out/label;p.mkdir(exist_ok=False);started=time.monotonic();export_database(p/'atlas.sqlite');index=bundle(p/'metadata',root=root);return {'elapsed_seconds':time.monotonic()-started,'agent_reviews':len(index['agent_reviews'])}
try:
 for name,data in candidate.items():assert hashlib.sha256(data).hexdigest()==plan['new_files'][name];(root/name).unlink()
 reg.write_bytes(before);b=exports('before')
finally:
 for name,data in candidate.items():(root/name).write_bytes(data)
 reg.write_bytes(after)
a=exports('after')
def tables(p):
 with sqlite3.connect(p)as db:
  names=[r[0]for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
  return {n:Counter(db.execute('SELECT * FROM '+n).fetchall())for n in names}
bt=tables(out/'before/atlas.sqlite');at=tables(out/'after/atlas.sqlite');assert set(bt)==set(at) and len(bt)==9
rows={}
for n in bt:
 lost=bt[n]-at[n];added=at[n]-bt[n];assert not lost,(n,'lost',lost)
 count=sum(added.values());assert count==(1 if n in ('model_approvals','agent_reviews')else 0),(n,count)
 rows[n]={'before':sum(bt[n].values()),'after':sum(at[n].values()),'removed_rows':0,'added_rows':count}
bi=json.loads((out/'before/metadata/evidence.json').read_text());ai=json.loads((out/'after/metadata/evidence.json').read_text());key=lambda r:r['id'];old={key(r):r for r in bi['agent_reviews']};new={key(r):r for r in ai['agent_reviews']};assert all(new[k]==v for k,v in old.items());assert len(new)==len(old)+1
r=next(v for k,v in new.items()if k not in old);assert r['catalogue_id']=='mohr-coulomb' and r['status']=='accepted' and r['definition_current'] and r['registered_approval_id']=='mohr-coulomb-independent-agent-review-v1-approval'
for k in bi:
 if k!='agent_reviews':assert bi[k]==ai[k],k
files=lambda folder:{p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.rglob('*')if p.is_file()}
bf=files(out/'before/metadata');af=files(out/'after/metadata');assert not(set(bf)-set(af));changes={'new':sorted(set(af)-set(bf)),'changed':sorted(p for p in bf if bf[p]!=af[p]),'removed':[]}
checks={'pass':True,'base':plan['base'],'before':b,'after':a,'tables':rows,'all_prior_evidence_sections_unchanged':True,'all_prior_agent_review_rows_unchanged':True,'new_agent_review':r,'metadata_files':changes,'scope':'Normal full database/evidence exports only; no material execution, current package/browser/live or experimental qualification.'};(out/'PROJECTION_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps({'pass':True,'tables':rows,'metadata_files':changes}))
