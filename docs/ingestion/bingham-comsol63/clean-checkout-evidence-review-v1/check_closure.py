from pathlib import Path
import json,hashlib,sqlite3,os
O=Path(__file__).resolve().parent; R=Path('/private/tmp/atlas-bingham-release-v3'); C=Path('/private/tmp/atlas-bingham-clean-review-v2'); P=R/'docs/ingestion/bingham-comsol63/clean-checkout-evidence-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
i=json.loads((O/'TRACKED-INVENTORY.json').read_text())['files'];a=json.loads((P/'INSTALLATION.json').read_text())['files']; changed=[n for n,v in i.items() if (hashlib.sha256(os.readlink(C/n).encode()).hexdigest() if v['mode']=='120000' else sha(C/n))!=v['sha256']];assert not changed
x=json.loads((O/'tracked-after.json').read_text());missing=[n for n in x['read_inputs'] if (C/n).is_file() and n not in i and n not in a];assert not missing,missing
reg=json.loads((O/'ALL-REGISTRY-AFTER.json').read_text());assert all(n in i or n in a for n in reg['inputs'])
# Compare database logical rows (SQLite bytes need not have stable layout).
def rows(p):
 with sqlite3.connect(p) as c:return {n[0]:sorted(c.execute('select * from '+n[0]).fetchall(),key=repr) for n in c.execute("select name from sqlite_master where type='table'").fetchall()}
assert rows(O/'tracked-after/atlas.sqlite')==rows(O/'local-complete/atlas.sqlite')
l=O/'local-complete/evidence-site';r=O/'tracked-after/evidence-site';lf={p.relative_to(l).as_posix():sha(p) for p in l.rglob('*') if p.is_file()};rf={p.relative_to(r).as_posix():sha(p) for p in r.rglob('*') if p.is_file()};assert lf==rf
out={'passed':True,'old_tracked_files_verified_unchanged':len(i),'additions':len(a),'active_observed_reads':len(x['read_inputs']),'untracked_required_reads':missing,'registry_paths':reg['path_checks'],'registry_approvals':reg['approval_count'],'logical_database_rows_equal_local':True,'export_files_equal_local':len(lf),'optional_local_pyc_reads':sum(n.endswith('.pyc') and (R/n).is_file() for n in json.loads((O/'local-complete.json').read_text())['read_inputs']),'clean_pyc_reads':sum(n.endswith('.pyc') and (C/n).is_file() for n in x['read_inputs'])};(O/'CLOSURE-CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
