"""Complete ordinary post-install exports, compared with retained current-root baseline."""
from pathlib import Path
import json,sqlite3,sys,hashlib,subprocess
from collections import Counter
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.research import export_database
from atlas.agent_review import approval_entry
from tools.build_evidence import bundle
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def tables(path):
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()==('ok',)
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        return {name:Counter(db.execute('SELECT * FROM '+name).fetchall()) for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
def main():
    entries=json.loads((ROOT/'docs/admission/baseline-hypoplastic-canonical-v1/approval-entries.json').read_text())
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
    for e in entries:
        assert approval_entry(ROOT/e['review']['path'],root=ROOT)==e
        assert registry['models'].count(e)==1
    before=tables(HERE/'database-before.sqlite')
    export_database(HERE/'database-after.sqlite')
    after=tables(HERE/'database-after.sqlite')
    assert set(before)==set(after)
    delta={}
    for name in before:
        removed=before[name]-after[name];added=after[name]-before[name]
        assert not removed,name
        assert sum(added.values())==(2 if name in ('agent_reviews','model_approvals') else 0),(name,sum(added.values()))
        delta[name]={'before':sum(before[name].values()),'after':sum(after[name].values()),'added':sum(added.values()),'removed':sum(removed.values())}
    projection=bundle(HERE/'evidence-after',root=ROOT)
    baseline=json.loads((HERE/'evidence-before/evidence.json').read_text())
    assert projection['records']==baseline['records']
    assert projection['reviews']==baseline['reviews']
    old={row['id']:row for row in baseline['agent_reviews']}
    new={row['id']:row for row in projection['agent_reviews']}
    assert all(new[k]==v for k,v in old.items())
    assert set(new)-set(old)=={json.loads((ROOT/e['review']['path']).read_text())['id'] for e in entries}
    for e in entries:
        record=json.loads((ROOT/e['review']['path']).read_text())
        row=new[record['id']]
        assert row['definition_current'] and row['registered_approval_id']==e['id']
        assert row['scope']==record['scope'] and row['limitations']==record['limitations']
    def files(folder):return {str(f.relative_to(folder)):sha(f) for f in folder.rglob('*') if f.is_file()}
    f0=files(HERE/'evidence-before');f1=files(HERE/'evidence-after')
    added=sorted(set(f1)-set(f0));removed=sorted(set(f0)-set(f1));changed=sorted(k for k in f0.keys()&f1.keys() if f0[k]!=f1[k])
    assert not removed and len(added)==4,(added,removed)
    assert changed==['evidence-records/catalogue/approved-models.json','evidence.json'],changed
    js="import fs from 'node:fs';import {validateEvidenceIndex} from './web/catalogue.mjs';const index=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));validateEvidenceIndex(index);console.log(JSON.stringify({agent_reviews:index.agent_reviews.length,status:'PASS',scope:'Full current projected evidence schema; no actual browser run'}));"
    proc=subprocess.run(['node','--input-type=module','-e',js,str(HERE/'evidence-after/evidence.json')],cwd=ROOT,text=True,capture_output=True)
    (HERE/'evidence-schema.stdout').write_text(proc.stdout);(HERE/'evidence-schema.stderr').write_text(proc.stderr)
    assert proc.returncode==0,proc.stderr
    result={'passed':True,'complete_current_database':delta,'numerical_records_unchanged':len(projection['records']),'source_reviews_unchanged':len(projection['reviews']),'existing_agent_reviews_unchanged':len(old),'new_agent_reviews':2,'public_export_delta':dict(added=added,removed=removed,changed=changed),'full_evidence_schema':json.loads(proc.stdout),'compiled_calls':0,'site_rebuilt_or_deployed':False}
    (HERE/'POST_INSTALL_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
