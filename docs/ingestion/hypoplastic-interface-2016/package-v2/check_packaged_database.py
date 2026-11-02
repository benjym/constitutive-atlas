"""Check final packaged database preserves every existing public row and exact admission."""
from pathlib import Path
from collections import Counter
import hashlib,json,sqlite3,sys
site=Path(sys.argv[1]);output=Path(sys.argv[2]);baseline=Path('/private/tmp/atlas-interface2016-delivery-v1/baseline.sqlite');model='hvwe2016-reconciled-fixed-local'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with sqlite3.connect('file:'+str(baseline)+'?mode=ro',uri=True) as old,sqlite3.connect('file:'+str(site/'atlas.sqlite')+'?mode=ro',uri=True) as new:
 tables=[n for n, in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")];assert len(tables)==9
 results={}
 for t in tables:
  assert t.replace('_','').isalnum();a=Counter(old.execute('SELECT * FROM '+t));b=Counter(new.execute('SELECT * FROM '+t));assert not (a-b),('Old rows missing',t);results[t]=dict(old=sum(a.values()),new=sum(b.values()),all_old_rows_preserved=True)
 assert new.execute('PRAGMA integrity_check').fetchall()==[('ok',)];assert new.execute('PRAGMA foreign_key_check').fetchall()==[]
 definition=json.loads(new.execute('SELECT definition_json FROM models WHERE id=?',(model,)).fetchone()[0]);assert definition==json.loads((site/'material-point-interface2016/engine-path/model.json').read_text())
 review=json.loads((site/'material-point-interface2016/engine-path/review.json').read_text());assert review['status']=='accepted' and review['model']['sha256']==sha(site/'material-point-interface2016/engine-path/model.json')
 report=dict(passed=True,scope='Packaged public database and old-row preservation; no numerical/browser claim',tables=results,baseline_sha256=sha(baseline),packaged_database_sha256=sha(site/'atlas.sqlite'),exact_model_and_review=True)
output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
