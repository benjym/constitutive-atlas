"""Verify the tested upload's database and preservation of the preceding atlas."""
import argparse,hashlib,json,sqlite3,subprocess
from pathlib import Path
MID='barodesy-sand'
PRIOR='9c0130fc0cf845f7e44b4c0741fa697329570948'
def main():
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 def old(path):return json.loads(subprocess.check_output(['git','show',PRIOR+':'+path]))
 previous=old('catalogue/manifest.json')['models'];approvals=old('catalogue/approved-models.json')['models']
 c=sqlite3.connect('file:'+str((a.site/'atlas.sqlite').resolve())+'?mode=ro',uri=True)
 rows={x[0]:x for x in c.execute('select id,name,family,status,executable from models')}
 current={m['id']:m for m in json.loads((a.site/'catalogue.json').read_text())['models']}
 for m in previous:
  if m['id']==MID:continue
  assert current[m['id']]==m
  assert rows[m['id']][0:3]==(m['id'],m['name'],m['family']) and rows[m['id']][4]==int(m['executable'])
  definition=c.execute('select definition_json from models where id=?',(m['id'],)).fetchone()[0]
  if definition is not None:assert rows[m['id']][3]==json.loads(definition)['status']
 saved={x[0]:json.loads(x[1]) for x in c.execute('select id,record_json from model_approvals')}
 for m in approvals:assert saved[m['id']]==m
 model=json.loads((a.site/'models'/f'{MID}.json').read_text());assert json.loads(c.execute('select definition_json from models where id=?',(MID,)).fetchone()[0])==model
 registry=json.loads((a.site/'evidence-records/catalogue/approved-models.json').read_text())['models'];approval=next(x for x in registry if x['model_id']==MID);assert saved[approval['id']]==approval
 review=json.loads((a.site/('evidence-records/'+approval['review']['path'])).read_text());assert json.loads(c.execute('select record_json from agent_reviews where id=?',(review['id'],)).fetchone()[0])==review
 assert c.execute('select count(*) from sources where model_id=? and url=?',(MID,'https://doi.org/10.1680/geot.14.P.151')).fetchone()[0]>0
 assert set(rows)-set(current)=={'nakai-hinokio-2004-clay-appendix-v-be'}
 report={'diagnostic_version':3,'public_catalogue_models':len(current),'additional_research_models':sorted(set(rows)-set(current)),'status':'passed','prior_revision':PRIOR,'prior_manifest_rows_preserved':len(previous),'prior_approval_entries_preserved':len(approvals),'database_models':len(rows),'database_approvals':len(saved),'exact_model_review_approval_and_primary_source':True,'database_sha256':hashlib.sha256((a.site/'atlas.sqlite').read_bytes()).hexdigest()}
 assert len(previous)==47 and len(approvals)==24 and len(current)==47 and len(rows)==48 and len(saved)==25
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
